from data_store.messaging import Message


class ValidationError(RuntimeError):
    error_messages: list[Message]

    def __init__(self, error_messages: list[Message]):
        self.error_messages = error_messages


class OldValidationError(RuntimeError):
    """Validation error raised by the old validation system used during TF ingestion."""

    def __init__(self, validation_failures):
        self.validation_failures = validation_failures


class InitialValidationError(RuntimeError):
    error_messages: list[str]

    def __init__(self, error_messages: list[str]):
        self.error_messages = error_messages


class MissingGeospatialException(Exception):
    def __init__(self, missing_postcode_prefixes: list[str]):
        self.description = f"Postcode prefixes not found in geospatial table: {', '.join(missing_postcode_prefixes)}"
        self.missing_postcode_prefixes = missing_postcode_prefixes
