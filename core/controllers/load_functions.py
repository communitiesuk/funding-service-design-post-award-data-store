"""Database loading functions.

This module contains methods used for loading data into the database,
as well as helper functions for loading.
"""

import pandas as pd
from sqlalchemy import desc, func

from core.const import SUBMISSION_ID_FORMAT
from core.controllers.mappings import DataMapping
from core.db import db
from core.db.entities import BaseModel, Organisation, Programme, Submission


class DataLoader:
    submission_id: str
    data_to_update: dict[DataMapping, BaseModel]

    def __init__(self, submission_id: str, models_to_update: dict[DataMapping, BaseModel]):
        self.submission_id = submission_id
        self.data_to_update = models_to_update

    def load(self, transformed_data: dict[str, pd.DataFrame], mapping: DataMapping):
        models = self.get_models(mapping, transformed_data)
        if mapping.only_load_new:
            models = self.filter_to_new(mapping, models)
        if existing_data := self.data_to_update.get(mapping):
            self.update_existing_data(models, existing_data)
        else:
            db.session.add_all(models)

    def get_models(self, mapping: DataMapping, transformed_data: dict[str, pd.DataFrame]):
        data_to_map = transformed_data[mapping.table]
        if mapping.submission_level:
            data_to_map["Submission ID"] = self.submission_id
        models = mapping.map_data_to_models(data_to_map)
        return models

    @staticmethod
    def update_existing_data(models: list[BaseModel], existing_data: BaseModel):
        if not len(models) == 1:
            raise ValueError("Only one model should be loaded when updating existing data")
        model = models[0]
        model.id = existing_data.id
        db.session.merge(model)

    @staticmethod
    def filter_to_new(mapping: DataMapping, models: list[BaseModel]) -> list:
        """Filters models to ones not already present in the database.

        :param mapping: mapping of ingest to db
        :param models: list of incoming outcomes or outputs being ingested
        :return: list of outcomes or outcomes to be inserted
        """
        if not mapping.primary_key:
            raise ValueError("Mapping must have primary key set to filter to new")
        query_results = db.session.query(getattr(mapping.model, mapping.primary_key)).all()
        existing_names = [str(row[0]) for row in query_results]
        models = [model for model in models if getattr(model, mapping.primary_key) not in existing_names]
        return models


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
