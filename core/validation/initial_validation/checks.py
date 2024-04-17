from abc import ABC, abstractmethod
from typing import Iterable

import pandas as pd


class Check(ABC):
    """
    Abstract base class representing a validation check on a specific tab/cell of a workbook.

    Attributes:
        sheet (str): The name of the sheet in the workbook.
        row (int): The row index of the cell to check.
        column (int): The column index of the cell to check.
        expected_values (tuple): A tuple of expected values for the cell.
        error_message (str): The error message sent to the user if the check fails.

    Methods:
        get_actual_value(workbook: dict[str, pd.DataFrame]) -> str:
            Retrieve the actual value from the workbook.
        run(workbook: dict[str, pd.DataFrame]) -> bool:
            Execute the check on the provided workbook.
    """

    def __init__(self, sheet: str, row: int, column: int, expected_values: tuple, error_message: str):
        self.sheet = sheet
        self.row = row
        self.column = column
        self.expected_values = expected_values
        self.error_message = error_message

    def get_actual_value(self, workbook: dict[str, pd.DataFrame]) -> str:
        return str(workbook[self.sheet].iloc[self.row][self.column]).strip()

    @abstractmethod
    def run(self, workbook: dict[str, pd.DataFrame], **kwargs) -> tuple[bool, str]:
        pass


class BasicCheck(Check):
    """
    Used for checks where the expected values are predefined.
    """

    def run(self, workbook: dict[str, pd.DataFrame], **kwargs) -> tuple[bool, str]:
        result = self.get_actual_value(workbook) in self.expected_values
        return result, self.error_message


class DynamicCheck(Check, ABC):
    """
    Abstract class to represent a dynamic check, i.e. where parameters must be dynamically generated at runtime.
    Contains an abstract method to retrieve the expected values for the check.
    """

    @abstractmethod
    def get_expected_values(self, workbook: dict[str, pd.DataFrame], **kwargs) -> Iterable:
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

    mapping: dict[str, set]
    mapped_column: int
    mapped_row: int

    def __init__(
        self,
        sheet: str,
        row: int,
        column: int,
        expected_values: tuple,
        error_message: str,
        mapping: dict,
        mapped_row: int,
        mapped_column: int,
    ):
        super().__init__(sheet, row, column, expected_values, error_message)
        self.mapping = mapping
        self.mapped_row = mapped_row
        self.mapped_column = mapped_column

    def get_expected_values(self, workbook: dict[str, pd.DataFrame], **kwargs) -> set:
        value_to_map = str(workbook[self.sheet].iloc[self.mapped_row][self.mapped_column]).strip()
        return self.mapping.get(value_to_map, set())

    def run(self, workbook: dict[str, pd.DataFrame], **kwargs) -> tuple[bool, str]:
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
        auth_type (str): The type of authorisation to check, e.g. "Place Names" or "Fund Types".

    Methods:
        substitute_error_message(actual_value: str, expected_values: tuple[str]) -> str:
            Substitute the actual and expected values into the error message.
    """

    auth_type: str

    def __init__(self, sheet: str, row: int, column: int, expected_values: tuple, error_message: str, auth_type: str):
        super().__init__(sheet, row, column, expected_values, error_message)
        self.auth_type = auth_type

    def substitute_error_message(self, actual_value: str, expected_values: tuple[str]) -> str:
        actual_value = actual_value or "None"
        expected_values = ", ".join(expected_values)
        return self.error_message.format(
            entered_value=actual_value,
            allowed_values=expected_values,
        )

    def get_expected_values(self, workbook: dict[str, pd.DataFrame], **kwargs) -> list:
        auth = kwargs.get("auth")
        return auth[self.auth_type] if auth else []

    def run(self, workbook: dict[str, pd.DataFrame], **kwargs) -> tuple[bool, str]:
        auth = kwargs.get("auth")
        actual_value = self.get_actual_value(workbook)
        expected_values = self.get_expected_values(workbook, auth=auth)
        result = actual_value in expected_values
        error_message = self.substitute_error_message(actual_value, expected_values)
        return result, "" if result else error_message


class SheetCheck:
    """
    Checks that the admin sheet exists for the fund being submitted. If it does not exist,
    then the return being submitted is invalid and will otherwise raise a KeyError when other
    checks take place.
    Attributes:
        sheet (str): The name of the sheet in the workbook.
        error_message (str): The error message sent to the user if the check fails.
    """

    def __init__(self, sheet: str, error_message: str):
        self.sheet = sheet
        self.error_message = error_message

    def run(self, workbook: dict[str, pd.DataFrame]) -> tuple[bool, str]:
        sheet_exists = workbook.get(self.sheet)
        if sheet_exists is None:
            return False, self.error_message
        else:
            return True, self.error_message
