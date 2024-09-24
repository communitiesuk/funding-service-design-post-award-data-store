"""Provides a controller for spreadsheet ingestion."""

import json
import typing
import uuid
from datetime import datetime
from io import BytesIO
from json import JSONDecodeError
from typing import IO, Callable
from zipfile import BadZipFile

import pandas as pd
import pandera as pa
from flask import current_app, g
from sqlalchemy import exc
from werkzeug.datastructures import FileStorage

import data_store.table_extraction as ta
from config import Config
from data_store.aws import upload_file
from data_store.const import DATETIME_ISO_8601, EXCEL_MIMETYPE, FAILED_FILE_S3_NAME_FORMAT
from data_store.controllers.ingest_dependencies import (
    IngestDependencies,
    PFIngestDependencies,
    TFIngestDependencies,
    ingest_dependencies_factory,
)
from data_store.controllers.load_functions import (
    delete_existing_submission,
    get_or_generate_submission_id,
)
from data_store.controllers.mappings import INGEST_MAPPINGS, DataMapping
from data_store.db import db
from data_store.db.entities import Fund, Programme, ProgrammeJunction, Submission
from data_store.db.queries import (
    get_programme_by_id_and_previous_round,
    get_programme_by_id_and_round,
    get_reporting_round_id,
)
from data_store.db.utils import transaction_retry_wrapper
from data_store.exceptions import InitialValidationError, OldValidationError, ValidationError
from data_store.messaging import Message, MessengerBase
from data_store.messaging.messaging import failures_to_messages, group_validation_messages
from data_store.metrics import capture_ingest_metrics
from data_store.table_extraction.config.pf_r1_config import PF_TABLE_CONFIG
from data_store.typing import FundTablesExtractionConfig
from data_store.validation import tf_validate
from data_store.validation.initial_validation.initial_validate import initial_validate
from data_store.validation.pathfinders.schema_validation.exceptions import TableValidationErrors
from data_store.validation.pathfinders.schema_validation.validate import TableValidator
from data_store.validation.towns_fund.failures import ValidationFailureBase
from data_store.validation.towns_fund.failures.internal import InternalValidationFailure
from data_store.validation.towns_fund.failures.user import UserValidationFailure


def __get_organisation_name(fund: str, workbook_data: dict[str, pd.DataFrame]):
    """Helper function - really just for Sentry metrics - to retrieve the org name a submission is about."""
    try:
        match fund:
            case "Towns Fund":
                return workbook_data["2 - Project Admin"].iloc[8, 4]
            case "Pathfinders":
                return workbook_data["Admin"].iloc[14, 1]
            case _:
                current_app.logger.warning("Unhandled fund in `__get_organisation_name`")
    except KeyError:
        # Will throw a KeyError if the spreadsheet is invalid (eg for the wrong fund) - let's not hard fail on this.
        pass
    return "unknown"


@capture_ingest_metrics
def ingest(body: dict, excel_file: FileStorage) -> tuple[dict, int]:  # noqa: C901
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
    # FIXME: FPASF-249; remove this - temporary to remain compatible with existing error responses from connexion.
    for key in ["fund_name", "reporting_round"]:
        if key not in body:
            return (
                {
                    "detail": f"'{key}' is a required property",
                    "status": 400,
                    "title": "Bad Request",
                    "type": "about:blank",
                },
                400,
            )

    # FIXME: FPASF-249; remove this - temporary to remain compatible with existing error responses from connexion.
    try:
        fund, reporting_round, auth, do_load, submitting_account_id, submitting_user_email = parse_body(body)
    except ValueError:  # error parsing auth body
        return {
            "detail": "Invalid auth JSON",
            "status": 400,
        }, 400

    ingest_dependencies: IngestDependencies | None = ingest_dependencies_factory(fund, reporting_round)
    if ingest_dependencies is None:
        raise RuntimeError(f"Ingest is not supported for {fund} round {reporting_round}")

    try:
        workbook_data = extract_data(excel_file)
    except ValueError as e:
        # FIXME: FPASF-249; remove this - temporary to remain compatible with existing error responses from connexion.
        return {
            "detail": str(e),
            "status": 400,
            "title": "Bad Request",
            "type": "about:blank",
        }, 400

    # Set these values for reporting sentry metrics via `core.metrics:capture_ingest_metrics`
    g.organisation_name = __get_organisation_name(fund, workbook_data)

    try:
        initial_validate(workbook_data, ingest_dependencies.initial_validation_schema, auth)
        if fund == "Towns Fund":
            if not isinstance(ingest_dependencies, TFIngestDependencies):
                raise ValueError("Ingest dependencies should be of type TFIngestDependencies")
            transformed_data = ingest_dependencies.transform(workbook_data, reporting_round)
            tf_validate(
                transformed_data,
                workbook_data,
                ingest_dependencies.validation_schema,
                ingest_dependencies.fund_specific_validation,
            )
        else:
            if not isinstance(ingest_dependencies, PFIngestDependencies):
                raise ValueError("Ingest dependencies should be of type PFIngestDependencies")
            tables, p_error_messages = extract_process_validate_tables(
                workbook_data, ingest_dependencies.extract_process_validate_schema
            )
            ct_error_messages = ingest_dependencies.cross_table_validate(tables)
            error_messages = p_error_messages + ct_error_messages
            if error_messages:
                raise ValidationError(error_messages)
            coerce_data(tables, PF_TABLE_CONFIG)
            transformed_data = ingest_dependencies.transform(tables, reporting_round)
    except InitialValidationError as e:
        return build_validation_error_response(initial_validation_messages=e.error_messages)
    except OldValidationError as validation_error:
        return process_validation_failures(validation_error.validation_failures, ingest_dependencies.messenger)
    except ValidationError as validation_error:
        error_messages = group_validation_messages(validation_error.error_messages)
        return build_validation_error_response(validation_messages=error_messages)
    except Exception as uncaught_exception:
        failure_uuid = save_failed_submission(excel_file.stream)
        current_app.logger.exception(
            "Uncaught ingest exception: {exc_name}: {exc_message}, failure_id={failure_uuid}",
            extra=dict(
                exc_name=type(uncaught_exception).__name__,
                exc_message=str(uncaught_exception),
                failure_uuid=failure_uuid,
            ),
        )
        return build_internal_error_response(
            detail=f"Uncaught ingest exception: {type(uncaught_exception).__name__}: {str(uncaught_exception)}",
            failure_uuid=failure_uuid,
        )
    clean_data(transformed_data)
    if do_load:
        populate_db(
            round_number=reporting_round,
            transformed_data=transformed_data,
            mappings=INGEST_MAPPINGS,
            excel_file=excel_file,
            load_mapping=ingest_dependencies.table_to_load_function_mapping,
            submitting_account_id=submitting_account_id,
            submitting_user_email=submitting_user_email,
        )
    programme_metadata = get_metadata(transformed_data)
    return build_success_response(programme_metadata=programme_metadata, do_load=do_load)


def parse_body(body: dict) -> tuple[str, int, dict | None, bool, str | None, str | None]:
    """Parses the request body.

    :param body: request body
    :return: parsed values
    """
    fund = body["fund_name"]
    reporting_round = body["reporting_round"]
    auth = parse_auth(body)
    do_load: bool = body.get("do_load", True)  # defaults to True, if False then do not load to database
    submitting_account_id: str | None = body.get("submitting_account_id", None)
    submitting_user_email: str | None = body.get("submitting_user_email", None)

    # Set these values for reporting sentry metrics via `core.metrics:capture_ingest_metrics`
    g.fund_name = fund
    g.reporting_round = reporting_round

    return fund, reporting_round, auth, do_load, submitting_account_id, submitting_user_email


def extract_process_validate_tables(
    workbook_data: dict[str, pd.DataFrame], tables_config: FundTablesExtractionConfig
) -> tuple[dict[str, pd.DataFrame], list[Message]]:
    """Extracts, processes and validates tables from a workbook based on the specified configuration.

    If all tables pass validation, then the data is coerced to the dtypes defined in the schema.

    :param workbook_data: a dictionary containing worksheet names as keys and corresponding pandas DataFrames as values
    :param tables_config: a dictionary containing table names as keys and corresponding configuration dictionaries as
        values
    :return: a tuple containing a dictionary of tables and a list of error messages
    """
    extractor = ta.TableExtractor(workbook_data)
    tables = {}
    error_messages = []
    for table_name, config in tables_config.items():
        worksheet_name = config["extract"]["worksheet_name"]
        extracted_tables = extractor.extract(**config["extract"])
        processor = ta.TableProcessor(**config["process"])
        validator = TableValidator(config["validate"])
        # All PFV1 tables are singular, so we assume there is only one table. This may not be true for future templates.
        table = extracted_tables[0]
        processor.process(table)
        try:
            validator.validate(table)
        except TableValidationErrors as e:
            for error in e.validation_errors:
                error_messages.append(
                    Message(
                        sheet=worksheet_name,
                        section=table_name,
                        cell_indexes=(error.cell.str_ref,) if error.cell else None,
                        description=error.message,
                        error_type=None,
                    )
                )
                current_app.logger.info(
                    "{worksheet_name} {cell_ref}: {error_message}",
                    extra=dict(
                        worksheet_name=worksheet_name,
                        cell_ref=error.cell.str_ref if error.cell else "",
                        error_message=error.message,
                    ),
                )
        tables[table_name] = table.df
    return tables, error_messages


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
    initial_validation_messages: list[str] | None = None, validation_messages: list[Message] | None = None
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
            validation_errors=[error.to_dict() for error in validation_messages] if validation_messages else [],
        ),
        400,
    )


def build_internal_error_response(
    detail: str, failure_uuid: uuid.UUID, internal_errors: list[str] | None = None
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
        "Internal ingest exception - failure_id={failure_id} internal_failures: {internal_failures}",
        extra=dict(failure_id=failure_uuid, internal_failures=internal_failures),
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


def extract_data(excel_file: FileStorage) -> dict[str, pd.DataFrame]:
    """Extract data from an Excel file.

    :param excel_file: an in-memory Excel file
    :return: DataFrames representing Excel sheets
    """
    if excel_file.content_type != EXCEL_MIMETYPE:
        raise ValueError("Invalid file type")

    try:
        # TODO: Remove type.cast when we upgrade Pandas
        workbook = typing.cast(
            dict[str, pd.DataFrame],
            pd.read_excel(
                BytesIO(excel_file.stream.read()).getvalue(),
                sheet_name=None,  # extract from all sheets
                header=None,
                index_col=None,
                engine="openpyxl",
                na_values=[""],
                keep_default_na=False,
            ),
        )
    except (ValueError, BadZipFile) as bad_file_error:
        current_app.logger.error(
            "Cannot read the bad excel file: {bad_file_error}", extra=dict(bad_file_error=str(bad_file_error))
        )
        raise ValueError("bad excel_file") from bad_file_error

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
    *,
    round_number: int,
    transformed_data: dict[str, pd.DataFrame],
    mappings: tuple[DataMapping],
    excel_file: FileStorage,
    load_mapping: dict[str, Callable],
    submitting_account_id: str | None = None,
    submitting_user_email: str | None = None,
) -> None:
    """Populate the database with the data from the specified transformed_data using the provided data mappings.

    If the same submission for the same reporting_round exists, delete the submission and its children.
    If not, generate a new submission_id by auto-incrementing based on the last submission_id for that reporting_round.

    :param transformed_data: A dictionary containing data in the form of pandas dataframes.
    :param mappings: A tuple of DataMapping objects, which contain the necessary information for mapping the data from
                     the workbook to the database.
    :param excel_file: source spreadsheet containing the data.
    :param load_mapping: dictionary of tables and functions to load the tables into the DB.
    :param submitting_account_id: The account ID of the submitting user.
    :param submitting_user_email: The email address of the submitting user.
    :return: None
    """
    programme_id = transformed_data["Programme_Ref"]["Programme ID"].iloc[0]
    fund_code = transformed_data["Programme_Ref"]["FundType_ID"].iloc[0]
    programme_exists_previous_round = get_programme_by_id_and_previous_round(programme_id, round_number)
    programme_exists_same_round = get_programme_by_id_and_round(programme_id, round_number)

    submission_id, submission_to_del = get_or_generate_submission_id(
        programme_exists_same_round, round_number, fund_code
    )
    if submission_to_del:
        delete_existing_submission(submission_to_del)

    reporting_round_id = get_reporting_round_id(transformed_data["ReportingRound"], fund_code)

    for mapping in mappings:
        if load_function := load_mapping.get(mapping.table):
            additional_kwargs = dict(
                submission_id=submission_id,
                programme_exists_previous_round=programme_exists_previous_round,
                round_number=round_number,
                reporting_round_id=reporting_round_id,
            )  # some load functions also expect additional key word args
            load_function(transformed_data, mapping, **additional_kwargs)

    save_submission_file_name_and_user_metadata(excel_file, submission_id, submitting_account_id, submitting_user_email)
    save_submission_file_s3(excel_file, submission_id)

    db.session.commit()


def save_submission_file_name_and_user_metadata(
    excel_file: FileStorage,
    submission_id: str,
    submitting_account_id: str | None = None,
    submitting_user_email: str | None = None,
):
    """Saves the submission Excel filename, and submitting user metadata.

    :param excel_file: The Excel file to save.
    :param submission_id: The ID of the submission to be updated.
    :param submitting_account_id: The account ID of the submitting user.
    :param submitting_user_email: The email address of the submitting user.
    """
    submission = Submission.query.filter_by(submission_id=submission_id).first()
    submission.submission_filename = excel_file.filename
    submission.submitting_account_id = submitting_account_id
    submission.submitting_user_email = submitting_user_email
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
        .join(Fund)
        .filter(Submission.submission_id == submission_id)
        .with_entities(Submission.id, Fund.fund_code, Programme.programme_name)
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
            raise ValueError("Invalid auth JSON") from err
    return auth
