"""Database loading functions.

This module contains methods used for loading data into the database,
as well as helper functions for loading.
"""

import pandas as pd
from sqlalchemy import desc, func

from core.const import SUBMISSION_ID_FORMAT
from core.controllers.mappings import DataMapping
from core.db import db
from core.db.entities import Organisation, Programme, Submission
from core.db.queries import get_organisation_exists


def load_programme_ref(
    transformed_data: dict[str, pd.DataFrame],
    mapping: DataMapping,
    programme_exists_previous_round: Programme,
    **kwargs
):
    """Loads data into the 'Programme_Ref' table.

    If the programme exists in a previous round, the incoming programme's information supersedes the existing programme.
    Data is added to the session via this method, but not committed.

    :param transformed_data: a dictionary of DataFrames of table data to be inserted into the db.
    :param mapping: the mapping of the relevant DataFrame to its attributes as they appear in the db.
    :param programme_exists_previous_round: programme if it exists in the same round or a previous one.
    """
    model_data = transformed_data[mapping.table]
    models = mapping.map_data_to_models(model_data)

    programme = models[0]

    if programme_exists_previous_round:
        programme_to_merge = programme
        programme_to_merge.id = programme_exists_previous_round.id
        db.session.merge(programme_to_merge)
    else:
        db.session.add(programme)


def load_organisation_ref(transformed_data: dict[str, pd.DataFrame], mapping: DataMapping, **kwargs):
    """
    Loads data into the 'Organisation_Ref' table.

    If the organisation already exists in the database, it merges to reuse the primary key.
    Data is added to the session via this method, but not committed.
    There can only be one Organisation per ingest.

    :param transformed_data: a dictionary of DataFrames of table data to be inserted into the db.
    :param mapping: the mapping of the relevant DataFrame to its attributes as they appear in the db.
    """
    model_data = transformed_data[mapping.table]
    models = mapping.map_data_to_models(model_data)

    organisation = models[0]

    organisation_exists = get_organisation_exists(organisation.organisation_name)
    if organisation_exists:
        org_to_merge = organisation
        org_to_merge.id = organisation_exists.id
        db.session.merge(org_to_merge)
    else:
        db.session.add(organisation)


def load_outputs_outcomes_ref(transformed_data: dict[str, pd.DataFrame], mapping: DataMapping, **kwargs):
    """
    Loads data into the 'Outputs_Ref' or 'Outcomes_Ref' tables.

    The function first retrieves the relevant data from the transformed data using the provided mapping.
    It then processes the data to get outcomes and outputs to insert,
    and finally adds all the models to the database session.

    :param transformed_data: a dictionary of DataFrames of table data to be inserted into the db.
    :param mapping: the mapping of the relevant DataFrame to its attributes as they appear in the db.
    """
    model_data = transformed_data[mapping.table]
    models = mapping.map_data_to_models(model_data)

    models = get_outcomes_outputs_to_insert(mapping, models)
    db.session.add_all(models)


def load_programme_junction(workbook: dict[str, pd.DataFrame], mapping: DataMapping, submission_id, **kwargs):
    """
    Load data into the programme junction table.

    ProgrammeJunction consists of two values: 'Programme ID' and 'Submission ID'.
    As these are both foreign keys the DataFrame is instantiated during load.

    :param workbook: a dictionary of DataFrames of table data to be inserted into the db.
    :param mapping: the mapping of the relevant DataFrame to its attributes as they appear in the db.
    :param submission_id: the ID of the submission associated with the data.
    """
    programme_id = workbook["Programme_Ref"]["Programme ID"].iloc[0]
    programme_junction_df = pd.DataFrame({"Submission ID": [submission_id], "Programme ID": [programme_id]})
    programme_junction = mapping.map_data_to_models(programme_junction_df)

    db.session.add(programme_junction[0])


def load_submission_level_data(workbook: dict[str, pd.DataFrame], mapping: DataMapping, submission_id: str, **kwargs):
    """
    Load submission-level data.

    Adds 'Submission ID' to the workbook and map the data accordingly.
    This column is retained for 'Submission_Ref', but is only used as a look-up for other tables.

    :param workbook: a dictionary of DataFrames of table data to be inserted into the db.
    :param mapping: the mapping of the relevant DataFrame to its attributes as they appear in the db.
    :param submission_id: string representation of id for submission.
    """
    worksheet = workbook[mapping.table]
    worksheet["Submission ID"] = submission_id
    models = mapping.map_data_to_models(worksheet)

    db.session.add_all(models)


def generic_load(transformed_data: dict[str, pd.DataFrame], mapping: DataMapping, **kwargs):
    """
    Function for loading data into the database that only requires mapping to adhere to the data model.

    :param transformed_data: a dictionary of DataFrames of table data to be inserted into the db.
    :param mapping: the mapping of the relevant DataFrame to its attributes as they appear in the db.
    """
    worksheet = transformed_data[mapping.table]
    models = mapping.map_data_to_models(worksheet)

    db.session.add_all(models)


def delete_existing_submission(submission_to_del: str) -> None:
    """
    Deletes the existing submission and all its children based on the UUID of that submission.

    :param submission_to_del: string of Submission's id to be deleted.
    :return: None
    """
    Submission.query.filter_by(id=submission_to_del).delete()
    db.session.flush()


def get_or_generate_submission_id(
    programme_exists_same_round: Programme, reporting_round: int
) -> tuple[str, Submission | None]:
    """
    Retrieves or generates a submission ID based on the information in the provided transformed data.

    This function first checks if the programme_exists_same_round parameter is None or not.
    If a matching programme exists in the same reporting round, it calls the
    delete_existing_submission function to delete the existing submission and its children.
    The submission ID is then retrieved, and if there is no matching programme,
    a new submission ID is generated.

    :param programme_exists_same_round: programme if it exists in the same round.
    :param reporting_round: integer representing the reporting round.
    :return: a string representing the submission ID, and the Submission to delete
    """
    if programme_exists_same_round:
        matching_programme_submission = next(
            (
                programme_submission
                for programme_submission in programme_exists_same_round.in_round_programmes
                if programme_submission.submission.reporting_round == reporting_round
            ),
            None,
        )
        submission_id = matching_programme_submission.submission.submission_id
        submission_to_del = matching_programme_submission.submission.id
    else:
        submission_id = next_submission_id(reporting_round)
        submission_to_del = None

    return submission_id, submission_to_del


def next_submission_id(reporting_round: int) -> str:
    """Get the next submission ID by incrementing the last in the DB.

    Converts the reporting_round from numpy type to pythonic type.
    Then orders by a substring of the submission_id to get the latest submission.
    If there are no submissions for the reporting_round, assumes this is the 1st.

    :return: The next submission ID.
    """
    reporting_round = int(reporting_round)
    latest_submission = (
        Submission.query.filter_by(reporting_round=reporting_round)
        .order_by(desc(func.cast(func.substr(Submission.submission_id, 7), db.Integer)))
        .first()
    )
    if not latest_submission:
        return SUBMISSION_ID_FORMAT.format(reporting_round, 1)

    incremented_submission_num = latest_submission.submission_number + 1
    return SUBMISSION_ID_FORMAT.format(reporting_round, incremented_submission_num)


def get_outcomes_outputs_to_insert(mapping: DataMapping, models: list) -> list:
    """Returns outcomes or outputs not present in the database.

    :param mapping: mapping of ingest to db
    :param models: list of incoming outcomes or outputs being ingested
    :return: list of outcomes or outcomes to be inserted
    """
    db_model_field = {"Outputs_Ref": "output_name", "Outcome_Ref": "outcome_name"}[mapping.table]

    query_results = db.session.query(getattr(mapping.model, db_model_field)).all()
    existing_names = [str(row[0]) for row in query_results]
    models = [model for model in models if getattr(model, db_model_field) not in existing_names]

    return models


def remove_unreferenced_organisations():
    """Removes organisations no longer referenced by a Programme.

    Some organisation names have been wrong in previous ingest.
    This will clean them up everytime a new ingest is run updating those names
    """

    organisations_without_child = Organisation.query.filter(~Organisation.programmes.any()).all()
    if organisations_without_child:
        for organisation in organisations_without_child:
            db.session.delete(organisation)

    db.session.commit()


def get_table_to_load_function_mapping() -> dict:
    """Get the mapping of functions to the tables that use them to load data into the database.

    Currently, Towns Fund is the only onboarded fund.
    This function can be extended for other funds after they have been onboarded.

    :return: dictionary of table to load function for that table.
    """

    tf_table_to_load_function_mapping = {
        "Submission_Ref": load_submission_level_data,
        "Organisation_Ref": load_organisation_ref,
        "Programme_Ref": load_programme_ref,
        "Programme Junction": load_programme_junction,
        "Programme Progress": load_submission_level_data,
        "Place Details": load_submission_level_data,
        "Funding Questions": load_submission_level_data,
        "Project Details": load_submission_level_data,
        "Project Progress": generic_load,
        "Funding": generic_load,
        "Funding Comments": generic_load,
        "Private Investments": generic_load,
        "Outputs_Ref": load_outputs_outcomes_ref,
        "Output_Data": generic_load,
        "Outcome_Ref": load_outputs_outcomes_ref,
        "Outcome_Data": load_submission_level_data,
        "RiskRegister": load_submission_level_data,
    }

    return tf_table_to_load_function_mapping
