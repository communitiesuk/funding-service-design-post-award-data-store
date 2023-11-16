import uuid
from datetime import datetime

from flask import Response, current_app, g, jsonify, request
from werkzeug.exceptions import HTTPException

from config import Config
from core.aws import upload_file
from core.const import DATETIME_ISO_8601, FAILED_FILE_S3_NAME_FORMAT
from core.exceptions import ValidationError
from core.validation.failures.user import failures_to_messages


def handle_validation_error(validation_error: ValidationError) -> Exception | tuple[dict, int]:
    """Handles raised ValidationErrors by converting the ValidationFailures to user facing components and adding these
        to the response payload.

    :param validation_error: A ValidationError containing ValidationFailures
    :return: A JSON response containing error messages used to fix the errors in the submitted document.
    """
    # ensures any Exceptions raised during message creation are handled in addition to the original ValidationError
    try:
        validation_messages = failures_to_messages(validation_error.validation_failures)
    except Exception as exc:
        return handle_exception(exc)
    return {
        "detail": "Workbook validation failed",
        "status": 400,
        "title": "Bad Request",
        "pre_transformation_errors": validation_messages.get("pre_transformation_errors", []),
        "validation_errors": validation_messages.get("validation_errors", []),
        "error_types": validation_messages.get("error_types", []),
    }, 400


def handle_exception(uncaught_exception: Exception) -> Exception | tuple[Response, int]:
    # pass through HTTP errors
    if isinstance(uncaught_exception, HTTPException):
        return uncaught_exception

    # handle uncaught ingest errors
    if request.path == "/ingest":
        failure_uuid = uuid.uuid4()
        s3_object_name = FAILED_FILE_S3_NAME_FORMAT.format(failure_uuid, datetime.now().strftime(DATETIME_ISO_8601))
        upload_file(file=g.excel_file, bucket=Config.AWS_S3_BUCKET_FAILED_FILES, object_name=s3_object_name)
        current_app.logger.error(f"Uncaught ingest exception - failure_id={str(failure_uuid)}", exc_info=True)
        return (
            jsonify(
                {
                    "detail": "Uncaught ingest exception.",
                    "id": failure_uuid,
                    "status": 500,
                    "title": "Internal Server Error",
                }
            ),
            500,
        )

    return uncaught_exception
