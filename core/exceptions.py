class OldValidationError(RuntimeError):
    """Validation error raised by the old validation system used during TF ingestion."""

    def __init__(self, validation_failures):
        self.validation_failures = validation_failures


class InitialValidationError(RuntimeError):
    error_messages: list[str]

    def __init__(self, error_messages: list[str]):
        self.error_messages = error_messages
