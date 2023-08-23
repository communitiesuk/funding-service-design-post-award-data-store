from core.validation.failures import ValidationFailure


class ValidationError(RuntimeError):
    """Validation error."""

    def __init__(self, validation_failures: list[ValidationFailure]):
        self.failure_messages = [str(error) for error in validation_failures]
        # TODO: uncomment once all failures have UC messages

        # self.failure_messages = serialise_user_centered_failures(validation_failures)


def validation_error_handler(error: ValidationError):
    return {
        "detail": "Workbook validation failed",
        "validation_errors": error.failure_messages,
        "status": 400,
        "title": "Bad Request",
    }, 400


class UnimplementedUCException(Exception):
    """Raised when a validation error occurs that is not supported as a user-centred error message."""


def unimplemented_uc_error_handler():
    return {
        "detail": "Uncaught workbook validation failure",
        "status": 500,
        "title": "Bad Request",
    }, 500
