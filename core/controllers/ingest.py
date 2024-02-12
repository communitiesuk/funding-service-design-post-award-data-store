"""Provides a controller for spreadsheet ingestion."""

import json
import uuid
from datetime import datetime
from io import BytesIO
from json import JSONDecodeError
from typing import BinaryIO
from zipfile import BadZipFile

import pandas as pd
from flask import abort, current_app, g
from sqlalchemy import exc
from werkzeug.datastructures import FileStorage

from config import Config
from core.aws import upload_file
from core.const import (
    DATETIME_ISO_8601,
    EXCEL_MIMETYPE,
    EXCLUDED_TABLES_BY_ROUND,
    FAILED_FILE_S3_NAME_FORMAT,
)
from core.controllers.ingest_dependencies import (
    IngestDependencies,
    ingest_dependencies_factory,
)
from core.controllers.load_functions import (
    delete_existing_submission,
    get_or_generate_submission_id,
    get_outcomes_outputs_to_insert,
    get_table_to_load_function_mapping,
)
from core.controllers.load_functions_historical import (
    get_programmes_newer_round,
    get_programmes_same_round_or_older,
)
from core.controllers.mappings import INGEST_MAPPINGS, DataMapping
from core.db import db
from core.db.entities import Organisation, Programme, Project, Submission
from core.db.queries import (
    get_programme_by_id_and_previous_round,
    get_programme_by_id_and_round,
)
from core.db.utils import transaction_retry_wrapper
from core.exceptions import InitialValidationError, ValidationError
from core.messaging import MessengerBase
from core.messaging.messaging import failures_to_messages
from core.validation import validate
from core.validation.failures import ValidationFailureBase
from core.validation.failures.internal import InternalValidationFailure
from core.validation.failures.user import UserValidationFailure
from core.validation.initial_validation.validate import initial_validate


def ingest(body: dict, excel_file: FileStorage) -> tuple[dict, int]:
    """Ingests a spreadsheet submission and stores its contents in a database.

    This function takes in an Excel file object and extracts data from the file, transforms it to fit the data model,
    casts it to the specified schema, and validates it. reporting round and fund are extracted from the request body
    and used to construct the dependencies to be injected for transformation and validation.

    If the data fails validation, a `ValidationError` is raised, which will result in a 400 error containing a set of
    validation messages that identify where in the spreadsheet is causing the validation failure.
    Otherwise, the data is cleaned and ingested into a database.

    :body: a dictionary of request body params
    :excel_file: the spreadsheet to ingest, from the request body
    :return: A JSON Response
    :raises ValidationError: raised if the data fails validation
    """
    g.excel_file = excel_file.stream
    fund = body.get("fund_name")
    reporting_round = body.get("reporting_round")
    auth = parse_auth(body)
    do_load = body.get("do_load", True)  # defaults to True, if False then do not load to database

    ingest_dependencies: IngestDependencies = ingest_dependencies_factory(fund, reporting_round)

    workbook_data = extract_data(excel_file)
    try:
        if iv_schema := ingest_dependencies.initial_validation_schema:
            initial_validate(workbook_data, iv_schema, auth)
        transformed_data = ingest_dependencies.transform_data(workbook_data)
        validate(
            transformed_data,
            workbook_data,
            ingest_dependencies.validation_schema,
            ingest_dependencies.fund_specific_validation,
        )
    except InitialValidationError as e:
        return process_initial_validation_errors(e.error_messages)
    except ValidationError as validation_error:
        return process_validation_failures(validation_error.validation_failures, ingest_dependencies.messenger)
    except Exception as uncaught_exception:
        return process_uncaught_exception(uncaught_exception)

    clean_data(transformed_data)

    if do_load:
        load_data(transformed_data, excel_file, reporting_round)

    success_payload = {
        "detail": f"Spreadsheet successfully validated{' and ingested' if do_load else ' but NOT ingested'}",
        "status": 200,
        "title": "success",
        "metadata": get_metadata(transformed_data, reporting_round),
        "loaded": do_load,
    }

    return success_payload, 200


def process_initial_validation_errors(error_messages: list[str]) -> tuple[dict, int]:
    return {
        "detail": "Workbook validation failed",
        "status": 400,
        "title": "Bad Request",
        "pre_transformation_errors": error_messages,
        "validation_errors": [],
    }, 400


def process_validation_failures(
    validation_failures: list[ValidationFailureBase],
    messenger: MessengerBase | None,
) -> tuple[dict, int]:
    """Processes a set of validation failures into the appropriate validation messages and constructs the response.

    This function takes in a list of validation failure objects, if any internal failures are present it returns a
    500 response. Otherwise, it then constructs the relevant error messages using the fund specific messenger class
    passed to this function. and constructs the appropriate response containing these messages.

    :param validation_failures: a list of validation failure objects generated during validation
    :param messenger: converts failures to user messages
    :return: A JSON Response
    """
    internal_failures = [failure for failure in validation_failures if isinstance(failure, InternalValidationFailure)]
    user_failures = [failure for failure in validation_failures if isinstance(failure, UserValidationFailure)]

    if internal_failures:
        return process_internal_failures(internal_failures)
    else:
        if not messenger:
            raise ValueError("Cannot process user failures without a Messenger")
        return process_user_failures(user_failures, messenger)


def process_internal_failures(internal_failures: list[InternalValidationFailure]) -> tuple[dict, int]:
    """Saves the failed submission, logs failures and returns them in a 500 response payload.

    :param internal_failures: failures produced by system error
    :return: a 500 response containing validation failures
    """
    failure_uuid = save_failed_submission(g.excel_file)
    current_app.logger.error(
        f"Internal ingest exception - failure_id={failure_uuid} internal_failures: {internal_failures}"
    )
    return {
        "detail": "Internal ingest exception.",
        "id": failure_uuid,
        "status": 500,
        "title": "Internal Server Error",
        "internal_errors": internal_failures,
    }, 500


def process_user_failures(user_failures: list[UserValidationFailure], messenger: MessengerBase) -> tuple[dict, int]:
    """Converts failures to messages and returns them in a 400 response.

    :param user_failures: failures produced by user error
    :param messenger: converts failures to user messages
    :return: a 400 response containing validation error messages
    """
    validation_messages = failures_to_messages(user_failures, messenger)
    return {
        "detail": "Workbook validation failed",
        "status": 400,
        "title": "Bad Request",
        "pre_transformation_errors": validation_messages.get("pre_transformation_errors", []),
        "validation_errors": validation_messages.get("validation_errors", []),
    }, 400


def process_uncaught_exception(uncaught_exception: Exception) -> tuple[dict, int]:
    """Saves the failed submission, logs the uncaught exception and returns them in a 500 response payload.

    :param uncaught_exception: the uncaught ingest exception
    :return: a 500 response containing the uncaught exception
    """
    failure_uuid = save_failed_submission(g.excel_file)
    current_app.logger.error(
        f"Uncaught ingest exception: {type(uncaught_exception).__name__}: {str(uncaught_exception)},"
        f" - failure_id={str(failure_uuid)}",
        exc_info=True,
    )
    return {
        "detail": f"Uncaught ingest exception: {type(uncaught_exception).__name__}: {str(uncaught_exception)}",
        "id": failure_uuid,
        "status": 500,
        "title": "Internal Server Error",
        "internal_errors": [],
    }, 500


def load_data(transformed_data: dict[str, pd.DataFrame], excel_file: FileStorage, reporting_round: int) -> None:
    """Loads a set of data, and it's source file into the database.

    :param workbook: transformed and validated data
    :param excel_file: source spreadsheet containing the data
    :param reporting_round: the reporting round
    :return: None
    """
    if reporting_round in [1, 2]:
        populate_db_historical_data(transformed_data, mappings=INGEST_MAPPINGS)

        # TODO: [FMD-227] Remove submission files from db
        submission_id = transformed_data["Submission_Ref"]["Submission ID"].iloc[0]
        save_submission_file_db(excel_file, submission_id)
        db.session.commit()
    else:
        populate_db(transformed_data, mappings=INGEST_MAPPINGS, excel_file=excel_file)


def extract_data(excel_file: FileStorage) -> dict[str, pd.DataFrame]:
    """Extract data from an Excel file.

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
    except (ValueError, BadZipFile) as bad_file_error:
        current_app.logger.error(f"Cannot read the bad excel file: {bad_file_error}")
        return abort(400, "bad excel_file")

    return workbook


def clean_data(transformed_data: dict[str, pd.DataFrame]) -> None:
    """Clean the transformed data by replacing all occurrences of `np.nan` with an empty string and `pd.NaT`
    with None.

    :param data: A dictionary where the keys are table names and the values are pd.DataFrames
    :return: None
    """
    for table in transformed_data.values():
        table.fillna("", inplace=True)
        # fillna with empty string does not work for datetime columns, so we need to replace NaT with None
        table.replace({pd.NaT: None}, inplace=True)


def get_metadata(transformed_data: dict[str, pd.DataFrame], reporting_round: int | None) -> dict:
    """Collect programme-level metadata on the submission.

    :param transformed_data: transformed data from the spreadsheet
    :param reporting_round: reporting round
    :return: metadata
    """
    return dict(transformed_data["Programme_Ref"].iloc[0]) if reporting_round not in (None, 1, 2) else {}


@transaction_retry_wrapper(max_retries=5, sleep_duration=0.6, error_type=exc.IntegrityError)
def populate_db(
    transformed_data: dict[str, pd.DataFrame], mappings: tuple[DataMapping], excel_file: FileStorage
) -> None:
    """Populate the database with the data from the specified transformed_data using the provided data mappings.

    If the same submission for the same reporting_round exists, delete the submission and its children.
    If not, generate a new submission_id by auto-incrementing based on the last submission_id for that reporting_round.

    :param transformed_data: A dictionary containing data in the form of pandas dataframes.
    :param mappings: A tuple of DataMapping objects, which contain the necessary information for mapping the data from
                     the workbook to the database.
    :param excel_file: source spreadsheet containing the data.
    :return: None
    """
    reporting_round = int(transformed_data["Submission_Ref"]["Reporting Round"].iloc[0])
    programme_id = transformed_data["Programme_Ref"]["Programme ID"].iloc[0]
    programme_exists_previous_round = get_programme_by_id_and_previous_round(programme_id, reporting_round)
    programme_exists_same_round = get_programme_by_id_and_round(programme_id, reporting_round)

    submission_id, submission_to_del = get_or_generate_submission_id(programme_exists_same_round, reporting_round)
    if submission_to_del:
        delete_existing_submission(submission_to_del)

    table_to_load_function_mapping = get_table_to_load_function_mapping()

    for mapping in mappings:
        load_function = table_to_load_function_mapping[mapping.table]
        additional_kwargs = dict(
            submission_id=submission_id, programme_exists_previous_round=programme_exists_previous_round
        )  # some load functions also expect additional key word args
        load_function(transformed_data, mapping, **additional_kwargs)

    save_submission_file_db(excel_file, submission_id)  # TODO: [FMD-227] Remove submission files from db
    save_submission_file_s3(excel_file, submission_id)

    db.session.commit()


def populate_db_historical_data(transformed_data: dict[str, pd.DataFrame], mappings: tuple[DataMapping]) -> None:
    """Populate the database with towns fund historical data from the transformed_data using provided data mappings.

    Historical data is batch data, and comprises multiple programmes.

    :param transformed_data: A dictionary containing data in the form of pandas dataframes.
    :param mappings: A tuple of DataMapping objects, which contain the necessary information for mapping the data from
                     the transformed_data to the database.
    :return: None
    """
    reporting_round = int(transformed_data["Submission_Ref"]["Reporting Round"].iloc[0])

    # tables excluded as not present in given round's data set
    excluded_tables = EXCLUDED_TABLES_BY_ROUND[reporting_round]

    programme_ids = transformed_data["Programme_Ref"]["Programme ID"]

    older_programmes = get_programmes_same_round_or_older(reporting_round, programme_ids)

    newer_programmes = get_programmes_newer_round(reporting_round, programme_ids)

    # delete all historical data for same round as given spreadsheet for ingestion sole source of truth
    Submission.query.filter(Submission.reporting_round == reporting_round).delete()
    db.session.flush()

    for mapping in mappings:
        if mapping.table in excluded_tables:
            continue
        table_data = transformed_data[mapping.table]
        models = mapping.map_data_to_models(table_data)

        if mapping.table == "Programme_Ref":
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

        if mapping.table == "Organisation_Ref":
            organisations = Organisation.query.all()
            existing_organisations = [org.organisation_name for org in organisations]
            for organisation in models:
                if organisation.organisation_name in existing_organisations:
                    continue
                else:
                    db.session.merge(organisation)
            continue

        # for outcome and output dim (ref) data, if record already exists, do nothing.
        if mapping.table in ["Outputs_Ref", "Outcome_Ref"]:
            models = get_outcomes_outputs_to_insert(mapping, models)

        db.session.add_all(models)

    db.session.commit()


# TODO: [FMD-227] Remove submission files from db
def save_submission_file_db(excel_file: FileStorage, submission_id: str):
    """Saves the submission Excel file.

    :param excel_file: The Excel file to save.
    :param submission_id: The ID of the submission to be updated.
    """
    submission = Submission.query.filter_by(submission_id=submission_id).first()
    submission.submission_filename = excel_file.filename
    excel_file.stream.seek(0)
    submission.submission_file = excel_file.stream.read()
    db.session.add(submission)


def save_submission_file_s3(excel_file: FileStorage, submission_id: str):
    """Saves the submission to S3 using fund_type and UUID as the key in the form fund_type/UUID
    eg. "TD/7931bfad-7430-4d1e-a1f1-fdc1a389d237"

    :param excel_file: The Excel file to save.
    :param submission_id: The ID of the submission to be updated.
    """
    uuid, fund_type, programme_name = (
        Programme.query.join(Project)
        .join(Submission)
        .filter(Submission.submission_id == submission_id)
        .with_entities(Submission.id, Programme.fund_type_id, Programme.programme_name)
        .distinct()
    ).one()

    upload_file(
        file=excel_file,
        bucket=Config.AWS_S3_BUCKET_SUCCESSFUL_FILES,
        object_name=f"{fund_type}/{str(uuid)}",
        metadata={
            "submission_id": submission_id,
            "filename": excel_file.filename,
            "programme_name": programme_name,
        },
    )


def save_failed_submission(file: BinaryIO):
    """Saves the failing file to S3 with a UUID

    :return: the UUID of the failed file
    """
    failure_uuid = uuid.uuid4()
    s3_object_name = FAILED_FILE_S3_NAME_FORMAT.format(failure_uuid, datetime.now().strftime(DATETIME_ISO_8601))
    upload_file(file=file, bucket=Config.AWS_S3_BUCKET_FAILED_FILES, object_name=s3_object_name)
    return failure_uuid


def parse_auth(body: dict) -> dict | None:
    """Parse the nested auth JSON details from the request body.

    A JSONDecodeError will be raised for a wrongly formatted string.
    A TypeError will be raised for a non-string type.

    :param body: request body dict
    :return: auth details
    """
    if auth := body.get("auth"):
        try:
            auth = json.loads(auth)
        except (JSONDecodeError, TypeError) as err:
            abort(400, "Invalid auth JSON", err)
    return auth
