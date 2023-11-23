import uuid
from datetime import datetime
from typing import BinaryIO

from flask import current_app, g, request
from werkzeug.exceptions import HTTPException

from config import Config
from core.aws import upload_file
from core.const import DATETIME_ISO_8601, FAILED_FILE_S3_NAME_FORMAT
from core.exceptions import ValidationError
from core.validation.failures.internal import InternalValidationFailure
from core.validation.failures.user import UserValidationFailure, failures_to_messages


def handle_validation_error(validation_error: ValidationError) -> Exception | tuple[dict, int]:
    """Handles a raised ValidationError.

    If internal failures, then saves the file to S3 and returns 500.

    Otherwise, converts user facing failures to message format and returns them in a 400.

    :param validation_error: A ValidationError containing ValidationFailures
    :return: A JSON response containing error messages used to fix the errors in the submitted document.
    """
    internal_failures = [
        failure for failure in validation_error.validation_failures if isinstance(failure, InternalValidationFailure)
    ]
    user_failures = [
        failure for failure in validation_error.validation_failures if isinstance(failure, UserValidationFailure)
    ]

    if internal_failures:
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

    try:
        validation_messages = failures_to_messages(user_failures)
    except Exception as exc:
        # ensures any Exceptions raised during message creation are handled in addition to the original ValidationError
        return handle_exception(exc)

    return {
        "detail": "Workbook validation failed",
        "status": 400,
        "title": "Bad Request",
        "pre_transformation_errors": validation_messages.get("pre_transformation_errors", []),
        "validation_errors": validation_messages.get("validation_errors", []),
    }, 400


def handle_exception(uncaught_exception: Exception) -> Exception | tuple[dict, int]:
    # pass through HTTP errors
    if isinstance(uncaught_exception, HTTPException):
        return uncaught_exception

    # handle uncaught ingest errors
    if request.path == "/ingest":
        failure_uuid = save_failed_submission(g.excel_file)
        current_app.logger.error(f"Uncaught ingest exception - failure_id={failure_uuid}", exc_info=True)
        return {
            "detail": "Uncaught ingest exception.",
            "id": failure_uuid,
            "status": 500,
            "title": "Internal Server Error",
            "internal_errors": None,
        }, 500

    return uncaught_exception


def save_failed_submission(file: BinaryIO):
    """Saves the failing file to S3 with a UUID

    :return: the UUID of the failed file
    """
    failure_uuid = uuid.uuid4()
    s3_object_name = FAILED_FILE_S3_NAME_FORMAT.format(failure_uuid, datetime.now().strftime(DATETIME_ISO_8601))
    upload_file(file=file, bucket=Config.AWS_S3_BUCKET_FAILED_FILES, object_name=s3_object_name)
    return failure_uuid
