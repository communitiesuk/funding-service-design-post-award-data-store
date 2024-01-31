class ValidationError(RuntimeError):
    """Validation error."""

    def __init__(self, validation_failures):
        self.validation_failures = validation_failures

class InitialValidationError(ValidationError):
    error_message: str

    def __init__(self, error_message: str):
        self.error_message = error_message
