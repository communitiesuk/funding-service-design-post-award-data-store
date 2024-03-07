"""Provides a controller for spreadsheet ingestion."""

import json
import uuid
from datetime import datetime
from io import BytesIO
from json import JSONDecodeError
from typing import IO, Callable
from zipfile import BadZipFile

import pandas as pd
import pandera as pa
from flask import abort, current_app, g
from sqlalchemy import exc
from werkzeug.datastructures import FileStorage

import tables as ta
from config import Config
from core.aws import upload_file
from core.const import DATETIME_ISO_8601, EXCEL_MIMETYPE, FAILED_FILE_S3_NAME_FORMAT
from core.controllers.ingest_dependencies import (
    IngestDependencies,
    ingest_dependencies_factory,
)
from core.controllers.load_functions import (
    delete_existing_submission,
    get_or_generate_submission_id,
)
from core.controllers.mappings import INGEST_MAPPINGS, DataMapping
from core.db import db
from core.db.entities import Programme, ProgrammeJunction, Submission
from core.db.queries import (
    get_programme_by_id_and_previous_round,
    get_programme_by_id_and_round,
)
from core.db.utils import transaction_retry_wrapper
from core.exceptions import InitialValidationError, OldValidationError, ValidationError
from core.messaging import Message, MessengerBase
from core.messaging.messaging import failures_to_messages, group_validation_messages
from core.table_configs.pathfinders.round_1 import PF_TABLE_CONFIG
from core.transformation.pathfinders.round_1.transform import pathfinders_transform
from core.validation import tf_validate
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
    fund, reporting_round, auth, do_load = parse_body(body)
    ingest_dependencies: IngestDependencies = ingest_dependencies_factory(fund, reporting_round)
    if ingest_dependencies is None:
        return abort(400, f"Ingest is not supported for {fund} round {reporting_round}")

    workbook_data = extract_data(excel_file)
    try:
        initial_validate(workbook_data, ingest_dependencies.initial_validation_schema, auth)
        if fund == "Towns Fund":
            # TODO https://dluhcdigital.atlassian.net/browse/SMD-660: use tables to extract, process and validate TF
            transformed_data = ingest_dependencies.transform_data(workbook_data)
            tf_validate(
                transformed_data,
                workbook_data,
                ingest_dependencies.validation_schema,
                ingest_dependencies.fund_specific_validation,
            )
        else:
            # TODO https://dluhcdigital.atlassian.net/browse/SMD-653: replace hardcoded dependencies with dependency
            #   injection
            tables = extract_process_validate_tables(workbook_data, PF_TABLE_CONFIG)  # noqa: F841
            # TODO https://dluhcdigital.atlassian.net/browse/SMD-533: do cross-table validation
            transformed_data = pathfinders_transform(tables, reporting_round)  # noqa: F841
    except InitialValidationError as e:
        return build_validation_error_response(initial_validation_messages=e.error_messages)
    except OldValidationError as validation_error:
        return process_validation_failures(validation_error.validation_failures, ingest_dependencies.messenger)
    except ValidationError as validation_error:
        error_messages = group_validation_messages(validation_error.error_messages)
        return build_validation_error_response(validation_messages=error_messages)
    except Exception as uncaught_exception:
        failure_uuid = save_failed_submission(excel_file.stream)
        current_app.logger.error(
            f"Uncaught ingest exception: {type(uncaught_exception).__name__}: {str(uncaught_exception)},"
            f" - failure_id={str(failure_uuid)}",
            exc_info=True,
        )
        return build_internal_error_response(
            detail=f"Uncaught ingest exception: {type(uncaught_exception).__name__}: {str(uncaught_exception)}",
            failure_uuid=failure_uuid,
        )
    clean_data(transformed_data)
    if do_load:
        load_data(transformed_data, excel_file, ingest_dependencies.table_to_load_function_mapping)
    programme_metadata = get_metadata(transformed_data)
    return build_success_response(programme_metadata=programme_metadata, do_load=do_load)


def parse_body(body: dict) -> tuple[str, int, dict | None, bool]:
    """Parses the request body.

    :param body: request body
    :return: parsed values
    """
    fund = body.get("fund_name")
    reporting_round = body.get("reporting_round")
    auth = parse_auth(body)
    do_load = body.get("do_load", True)  # defaults to True, if False then do not load to database
    return fund, reporting_round, auth, do_load


def extract_process_validate_tables(
    workbook_data: dict[str, pd.DataFrame], tables_config: dict[str, dict]
) -> dict[str, pd.DataFrame]:
    """Extracts, processes and validates tables from a workbook based on the specified configuration.

    If all tables pass validation, then the data is coerced to the dtypes defined in the schema.

    :param workbook_data: a dictionary containing worksheet names as keys and corresponding pandas DataFrames as values
    :param tables_config: a dictionary containing table names as keys and corresponding configuration dictionaries as
        values
    :return: a dictionary containing table names as keys and lists of extracted tables as pandas DataFrames as values
    :raises ValidationError: if the data fails validation
    """
    extractor = ta.TableExtractor(workbook_data)
    tables = {}
    error_messages = []
    for table_name, config in tables_config.items():
        worksheet_name = config["extract"]["worksheet_name"]
        extracted_tables = extractor.extract(**config["extract"])
        processor = ta.TableProcessor(**config["process"])
        validator = ta.TableValidator(config["validate"])
        # All PFV1 tables are singular, so we assume there is only one table. This may not be true for future templates.
        table = extracted_tables[0]
        processor.process(table)
        try:
            validator.validate(table)
        except ta.TableValidationErrors as e:
            for error in e.validation_errors:
                error_messages.append(
                    Message(
                        sheet=worksheet_name,
                        section=None,
                        cell_index=error.cell.str_ref if error.cell else None,
                        description=error.message,
                        error_type=None,
                    )
                )
                current_app.logger.info(
                    f"{config['extract']['worksheet_name']} {error.cell.str_ref if error.cell else ''}:"
                    f" {error.message}"
                )
        tables[table_name] = table.df
    if error_messages:
        raise ValidationError(error_messages)
    coerce_data(tables, tables_config)
    return tables


def coerce_data(tables: dict[str, pd.DataFrame], tables_config: dict) -> None:
    """Coerce the data to the specified schema.

    If the data has passed validation, this should not raise any exceptions.

    :param tables: a dictionary containing table names as keys and corresponding DataFrames as values
    :param tables_config: tables config
    :return: coerced data
    """
    for table_name, config in tables_config.items():
        tables[table_name] = pa.DataFrameSchema(**config["validate"], coerce=True).coerce_dtype(tables[table_name])


def build_validation_error_response(
    initial_validation_messages: list[str] = None, validation_messages: list[Message] = None
) -> tuple[dict, int]:
    """Builds a validation error response.

    :param initial_validation_messages: initial validation errors
    :param validation_messages: validation errors
    :return: the response payload
    """
    return (
        dict(
            detail="Workbook validation failed",
            status=400,
            title="Bad Request",
            pre_transformation_errors=initial_validation_messages or [],
            validation_errors=[vars(error) for error in validation_messages] if validation_messages else [],
        ),
        400,
    )


def build_internal_error_response(
    detail: str, failure_uuid: uuid.UUID, internal_errors: list[str] = None
) -> tuple[dict, int]:
    """Builds an internal error response.

    :param detail: detail message
    :param failure_uuid: UUID reference to the failure
    :param internal_errors:
    :return: the response payload
    """
    return (
        dict(
            detail=detail,
            status=500,
            title="Internal Server Error",
            id=str(failure_uuid),
            internal_errors=internal_errors or [],
        ),
        500,
    )


def build_success_response(programme_metadata: dict[str, pd.DataFrame], do_load: bool) -> tuple[dict, int]:
    """Builds a success response.

    :param programme_metadata: metadata about the program being ingested
    :param do_load: if the data was loaded to the db
    :return: the response payload
    """
    return (
        dict(
            detail=f"Spreadsheet successfully validated{' and ingested' if do_load else ' but NOT ingested'}",
            status=200,
            title="success",
            metadata=programme_metadata,
            loaded=do_load,
        ),
        200,
    )


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
    return build_internal_error_response(detail="Internal ingest exception.", failure_uuid=failure_uuid)


def process_user_failures(user_failures: list[UserValidationFailure], messenger: MessengerBase) -> tuple[dict, int]:
    """Converts failures to messages and returns them in a 400 response.

    :param user_failures: failures produced by user error
    :param messenger: converts failures to user messages
    :return: a 400 response containing validation error messages
    """
    validation_messages = failures_to_messages(user_failures, messenger)
    return build_validation_error_response(validation_messages=validation_messages)


def load_data(
    transformed_data: dict[str, pd.DataFrame], excel_file: FileStorage, load_mapping: dict[str, Callable]
) -> None:
    """Loads a set of data, and it's source file into the database.

    :param transformed_data: transformed and validated data
    :param excel_file: source spreadsheet containing the data
    :param load_mapping: dictionary of tables and functions to load the tables into the DB.
    :return: None
    """
    if "Programme Management" in transformed_data:  # Temporary fix for Programme Management data not being used
        del transformed_data["Programme Management"]
    populate_db(transformed_data, mappings=INGEST_MAPPINGS, excel_file=excel_file, load_mapping=load_mapping)


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
            header=None,
            index_col=None,
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


def get_metadata(transformed_data: dict[str, pd.DataFrame]) -> dict:
    """Collect programme-level metadata on the submission.

    :param transformed_data: transformed data from the spreadsheet
    :return: metadata
    """
    return dict(transformed_data["Programme_Ref"].iloc[0])


@transaction_retry_wrapper(max_retries=5, sleep_duration=0.6, error_type=exc.IntegrityError)
def populate_db(
    transformed_data: dict[str, pd.DataFrame],
    mappings: tuple[DataMapping],
    excel_file: FileStorage,
    load_mapping: dict[str, Callable],
) -> None:
    """Populate the database with the data from the specified transformed_data using the provided data mappings.

    If the same submission for the same reporting_round exists, delete the submission and its children.
    If not, generate a new submission_id by auto-incrementing based on the last submission_id for that reporting_round.

    :param transformed_data: A dictionary containing data in the form of pandas dataframes.
    :param mappings: A tuple of DataMapping objects, which contain the necessary information for mapping the data from
                     the workbook to the database.
    :param excel_file: source spreadsheet containing the data.#
    :param load_mapping: dictionary of tables and functions to load the tables into the DB.
    :return: None
    """
    reporting_round = int(transformed_data["Submission_Ref"]["Reporting Round"].iloc[0])
    programme_id = transformed_data["Programme_Ref"]["Programme ID"].iloc[0]
    programme_exists_previous_round = get_programme_by_id_and_previous_round(programme_id, reporting_round)
    programme_exists_same_round = get_programme_by_id_and_round(programme_id, reporting_round)

    submission_id, submission_to_del = get_or_generate_submission_id(programme_exists_same_round, reporting_round)
    if submission_to_del:
        delete_existing_submission(submission_to_del)

    for mapping in mappings:
        if load_function := load_mapping.get(mapping.table):
            additional_kwargs = dict(
                submission_id=submission_id, programme_exists_previous_round=programme_exists_previous_round
            )  # some load functions also expect additional key word args
            load_function(transformed_data, mapping, **additional_kwargs)

    save_submission_file_name(excel_file, submission_id)
    save_submission_file_s3(excel_file, submission_id)

    db.session.commit()


def save_submission_file_name(excel_file: FileStorage, submission_id: str):
    """Saves the submission Excel filename.

    :param excel_file: The Excel file to save.
    :param submission_id: The ID of the submission to be updated.
    """
    submission = Submission.query.filter_by(submission_id=submission_id).first()
    submission.submission_filename = excel_file.filename
    db.session.add(submission)


def save_submission_file_s3(excel_file: FileStorage, submission_id: str):
    """Saves the submission to S3 using fund_type and UUID as the key in the form fund_type/UUID
    eg. "TD/7931bfad-7430-4d1e-a1f1-fdc1a389d237"

    :param excel_file: The Excel file to save.
    :param submission_id: The ID of the submission to be updated.
    """
    uuid, fund_type, programme_name = (
        Programme.query.join(ProgrammeJunction)
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


def save_failed_submission(file: IO) -> uuid.UUID:
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
