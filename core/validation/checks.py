from core.validation.failures import ValidationFailureBase

class Check:
    def __init__(
        self,
        sheet: str,
        column: int,
        row: int,
        expected_values: tuple | None,
        error_type: ValidationFailureBase,
        error_message: str
    ):
        self.sheet = sheet
        self.column = column
        self.row = row
        self.expected_values = expected_values
        self.error_type = error_type
        self.error_message = error_message


class DynamicCheck(Check):
    """
    A check that dynamically generates the expected values based on the workbook.
    """
    calc_values: dict  # Values used to calculate the expected values

    def __init__(
        self,
        sheet: str,
        column: int,
        row: int,
        calc_values: dict,
        error_type: ValidationFailureBase,
        error_message: str
    ):
        super().__init__(sheet, column, row, None, error_type, error_message)
        self.calc_values = calc_values
