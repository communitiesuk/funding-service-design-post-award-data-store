class ValidationError(RuntimeError):
    """Validation error."""

    def __init__(self, validation_failures):
        self.validation_failures = validation_failures
