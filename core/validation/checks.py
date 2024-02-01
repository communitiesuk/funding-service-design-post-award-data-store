from abc import ABC, abstractmethod

import pandas as pd

from core.exceptions import InitialValidationError

class Check:
    def __init__(
        self,
        sheet: str,
        column: int,
        row: int,
        expected_values: tuple | None,
        error_message: str
    ):
        self.sheet = sheet
        self.column = column
        self.row = row
        self.expected_values = expected_values
        self.error_message = error_message
    
    def run(self, workbook: dict[str, pd.DataFrame]) -> bool:
        actual_value = str(workbook[self.sheet].iloc[self.column][self.row]).strip()
        if actual_value not in self.expected_values:
            return False
        return True


class DynamicCheck(Check, ABC):
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
        error_message: str
    ):
        super().__init__(sheet, column, row, None, error_message)
        self.calc_values = calc_values

    @abstractmethod
    def calculate_expected_values(self) -> tuple:
        pass

    def run(self, workbook: dict[str, pd.DataFrame]) -> bool:
        self.calculate_expected_values(workbook)
        return super().run(workbook)


class MappedCheck(DynamicCheck):
    def calculate_expected_values(self, workbook: dict[str, pd.DataFrame]) -> tuple:
        mapping = self.calc_values["mapping"]
        assert isinstance(mapping, dict)
        mapped_column = self.calc_values["mapped_column"]
        mapped_row = self.calc_values["mapped_row"]
        value_to_map = str(workbook[self.sheet].iloc[mapped_column][mapped_row]).strip()
        self.expected_values = mapping.get(value_to_map)


class AuthorisationCheck(DynamicCheck):
    auth: dict | None

    def set_auth(self, auth: dict):
        self.auth = auth

    def calculate_expected_values(self, workbook: dict[str, pd.DataFrame]) -> tuple:
        auth_type = self.calc_values["auth_type"]
        expected_values = self.auth[auth_type]
        self.expected_values = expected_values
