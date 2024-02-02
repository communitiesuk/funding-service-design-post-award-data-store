from abc import ABC, abstractmethod

import pandas as pd


class Check(ABC):
    """
    Abstract base class representing a validation check on a specific tab/cell of a workbook.

    Attributes:
        sheet (str): The name of the sheet in the workbook.
        column (int): The column index of the cell to check.
        row (int): The row index of the cell to check.
        expected_values (tuple or None): A tuple of expected values for the cell, or None if any value is acceptable.
        error_message (str): The error message sent to the user if the check fails.
        actual_value (str or None): The actual value retrieved from the cell on the ingested spreadsheet.

    Methods:
        run(workbook: dict[str, pd.DataFrame]) -> bool:
            Execute the check on the provided workbook.
    """

    def __init__(self, sheet: str, column: int, row: int, expected_values: tuple | None, error_message: str):
        self.sheet = sheet
        self.column = column
        self.row = row
        self.expected_values = expected_values
        self.error_message = error_message
        self.actual_value = None

    def run(self, workbook: dict[str, pd.DataFrame]) -> bool:
        self.actual_value = str(workbook[self.sheet].iloc[self.column][self.row]).strip()
        if self.actual_value not in self.expected_values:
            return False
        return True


class BasicCheck(Check):
    """
    Used for checks that require no extra parameters or variable error messages
    """

    pass


class DynamicCheck(Check, ABC):
    """
    Used to represent a dynamic check, i.e. containing parameters dynamically generated at runtime. Contains methods for
    calculating the expected values on a cell, and substituting placeholders in error messages with the calculated
    parameters.

    Attributes:
        _dynamic_params (dict): Dictionary containing values used to calculate the expected values dynamically.
        _error_message_with_placeholders (str): The error message template before substitution.

    """

    _dynamic_params: dict  # Values used to calculate the expected values
    _error_message_with_placeholders: str  # The error message before substitution

    def __init__(self, sheet: str, column: int, row: int, dynamic_params: dict, error_message_with_placeholders: str):
        super().__init__(sheet, column, row, None, None)
        self._dynamic_params = dynamic_params
        self._error_message_with_placeholders = error_message_with_placeholders

    @abstractmethod
    def calculate_expected_values(self) -> tuple:
        pass

    def substitute_error_message(self) -> None:
        self.error_message = self._error_message_with_placeholders

    def run(self, workbook: dict[str, pd.DataFrame]) -> bool:
        self.calculate_expected_values(workbook)
        result = super().run(workbook)
        self.substitute_error_message()
        return result


class ConflictingCheck(DynamicCheck):
    """
    A dynamic check that uses calculated expected values to compare with the ingested spreadsheet. The values are
    retrieved from specified columns and rows in the workbook to be mapped to a set of predefined values.

    Parameters:
        workbook (dict[str, pd.DataFrame]): A dictionary of DataFrames representing the ingested workbook.

    Returns:
        tuple: The calculated expected values based on the dynamically generated parameters and mapping.

    """

    def calculate_expected_values(self, workbook: dict[str, pd.DataFrame]) -> tuple:
        mapping = self._dynamic_params["mapping"]
        assert isinstance(mapping, dict)
        mapped_column = self._dynamic_params["mapped_column"]
        mapped_row = self._dynamic_params["mapped_row"]
        value_to_map = str(workbook[self.sheet].iloc[mapped_column][mapped_row]).strip()
        self.expected_values = mapping.get(value_to_map, [])


class AuthorisationCheck(DynamicCheck):
    """
    A dynamic check which uses authorization, verifying if the user is submitting data for the correct place names
    and fund types associated with their account.

    Though empty auth values are handled by the code here, submissions with auth values set to None are no longer
    permitted for round 4 data, and will raise a validation error in initial_validate.py whenever this is the case.

    Parameters:
        Inherits attributes from the DynamicCheck class.
        auth (dict or None): Authorization information to be set using the set_auth method.
    """

    auth: dict | None

    def set_auth(self, auth: dict | None):
        self.auth = auth

    def calculate_expected_values(self, workbook: dict[str, pd.DataFrame]) -> tuple:
        auth_type = self._dynamic_params["auth_type"]
        expected_values = self.auth[auth_type] if self.auth else ()
        self.expected_values = expected_values

    def substitute_error_message(self) -> None:
        wrong_place_or_fund_type = self.actual_value or "None"
        allowed_places_or_fund_types = ", ".join(self.expected_values)
        self.error_message = self._error_message_with_placeholders.format(
            wrong_place_or_fund_type=wrong_place_or_fund_type,
            allowed_places_or_fund_types=allowed_places_or_fund_types,
        )
