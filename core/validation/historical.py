from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from core.validation.exceptions import UnimplementedErrorMessageException
from core.validation.failures import ValidationFailureMixin


class NonUserFacingValidationFailure(ValidationFailureMixin):
    """Historical Validation Failures do not support validation messages."""

    @abstractmethod
    def __str__(self):
        pass


@dataclass
class ExtraSheetFailure(NonUserFacingValidationFailure):
    """Class representing an extra sheet failure."""

    extra_sheet: str

    def __str__(self):
        """
        Method to get the string representation of the extra sheet failure.
        """
        return (
            "Extra Sheets Failure: The workbook included a sheet named"
            f'"{self.extra_sheet}" but it is not in the schema.'
        )

    def to_message(self) -> tuple[str | None, str | None, str]:
        raise UnimplementedErrorMessageException


@dataclass
class EmptySheetFailure(NonUserFacingValidationFailure):
    """Class representing an empty sheet failure."""

    empty_sheet: str

    def __str__(self):
        """Method to get the string representation of the empty sheet failure."""
        return f'Empty Sheets Failure: The sheet named "{self.empty_sheet}" contains no ' "data."

    def to_message(self) -> tuple[str | None, str | None, str]:
        raise UnimplementedErrorMessageException


@dataclass
class ExtraColumnFailure(NonUserFacingValidationFailure):
    """Class representing an extra column failure."""

    sheet: str
    extra_column: str

    def __str__(self):
        """
        Method to get the string representation of the extra column failure.
        """
        return f'Extra Column Failure: Sheet "{self.sheet}" Column' f' "{self.extra_column}" is not in the schema.'

    def to_message(self) -> tuple[str | None, str | None, str]:
        raise UnimplementedErrorMessageException


@dataclass
class MissingColumnFailure(NonUserFacingValidationFailure):
    """Class representing a missing column failure."""

    sheet: str
    missing_column: str

    def __str__(self):
        """Method to get the string representation of the missing column failure."""
        return (
            f'Missing Column Failure: Sheet "{self.sheet}" Column'
            f' "{self.missing_column}" is missing from the schema.'
        )

    def to_message(self) -> tuple[str | None, str | None, str]:
        raise UnimplementedErrorMessageException


@dataclass
class NonUniqueFailure(NonUserFacingValidationFailure):
    """Class representing a non-unique value failure."""

    sheet: str
    column: str

    def __str__(self):
        """Method to get the string representation of the non-unique value failure."""
        return f'Non Unique Failure: Sheet "{self.sheet}" column "{self.column}" should ' f"contain only unique values."

    def to_message(self) -> tuple[str | None, str | None, str]:
        raise UnimplementedErrorMessageException


@dataclass
class OrphanedRowFailure(NonUserFacingValidationFailure):
    """Class representing an orphaned row failure."""

    sheet: str
    row: int
    foreign_key: str
    fk_value: Any
    parent_table: str
    parent_pk: str

    def __str__(self):
        """Method to get the string representation of the orphaned row failure."""
        return (
            f'Orphaned Row Failure: Sheet "{self.sheet}" Column "{self.foreign_key}" '
            f"Row {self.row} "
            f'Value "{self.fk_value}" not in parent table '
            f'"{self.parent_table}" where PK "{self.parent_pk}"'
        )

    def to_message(self) -> tuple[str | None, str | None, str]:
        raise UnimplementedErrorMessageException


@dataclass
class InvalidSheetFailure(NonUserFacingValidationFailure):
    """Class representing an invalid sheet failure."""

    invalid_sheet: str

    def __str__(self):
        """Method to get the string representation of the empty sheet failure."""
        return (
            f"Invalid Sheets Failure: The sheet named {self.invalid_sheet} is invalid "
            f"as it is missing expected values"
        )

    def to_message(self) -> tuple[str | None, str | None, str]:
        raise UnimplementedErrorMessageException
