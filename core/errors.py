from core.validation.failures import ValidationFailure, serialise_user_centered_failures


class ValidationError(RuntimeError):
    """Validation error."""

    def __init__(self, validation_failures: list[ValidationFailure]):
        self.failure_messages = serialise_user_centered_failures(validation_failures)


def validation_error_handler(error: ValidationError):
    return {
        "detail": "Workbook validation failed",
        "validation_errors": error.failure_messages,
        "status": 440,
        "title": "Bad Request",
    }, 440


class UnimplementedUCException(Exception):
    """Raised when a validation error occurs that is not supported as a user-centred error message."""


def unimplemented_uc_error_handler():
    return {
        "detail": "Uncaught workbook validation failure",
        "status": 500,
        "title": "Bad Request",
    }, 500
