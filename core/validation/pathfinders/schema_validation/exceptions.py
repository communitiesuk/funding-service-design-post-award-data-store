from core.table_extraction.table import Cell


class TableValidationError:
    """Validation error with reference to an Excel cell."""

    message: str
    cell: Cell | None

    def __init__(self, message: str, cell: Cell | None):
        self.message = message
        self.cell = cell


class TableValidationErrors(Exception):
    validation_errors: list[TableValidationError]

    def __init__(self, validation_errors: list[TableValidationError]):
        self.validation_errors = validation_errors
