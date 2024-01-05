"""This module defines a set of classes representing different types of validation
failures that can occur while validating a Workbook, but that will not occur for user submissions.

These classes can be useful for developers to debug a data pipeline by providing more
detailed and granular failures that may occur when developing a new pipeline or adjusting an historical one.
"""

from abc import abstractmethod
from dataclasses import dataclass
from typing import Any

from core.validation.failures import ValidationFailureBase


class InternalValidationFailure(ValidationFailureBase):
    """Validation Failures that do not support validation messages.

    These highlight issues in the data caused by system error.
    """

    @abstractmethod
    def __str__(self):
        pass


@dataclass
class ExtraTableFailure(InternalValidationFailure):
    """Class representing an extra table failure."""

    extra_table: str

    def __str__(self):
        """
        Method to get the string representation of the extra table failure.
        """
        return (
            "Extra Table Failure: The data included a table named" f'"{self.extra_table}" but it is not in the schema.'
        )


@dataclass
class EmptyTableFailure(InternalValidationFailure):
    """Class representing an empty table failure."""

    empty_table: str

    def __str__(self):
        """Method to get the string representation of the empty table failure."""
        return f'Empty Table Failure: The table named "{self.empty_table}" contains no data.'


@dataclass
class ExtraColumnFailure(InternalValidationFailure):
    """Class representing an extra column failure."""

    table: str
    extra_column: str

    def __str__(self):
        """
        Method to get the string representation of the extra column failure.
        """
        return f'Extra Column Failure: Table "{self.table}" Column' f' "{self.extra_column}" is not in the schema.'


@dataclass
class MissingColumnFailure(InternalValidationFailure):
    """Class representing a missing column failure."""

    table: str
    missing_column: str

    def __str__(self):
        """Method to get the string representation of the missing column failure."""
        return (
            f'Missing Column Failure: Table "{self.table}" Column'
            f' "{self.missing_column}" is missing from the schema.'
        )


@dataclass
class NonUniqueFailure(InternalValidationFailure):
    """Class representing a non-unique value failure."""

    table: str
    column: str

    def __str__(self):
        """Method to get the string representation of the non-unique value failure."""
        return f'Non Unique Failure: Table "{self.table}" column "{self.column}" should ' f"contain only unique values."


@dataclass
class OrphanedRowFailure(InternalValidationFailure):
    """Class representing an orphaned row failure."""

    table: str
    row: int
    foreign_key: str
    fk_value: Any
    parent_table: str
    parent_pk: str

    def __str__(self):
        """Method to get the string representation of the orphaned row failure."""
        return (
            f'Orphaned Row Failure: Table "{self.table}" Column "{self.foreign_key}" '
            f"Row {self.row} "
            f'Value "{self.fk_value}" not in parent table '
            f'"{self.parent_table}" where PK "{self.parent_pk}"'
        )


@dataclass
class InvalidTableFailure(InternalValidationFailure):
    """Class representing an invalid table failure."""

    invalid_table: str

    def __str__(self):
        """Method to get the string representation of the empty table failure."""
        return f'Invalid Table Failure: Table "{self.invalid_table}" is invalid as it is missing expected values'
