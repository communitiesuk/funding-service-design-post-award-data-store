"""Database loading functions.

This module contains methods used for loading data into the database,
as well as helper functions for loading.
"""

import pandas as pd

from data_store.const import SUBMISSION_ID_FORMAT
from data_store.controllers.mappings import DataMapping
from data_store.db import db
from data_store.db.entities import GeospatialDim, Organisation, Programme, ProgrammeJunction, Submission
from data_store.db.queries import (
    get_latest_submission_by_round_and_fund,
    get_organisation_exists,
)
from data_store.exceptions import MissingGeospatialException
from data_store.util import get_postcode_prefix_set


def load_programme_ref(
    transformed_data: dict[str, pd.DataFrame],
    mapping: DataMapping,
    programme_exists_previous_round: Programme,
    **kwargs,
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


def load_programme_junction(
    transformed_data: dict[str, pd.DataFrame],
    mapping: DataMapping,
    submission_id,
    round_number: int,
    reporting_round_id: str,
    **kwargs,
):
    """
    Load data into the programme junction table.

    ProgrammeJunction consists of three values: 'Programme ID', 'Submission ID', and 'Reporting Round'.
    As the first two are foreign keys the DataFrame is instantiated during load.

    :param transformed_data: a dictionary of DataFrames of table data to be inserted into the db.
    :param mapping: the mapping of the relevant DataFrame to its attributes as they appear in the db.
    :param submission_id: the ID of the submission associated with the data.
    :param round_number: the reporting round number.
    :param reporting_round_id: the ID of the reporting round associated with the data.
    """
    programme_id = transformed_data["Programme_Ref"]["Programme ID"].iloc[0]
    programme_junction_df = pd.DataFrame(
        {
            "Submission ID": [submission_id],
            "Programme ID": [programme_id],
            "Reporting Round": [round_number],
            "Reporting Round ID": [reporting_round_id],
        }
    )
    programme_junction = mapping.map_data_to_models(programme_junction_df)

    db.session.add(programme_junction[0])


def load_submission_ref(
    transformed_data: dict[str, pd.DataFrame],
    mapping: DataMapping,
    submission_id: str,
    reporting_round_id: str,
    **kwargs,
):
    """
    Load submission_dim table.
    """
    worksheet = transformed_data[mapping.table]
    worksheet["Submission ID"] = submission_id
    worksheet["Reporting Round ID"] = reporting_round_id
    models = mapping.map_data_to_models(worksheet)
    db.session.add_all(models)


def load_submission_level_data(
    transformed_data: dict[str, pd.DataFrame], mapping: DataMapping, submission_id: str, **kwargs
):
    """
    Load submission-level data.

    Adds 'Submission ID' to the transformed_data and map the data accordingly.
    When used for 'Project Details' mapping, calls another function to after creating the models to
    create the many-to-many relationship between projects and geospatial reference data.

    :param transformed_data: a dictionary of DataFrames of table data to be inserted into the db.
    :param mapping: the mapping of the relevant DataFrame to its attributes as they appear in the db.
    :param submission_id: string representation of id for submission.
    """
    worksheet = transformed_data[mapping.table]
    worksheet["Submission ID"] = submission_id
    models = mapping.map_data_to_models(worksheet)

    if mapping.table == "Project Details":
        add_project_geospatial_relationship(models)

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


def get_submission_by_programme_and_round(
    programme_id: str,
    round_number: int,
) -> Submission | None:
    return (
        Submission.query.join(ProgrammeJunction)
        .join(Programme)
        .filter(Programme.programme_id == programme_id)
        .filter(ProgrammeJunction.reporting_round == round_number)
        .first()
    )


def get_or_generate_submission_id(
    programme_exists_same_round: Programme | None, round_number: int, fund_code: str
) -> tuple[str, Submission | None]:
    """
    Retrieves or generates a submission ID based on the information in the provided transformed data.

    This function first checks if the programme_exists_same_round parameter is None or not.
    If a matching programme exists in the same reporting round, it calls the
    delete_existing_submission function to delete the existing submission and its children.
    The submission ID is then retrieved, and if there is no matching programme,
    a new submission ID is generated.

    :param programme_exists_same_round: programme if it exists in the same round.
    :param round_number: the reporting round number.
    :param fund_code: the two letter code representing the fund.
    :return: a string representing the submission ID, and the Submission to delete
    """
    if programme_exists_same_round:
        matching_programme_submission = get_submission_by_programme_and_round(
            programme_exists_same_round.programme_id, round_number
        )

        if matching_programme_submission:
            submission_id = matching_programme_submission.submission_id
            submission_to_del = matching_programme_submission.id
    else:
        submission_id = next_submission_id(round_number, fund_code)
        submission_to_del = None

    return submission_id, submission_to_del


def next_submission_id(round_number: int, fund_code: str) -> str:
    """Get the next submission ID by incrementing the last in the DB.

    Converts the reporting_round from numpy type to pythonic type.
    Then orders by a substring of the submission_id to get the latest submission.
    If there are no submissions for the reporting_round, assumes this is the 1st.

    :param round_number: the reporting round number.
    :param fund_code: the two-letter code representing the fund.

    :return: The next submission ID.
    """
    round_number = int(round_number)
    latest_submission = get_latest_submission_by_round_and_fund(round_number, fund_code)
    if not latest_submission:
        return SUBMISSION_ID_FORMAT[fund_code].format(round_number, 1)

    incremented_submission_num = latest_submission.submission_number + 1
    return SUBMISSION_ID_FORMAT[fund_code].format(round_number, incremented_submission_num)


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


def get_table_to_load_function_mapping(fund: str) -> dict:
    """Get the mapping of functions to the tables that use them to load data into the database.

    :param fund: string representation of the fund.
    :return: dictionary of table to load function for that table.
    """

    fund_to_table_mapping_dict = {
        "Towns Fund": {
            "Submission_Ref": load_submission_ref,
            "Organisation_Ref": load_organisation_ref,
            "Programme_Ref": load_programme_ref,
            "Programme Junction": load_programme_junction,
            "Programme Progress": load_submission_level_data,
            "Place Details": load_submission_level_data,
            "Funding Questions": load_submission_level_data,
            "Project Details": load_submission_level_data,
            "Project Progress": generic_load,
            "Funding": load_submission_level_data,
            "Funding Comments": generic_load,
            "Private Investments": generic_load,
            "Outputs_Ref": load_outputs_outcomes_ref,
            "Output_Data": load_submission_level_data,
            "Outcome_Ref": load_outputs_outcomes_ref,
            "Outcome_Data": load_submission_level_data,
            "RiskRegister": load_submission_level_data,
            "Programme Management": load_submission_level_data,
        },
        "Pathfinders": {
            "Submission_Ref": load_submission_ref,
            "Organisation_Ref": load_organisation_ref,
            "Programme_Ref": load_programme_ref,
            "Programme Junction": load_programme_junction,
            "Programme Progress": load_submission_level_data,
            "Place Details": load_submission_level_data,
            "Funding Questions": load_submission_level_data,
            "Project Details": load_submission_level_data,
            "Project Progress": generic_load,
            "Funding": load_submission_level_data,
            "Outputs_Ref": load_outputs_outcomes_ref,
            "Output_Data": load_submission_level_data,
            "Outcome_Ref": load_outputs_outcomes_ref,
            "Outcome_Data": load_submission_level_data,
            "RiskRegister": load_submission_level_data,
            "ProjectFinanceChange": load_submission_level_data,
        },
    }

    return fund_to_table_mapping_dict[fund]


def add_project_geospatial_relationship(project_models: list[db.Model]) -> list[db.Model]:
    """
    Creates the many-to-many relationship between each project and the geospatial_dim
    based on the project's postcodes by appending the relevant geospatial_dim entity
    to the project's 'geospatial' field.

    :param models: A list of instantiated Project model instances.
    :return: A list of instantiated Project model instances.
    """
    failing_postcode_prefixes = set()

    for row in project_models:
        if row.postcodes is None:
            continue

        postcodes_prefix_set = get_postcode_prefix_set(row.postcodes)
        filtered_geospatial_records = GeospatialDim.query.filter(
            GeospatialDim.postcode_prefix.in_(postcodes_prefix_set)
        ).all()
        row.geospatial_dims = [geo_row for geo_row in filtered_geospatial_records]

        failing_postcode_prefixes.update(
            postcodes_prefix_set - {associated_row.postcode_prefix for associated_row in row.geospatial_dims}
        )

    if failing_postcode_prefixes:
        sorted_failing_postcode_prefixes = sorted(list(failing_postcode_prefixes))
        raise MissingGeospatialException(sorted_failing_postcode_prefixes)

    return project_models
