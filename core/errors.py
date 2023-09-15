from http.client import HTTPException

from flask import current_app, request

from core.validation.failures import ValidationFailure, failures_to_messages


class ValidationError(RuntimeError):
    """Validation error."""

    def __init__(self, validation_failures: list[ValidationFailure]):
        self.failure_messages = failures_to_messages(validation_failures)


def handle_validation_error(error: ValidationError):
    return {
        "detail": "Workbook validation failed",
        "validation_errors": error.failure_messages,
        "status": 400,
        "title": "Bad Request",
    }, 400


def handle_exception(e: Exception):
    # pass through HTTP errors
    if isinstance(e, HTTPException):
        return e

    # handle uncaught ingest errors
    if request.path == "/ingest":
        # TODO: save file to S3
        current_app.logger.error("Uncaught ingest exception.", exc_info=True)
        return {
            "detail": "Uncaught ingest exception.",
            "status": 500,
            "title": "Internal Server Error",
        }, 500

    return e
