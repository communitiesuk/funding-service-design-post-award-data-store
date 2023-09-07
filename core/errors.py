from core.validation.failures import ValidationFailure, failures_to_messages


class ValidationError(RuntimeError):
    """Validation error."""

    def __init__(self, validation_failures: list[ValidationFailure]):
        self.failure_messages = failures_to_messages(validation_failures)


def validation_error_handler(error: ValidationError):
    return {
        "detail": "Workbook validation failed",
        "validation_errors": error.failure_messages,
        "status": 400,
        "title": "Bad Request",
    }, 400


def unimplemented_uc_error_handler():
    return {
        "detail": "Uncaught workbook validation failure",
        "status": 500,
        "title": "Bad Request",
    }, 500
