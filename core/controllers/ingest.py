"""Provides a controller for spreadsheet ingestion."""
from io import BytesIO

import numpy as np
import pandas as pd
from flask import abort, current_app, jsonify
from sqlalchemy import desc, func
from werkzeug.datastructures import FileStorage

# isort: off
from core.const import EXCEL_MIMETYPE, EXCLUDED_TABLES_BY_ROUND, SUBMISSION_ID_FORMAT
from core.controllers.mappings import INGEST_MAPPINGS, DataMapping
from core.db import db
from core.db.entities import Organisation, Programme, Project, Submission
from core.validation.initial_check import extract_submission_details, pre_transformation_check
from core.validation.validate import validate
from core.errors import ValidationError
from core.extraction.towns_fund import ingest_towns_fund_data
from core.extraction.towns_fund_round_one import ingest_round_one_data_towns_fund
from core.extraction.towns_fund_round_two import ingest_round_two_data_towns_fund
from core.validation.casting import cast_to_schema
from core.validation.specific_validations import towns_fund_round_four as tf_round_4


REPORTING_ROUND = {
    "tf_round_three": 3,
    "tf_round_four": 4,
}

ETL_PIPELINES = {
    "tf_round_one": ingest_round_one_data_towns_fund,
    "tf_round_two": ingest_round_two_data_towns_fund,
    "tf_round_three": ingest_towns_fund_data,
    "tf_round_four": ingest_towns_fund_data,
}


def ingest(body, excel_file):
    """Ingests a spreadsheet submission and stores its contents in a database.

    This function takes in an Excel file object and extracts data from the file, casts it to the
    specified schema, and validates it.
    If source_type is specified, the data will be put through an etl pipeline, prior
    to validation.
    If the data fails validation, a `ValidationError` is raised. Otherwise, the data is cleaned and ingested into a
    database.

    :body: contains the request body params
    :excel_file: the Excel file to ingest, from the request body
    :return: A tuple containing a string message and an integer HTTP status code.
    :raises ValidationError: If the data fails validation against the specified schema.
    """
    source_type = body.get("source_type")  # required
    workbook = extract_data(excel_file=excel_file)
    reporting_round = REPORTING_ROUND.get(source_type)

    if source_type:
        if reporting_round:
            pre_transformation_details = extract_submission_details(workbook=workbook, reporting_round=reporting_round)
            file_validation_failures = pre_transformation_check(pre_transformation_details)
            if file_validation_failures:
                raise ValidationError(validation_failures=file_validation_failures)
        etl_pipeline = ETL_PIPELINES[source_type]
        workbook = etl_pipeline(workbook)

    schema = get_schema(source_type)
    cast_to_schema(workbook, schema)
    validation_failures = validate(workbook, schema)

    if reporting_round == 4:
        round_4_failures = tf_round_4.validate(workbook, excel_file)
        validation_failures = [*validation_failures, *round_4_failures]

    if validation_failures:
        raise ValidationError(validation_failures=validation_failures)

    clean_data(workbook)
    if source_type in ["tf_round_one", "tf_round_two"]:
        populate_db_historical_data(workbook, INGEST_MAPPINGS)
    else:
        populate_db(workbook, INGEST_MAPPINGS)

    # provisionally removing unreferenced entities caused by updates to ingest process
    # TODO: DELETE THIS WHEN R1 AND R3 RE-INGESTED, OR NO MORE DUPLICATE ORGS
    if source_type in ["tf_round_one", "tf_round_three"]:
        remove_unreferenced_organisations()

    submission_id = workbook["Submission_Ref"]["Submission ID"].iloc[0]

    save_submission_file(excel_file, submission_id)

    return jsonify(
        {
            "detail": "Spreadsheet successfully uploaded",
            "status": 200,
            "title": "success",
        }
    )


def extract_data(excel_file: FileStorage) -> dict[str, pd.DataFrame]:
    """Extract data from an excel_file.

    :param excel_file: an in-memory Excel file
    :return: DataFrames representing Excel sheets
    """
    if excel_file.content_type != EXCEL_MIMETYPE:
        return abort(400, "Invalid file type")

    try:
        workbook = pd.read_excel(
            BytesIO(excel_file.stream.read()).getvalue(),
            sheet_name=None,  # extract from all sheets
            engine="openpyxl",
        )
        excel_file.seek(0)
    except ValueError as ingest_err:
        if "Worksheet" in ingest_err.args[0]:
            return abort(400, "Invalid array of sheet names")
        return abort(500, "Internal Ingestion Error")

    return workbook


def clean_data(workbook: dict[str, pd.DataFrame]) -> None:
    """Clean the data in the given workbook by replacing all occurrences of `np.NA` with an empty string and `np.nan`
    with None.

    :param workbook: A dictionary where the keys are worksheet names and the values are Pandas dataframes representing
                     the contents of those worksheets.
    :return: None
    """
    for worksheet in workbook.values():
        worksheet.fillna("", inplace=True)  # broad replace of np.NA with empty string
        worksheet.replace({np.nan: None}, inplace=True)  # replaces np.NAT with None


def next_submission_id(reporting_round: int) -> str:
    """Get the next submission ID by incrementing the last in the DB.

    :return: The next submission ID.
    """
    # Conversion to cast numpy int types from pandas data extract
    reporting_round = int(reporting_round)
    latest_submission = (
        Submission.query.filter_by(reporting_round=reporting_round)
        # substring submission number digits, cast to int and order to get the latest submission
        .order_by(desc(func.cast(func.substr(Submission.submission_id, 7), db.Integer))).first()
    )
    if not latest_submission:
        return SUBMISSION_ID_FORMAT.format(reporting_round, 1)  # the first submission

    incremented_submission_num = latest_submission.submission_number + 1
    return SUBMISSION_ID_FORMAT.format(reporting_round, incremented_submission_num)


def populate_db(workbook: dict[str, pd.DataFrame], mappings: tuple[DataMapping]) -> None:
    """Populate the database with the data from the specified workbook using the provided data mappings.

    :param workbook: A dictionary containing data in the form of pandas dataframes.
    :param mappings: A tuple of DataMapping objects, which contain the necessary information for mapping the data from
                     the workbook to the database.
    :return: None
    """
    # TODO: We do not have an updated "Round 4" spreadsheet yet so all concept of Round 4 is purely for validation only.
    #  Once we have an updated Round 4 spreadsheet we need to create a new transformation pipeline based off of Round 3.
    #  "Round 4" will ingest as if it were Round 3 - replacing that programme in the database.

    reporting_round = int(workbook["Submission_Ref"]["Reporting Round"].iloc[0])
    programme_id = workbook["Programme_Ref"]["Programme ID"].iloc[0]

    # if already added this round, this entity used to drop existing round data
    programme_exists_same_round = (
        Programme.query.join(Project)
        .join(Submission)
        .filter(Programme.programme_id == programme_id)
        .filter(Submission.reporting_round == reporting_round)
        .first()
    )
    # if added before or during this round, get the programme entity to merge (update)
    programme_exists_previous_round = (
        Programme.query.join(Project)
        .join(Submission)
        .filter(Programme.programme_id == programme_id)
        .filter(Submission.reporting_round <= reporting_round)
        .first()
    )

    if programme_exists_same_round:
        matching_project = None
        for project in programme_exists_same_round.projects:
            if project.submission.reporting_round == reporting_round:
                matching_project = project
                break
        if matching_project:
            # get id of submission to replace and re-use it
            submission_id = matching_project.submission.submission_id
            # submission instance to remove
            submission_to_del = matching_project.submission
            # drop submission, all children should be dropped via cascade
            Submission.query.filter_by(id=submission_to_del.id).delete()
            db.session.flush()

    else:
        submission_id = next_submission_id(reporting_round)

    for mapping in mappings:
        worksheet = workbook[mapping.worksheet_name]
        if "Submission ID" in mapping.columns:
            worksheet["Submission ID"] = submission_id
        models = mapping.map_worksheet_to_models(worksheet)

        if mapping.worksheet_name == "Programme_Ref" and programme_exists_previous_round:
            # Set incoming model pk to match existing DB row pk (this record will then be updated).
            programme_to_merge = models[0]
            programme_to_merge.id = programme_exists_previous_round.id
            db.session.merge(programme_to_merge)  # There can only be 1 programme per ingest.
            continue

        if mapping.worksheet_name == "Organisation_Ref":
            organisation_exists = Organisation.query.filter(
                Organisation.organisation_name == models[0].organisation_name
            ).first()
            # If this org already in DB, merge to re-use pk, otherwise use add_all as per loop continuation
            if organisation_exists:
                org_to_merge = models[0]
                org_to_merge.id = organisation_exists.id
                db.session.merge(org_to_merge)  # There can only be 1 org per ingest.
                continue

        # for outcome and output dim (ref) data, if record already exists, do nothing.
        if mapping.worksheet_name in ["Outputs_Ref", "Outcome_Ref"]:
            models = get_outcomes_outputs_to_insert(mapping, models)

        db.session.add_all(models)

    db.session.commit()


def populate_db_historical_data(workbook: dict[str, pd.DataFrame], mappings: tuple[DataMapping]) -> None:
    """Populate the database with towns fund historical data from the workbook using provided data mappings.

    Historical data is batch data, and comprises multiple programmes.

    :param workbook: A dictionary containing data in the form of pandas dataframes.
    :param mappings: A tuple of DataMapping objects, which contain the necessary information for mapping the data from
                     the workbook to the database.
    :return: None
    """
    reporting_round = int(workbook["Submission_Ref"]["Reporting Round"].iloc[0])

    # tables excluded as not present in given round's data set
    excluded_tables = EXCLUDED_TABLES_BY_ROUND[reporting_round]

    programme_ids = workbook["Programme_Ref"]["Programme ID"]

    older_programmes = get_programmes_same_round_or_older(reporting_round, programme_ids)

    newer_programmes = get_programmes_newer_round(reporting_round, programme_ids)

    # delete all historical data for same round as given spreadsheet for ingestion sole source of truth
    Submission.query.filter(Submission.reporting_round == reporting_round).delete()
    db.session.flush()

    for mapping in mappings:
        if mapping.worksheet_name in excluded_tables:
            continue
        worksheet = workbook[mapping.worksheet_name]
        models = mapping.map_worksheet_to_models(worksheet)

        if mapping.worksheet_name == "Programme_Ref":
            # historical rounds have multiple programmes so iterate through all of them
            for programme in models:
                # if exists beyond current round, do nothing
                if programme.programme_id in newer_programmes:
                    continue
                # if only exists in same round or older, update
                if programme.programme_id in older_programmes:
                    programme.id = older_programmes[programme.programme_id]
                # upsert programme
                db.session.merge(programme)
            continue

        if mapping.worksheet_name == "Organisation_Ref":
            organisations = Organisation.query.all()
            existing_organisations = [org.organisation_name for org in organisations]
            for organisation in models:
                if organisation.organisation_name in existing_organisations:
                    continue
                else:
                    db.session.merge(organisation)
            continue

        # for outcome and output dim (ref) data, if record already exists, do nothing.
        if mapping.worksheet_name in ["Outputs_Ref", "Outcome_Ref"]:
            models = get_outcomes_outputs_to_insert(mapping, models)

        db.session.add_all(models)

    db.session.commit()


def save_submission_file(excel_file, submission_id):
    """Saves the submission Excel file.

    TODO: Store files in an S3 bucket, rather than the database.

    :param excel_file: The Excel file to save.
    :param submission_id: The ID of the submission to be updated.
    """
    # TODO: if updating (rather than new), check it upserts (deletes old file)
    submission = Submission.query.filter_by(submission_id=submission_id).first()
    submission.submission_filename = excel_file.filename
    excel_file.stream.seek(0)
    submission.submission_file = excel_file.stream.read()
    db.session.add(submission)
    db.session.commit()


def get_programmes_same_round_or_older(reporting_round: int, programme_ids: list[str]) -> dict[str, str]:
    """Return ids of programmes updated in any round up to and including the specified round.

    :param reporting_round: The round currently being ingested.
    :param programme_ids: The programme ids of the data being ingested.
    :return: list of programme ids
    """
    existing_programmes = (
        Programme.query.join(Project)
        .join(Submission)
        .filter(Programme.programme_id.in_(programme_ids))
        .filter(Submission.reporting_round <= reporting_round)
        .all()
    )

    existing_programme_ids = {programme.programme_id: programme.id for programme in existing_programmes}

    return existing_programme_ids


def get_programmes_newer_round(reporting_round: int, programme_ids: list[str]) -> list[str]:
    """Return ids of programmes updated in any round after the specified round.

    :param reporting_round: The round currently being ingested.
    :param programme_ids: The programme ids of the data being ingested.
    :return: list of programme ids
    """
    programmes_newer_round = (
        Programme.query.join(Project)
        .join(Submission)
        .filter(Programme.programme_id.in_(programme_ids))
        .filter(Submission.reporting_round >= reporting_round)
        .with_entities(Programme.programme_id)
        .all()
    )

    programme_ids_newer_round = [programme.programme_id for programme in programmes_newer_round]

    return programme_ids_newer_round


def get_schema(reporting_round: str) -> dict[str, object]:
    """Returns validation schema corresponding to reporting round.

    :param reporting_round: the round being ingested
    :return:
    """
    schema_dict = {
        "tf_round_one": current_app.config["ROUND_ONE_TF_VALIDATION_SCHEMA"],
        "tf_round_two": current_app.config["ROUND_TWO_TF_VALIDATION_SCHEMA"],
        "tf_round_four": current_app.config["ROUND_FOUR_TF_VALIDATION_SCHEMA"],
    }

    return schema_dict.get(reporting_round, current_app.config["ROUND_THREE_TF_VALIDATION_SCHEMA"])


def get_outcomes_outputs_to_insert(mapping: DataMapping, models: list) -> list:
    """Returns outcomes or outputs not present in the database.

    :param mapping: mapping of ingest to db
    :param models: list of incoming outcomes or outputs being ingested
    :return: list of outcomes or outcomes to be inserted
    """
    db_model_field = {"Outputs_Ref": "output_name", "Outcome_Ref": "outcome_name"}[mapping.worksheet_name]

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
