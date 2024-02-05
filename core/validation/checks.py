from abc import ABC, abstractmethod

import pandas as pd


class Check(ABC):
    """
    Abstract base class representing a validation check on a specific tab/cell of a workbook.

    Attributes:
        sheet (str): The name of the sheet in the workbook.
        column (int): The column index of the cell to check.
        row (int): The row index of the cell to check.
        expected_values (tuple): A tuple of expected values for the cell.
        error_message (str): The error message sent to the user if the check fails.

    Methods:
        get_actual_value(workbook: dict[str, pd.DataFrame]) -> str:
            Retrieve the actual value from the workbook.
        run(workbook: dict[str, pd.DataFrame]) -> bool:
            Execute the check on the provided workbook.
    """

    def __init__(self, sheet: str, column: int, row: int, expected_values: tuple, error_message: str):
        self.sheet = sheet
        self.column = column
        self.row = row
        self.expected_values = expected_values
        self.error_message = error_message

    def get_actual_value(self, workbook: dict[str, pd.DataFrame]) -> str:
        return str(workbook[self.sheet].iloc[self.column][self.row]).strip()

    def run(self, workbook: dict[str, pd.DataFrame]) -> tuple[bool, str]:
        if self.get_actual_value(workbook) not in self.expected_values:
            return False, self.error_message
        return True, ""


class BasicCheck(Check):
    """
    Used for checks where the expected values are predefined.
    """

    pass


class DynamicCheck(Check, ABC):
    """
    Abstract class to represent a dynamic check, i.e. where parameters must be dynamically generated at runtime.
    Contains an abstract method to retrieve the expected values for the check.
    """

    @abstractmethod
    def get_expected_values(self, workbook: dict[str, pd.DataFrame]) -> tuple:
        pass


class ConflictingCheck(DynamicCheck):
    """
    A dynamic check that checks whether the values in two cells conflict with each other, for example where the provided
    fund type does not match any of the expected fund types for the provided place name. It uses a mapping defined
    elsewhere in the source code to map the values from one cell to a list of expected values for the other cell.

    Attributes:
        Inherits attributes from the DynamicCheck class.
        mapping (dict): A dictionary mapping the values from the mapped column and row to the expected values.
        mapped_column (int): The column index of the cell to map from.
        mapped_row (int): The row index of the cell to map from.
    """

    mapping: dict
    mapped_column: int
    mapped_row: int

    def __init__(
        self,
        sheet: str,
        column: int,
        row: int,
        expected_values: tuple,
        error_message: str,
        mapping: dict,
        mapped_column: int,
        mapped_row: int,
    ):
        super().__init__(sheet, column, row, expected_values, error_message)
        self.mapping = mapping
        self.mapped_column = mapped_column
        self.mapped_row = mapped_row

    def get_expected_values(self, workbook: dict[str, pd.DataFrame]) -> tuple:
        value_to_map = str(workbook[self.sheet].iloc[self.mapped_column][self.mapped_row]).strip()
        return self.mapping.get(value_to_map, [])

    def run(self, workbook: dict[str, pd.DataFrame]) -> tuple[bool, str]:
        result = self.get_actual_value(workbook) in self.get_expected_values(workbook)
        return result, self.error_message


class AuthorisationCheck(DynamicCheck):
    """
    A dynamic check which uses authorisation, verifying if the user is submitting data for the correct place names or
    fund types associated with their account.

    Though empty auth values are handled by the code here, submissions with auth values set to None are no longer
    permitted for round 4 data, and will raise a validation error in initial_validate.py whenever this is the case.

    Attributes:
        Inherits attributes from the DynamicCheck class.
        auth_dict (dict): A dictionary of authorisation values for the user.
        auth_type (str): The type of authorisation to check, e.g. "Place Names" or "Fund Types".

    Methods:
        set_auth_dict(auth_dict: dict | None):
            Set the authorisation dictionary for the user.
        substitute_error_message(actual_value: str, expected_values: tuple[str]) -> str:
            Substitute the actual and expected values into the error message.
    """

    auth_dict: dict | None
    auth_type: str

    def __init__(self, sheet: str, column: int, row: int, expected_values: tuple, error_message: str, auth_type: str):
        super().__init__(sheet, column, row, expected_values, error_message)
        self.auth_type = auth_type

    def set_auth_dict(self, auth_dict: dict | None):
        self.auth_dict = auth_dict

    def substitute_error_message(self, actual_value: str, expected_values: tuple[str]) -> str:
        wrong_place_or_fund_type = actual_value or "None"
        allowed_places_or_fund_types = ", ".join(expected_values)
        return self.error_message.format(
            wrong_place_or_fund_type=wrong_place_or_fund_type,
            allowed_places_or_fund_types=allowed_places_or_fund_types,
        )

    def get_expected_values(self, workbook: dict[str, pd.DataFrame]) -> tuple:
        return self.auth_dict[self.auth_type] if self.auth_dict else ()

    def run(self, workbook: dict[str, pd.DataFrame]) -> tuple[bool, str]:
        actual_value = self.get_actual_value(workbook)
        expected_values = self.get_expected_values(workbook)
        result = actual_value in expected_values
        error_message = self.substitute_error_message(actual_value, expected_values)
        return result, "" if result else error_message
