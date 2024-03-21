from core.messaging import Message


class ValidationError(RuntimeError):
    error_messages: list[Message]

    def __init__(self, error_messages: list[Message]):
        self.error_messages = error_messages


# TODO make this extend validation error
class TamperedFileError(RuntimeError):
    """Raised when a file has been tampered with."""

    def __init__(self, error_messages: list[Message]):
        self.error_message = error_messages


class OldValidationError(RuntimeError):
    """Validation error raised by the old validation system used during TF ingestion."""

    def __init__(self, validation_failures):
        self.validation_failures = validation_failures


class InitialValidationError(RuntimeError):
    error_messages: list[str]

    def __init__(self, error_messages: list[str]):
        self.error_messages = error_messages
