from abc import ABC, abstractmethod

import pandas as pd


class Check(ABC):
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
    pass


class DynamicCheck(Check, ABC):
    """
    A check that dynamically generates the expected values based on the workbook.
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


class MappedCheck(DynamicCheck):
    def calculate_expected_values(self, workbook: dict[str, pd.DataFrame]) -> tuple:
        mapping = self._dynamic_params["mapping"]
        assert isinstance(mapping, dict)
        mapped_column = self._dynamic_params["mapped_column"]
        mapped_row = self._dynamic_params["mapped_row"]
        value_to_map = str(workbook[self.sheet].iloc[mapped_column][mapped_row]).strip()
        self.expected_values = mapping.get(value_to_map, [])


class AuthorisationCheck(DynamicCheck):
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
