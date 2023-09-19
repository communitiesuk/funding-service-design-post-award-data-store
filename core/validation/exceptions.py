"""Contains exceptions that can be raised during validation."""


class UnimplementedErrorMessageException(NotImplementedError):
    """Raised when a validation failure occurs that cannot be represented by an error message."""
