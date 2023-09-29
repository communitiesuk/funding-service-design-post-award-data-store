from flask import current_app, request
from werkzeug.exceptions import HTTPException

from core.exceptions import ValidationError
from core.validation.failures import failures_to_messages


def handle_validation_error(validation_error: ValidationError):
    validation_messages = failures_to_messages(validation_error.validation_failures)
    return {
        "detail": "Workbook validation failed",
        "validation_errors": validation_messages,
        "status": 400,
        "title": "Bad Request",
    }, 400


def handle_exception(uncaught_exception: Exception):
    # pass through HTTP errors
    if isinstance(uncaught_exception, HTTPException):
        return uncaught_exception

    # handle uncaught ingest errors
    if request.path == "/ingest":
        # TODO: save file to S3
        current_app.logger.error("Uncaught ingest exception.", exc_info=True)
        return {
            "detail": "Uncaught ingest exception.",
            "status": 500,
            "title": "Internal Server Error",
        }, 500

    return uncaught_exception
