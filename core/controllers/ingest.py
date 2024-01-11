"""Provides a controller for spreadsheet ingestion."""

import json
from io import BytesIO
from json import JSONDecodeError
from zipfile import BadZipFile

import numpy as np
import pandas as pd
from flask import abort, current_app, g
from sqlalchemy import exc
from werkzeug.datastructures import FileStorage

from core.const import EXCEL_MIMETYPE, EXCLUDED_TABLES_BY_ROUND
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
from core.db.entities import Organisation, Submission
from core.db.queries import (
    get_programme_by_id_and_previous_round,
    get_programme_by_id_and_round,
)
from core.db.utils import transaction_retry_wrapper
from core.exceptions import ValidationError
from core.handlers import save_failed_submission
from core.messaging import MessengerBase
from core.messaging.messaging import failures_to_messages
from core.validation import validate
from core.validation.failures import ValidationFailureBase
from core.validation.failures.internal import InternalValidationFailure
from core.validation.failures.user import UserValidationFailure
from core.validation.pre_transformation_validate import pre_transformation_validations


def ingest(body: dict, excel_file: FileStorage) -> tuple[dict, int]:
    """Ingests a spreadsheet submission and stores its contents in a database.

    This function takes in an Excel file object and extracts data from the file, transforms it to fit the data model,
    casts it to the specified schema, and validates it.
    If reporting round is specified, the spreadsheet will be transformed using round specific implementations, prior to
     validation.

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

    original_workbook = extract_data(excel_file=excel_file)
    try:
        if ptv_schema := ingest_dependencies.pre_transformation_validation_schema:
            pre_transformation_validations(original_workbook, ptv_schema, auth)
        data_dict = ingest_dependencies.transform_data(original_workbook)
        validate(
            data_dict,
            original_workbook,
            ingest_dependencies.validation_schema,
            ingest_dependencies.fund_specific_validation,
        )

    except ValidationError as validation_error:
        return process_validation_failures(validation_error.validation_failures, ingest_dependencies.messenger)

    clean_data(data_dict)

    if do_load:
        load_data(data_dict, excel_file, reporting_round)

    success_payload = {
        "detail": f"Spreadsheet successfully validated{' and ingested' if do_load else ' but NOT ingested'}",
        "status": 200,
        "title": "success",
        "metadata": get_metadata(data_dict, reporting_round),
        "loaded": do_load,
    }

    return success_payload, 200


def process_validation_failures(
    validation_failures: list[ValidationFailureBase],
    messenger: MessengerBase | None,
) -> tuple[dict, int]:
    """Processes a set of validation failures into the appropriate validation messages and constructs the response.

    This function takes in a list of validation failure objects, if any internal failures are present it returns a
    500 response. Otherwise, it then constructs the relevant error messages using a fund specific messenger class
    instantiated from the messaging class factory. and constructs the appropriate response containing these messages.

    :param validation_failures: a list of validation failure objects generated during validation
    :param messenger: converts failures to user messages
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


def load_data(workbook: dict[str, pd.DataFrame], excel_file: FileStorage, reporting_round: int) -> None:
    """Loads a set of data, and it's source file into the database.

    :param workbook: transformed and validated data
    :param excel_file: source spreadsheet containing the data
    :param reporting_round: the reporting round
    :return: None
    """
    if reporting_round in [1, 2]:
        populate_db_historical_data(workbook, INGEST_MAPPINGS)
    else:
        populate_db(workbook=workbook, mappings=INGEST_MAPPINGS)
    submission_id = workbook["Submission_Ref"]["Submission ID"].iloc[0]
    save_submission_file(excel_file, submission_id)


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
    except (ValueError, BadZipFile) as bad_file_error:
        current_app.logger.error(f"Cannot read the bad excel file: {bad_file_error}")
        return abort(400, "bad excel_file")

    return workbook


def clean_data(data: dict[str, pd.DataFrame]) -> None:
    """Clean the data in the given workbook by replacing all occurrences of `np.NA` with an empty string and `np.nan`
    with None.

    :param data: A dictionary where the keys are table names and the values are pd.DataFrames
    :return: None
    """
    for table in data.values():
        table.fillna("", inplace=True)  # broad replace of np.NA with empty string
        table.replace({np.nan: None}, inplace=True)  # replaces np.NAT with None


def get_metadata(workbook: dict[str, pd.DataFrame], reporting_round: int | None) -> dict:
    """Collect programme-level metadata on the submission.

    :param workbook: ingested workbook
    :param reporting_round: reporting round
    :return: metadata
    """
    if reporting_round in (None, 1, 2):
        # no meta data for historical rounds
        return {}
    metadata = dict(workbook["Programme_Ref"].iloc[0])
    return metadata


@transaction_retry_wrapper(max_retries=5, sleep_duration=0.6, error_type=exc.IntegrityError)
def populate_db(workbook: dict[str, pd.DataFrame], mappings: tuple[DataMapping]) -> None:
    """Populate the database with the data from the specified workbook using the provided data mappings.

    If the same submission for the same reporting_round exists, delete the submission and its children.
    If not, generate a new submission_id by auto-incrementing based on the last submission_id for that reporting_round.

    :param workbook: A dictionary containing data in the form of pandas dataframes.
    :param mappings: A tuple of DataMapping objects, which contain the necessary information for mapping the data from
                     the workbook to the database.
    :return: None
    """
    reporting_round = int(workbook["Submission_Ref"]["Reporting Round"].iloc[0])
    programme_id = workbook["Programme_Ref"]["Programme ID"].iloc[0]
    programme_exists_previous_round = get_programme_by_id_and_previous_round(programme_id, reporting_round)
    programme_exists_same_round = get_programme_by_id_and_round(programme_id, reporting_round)

    submission_id, submission_to_del = get_or_generate_submission_id(programme_exists_same_round, reporting_round)
    if submission_to_del:
        delete_existing_submission(submission_to_del)

    table_to_load_function_mapping = get_table_to_load_function_mapping()

    for mapping in mappings:
        load_function = table_to_load_function_mapping[mapping.table]
        if load_function.__name__ == "generic_load":
            load_function(workbook, mapping, submission_id)
        elif load_function.__name__ == "load_programme_ref":
            load_function(workbook, mapping, programme_exists_previous_round)
        else:
            load_function(workbook, mapping)

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
        if mapping.table in excluded_tables:
            continue
        worksheet = workbook[mapping.table]
        models = mapping.map_data_to_models(worksheet)

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
