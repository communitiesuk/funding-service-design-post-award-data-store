"""This module defines a set of classes representing different types of validation
failures that can occur while validating a Workbook.

All the below classes are defined as dataclasses with appropriate attributes and methods
to represent the corresponding validation failures.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any


class ValidationFailure(ABC):
    """Abstract base class representing a validation failure."""

    @abstractmethod
    def __str__(self):
        """Abstract method to get the string representation of the failure."""


@dataclass
class CantCastFailure(ValidationFailure):
    """Class representing a type casting failure."""

    sheet: str
    column: str
    original_type: str
    target_type: str

    def __str__(self):
        """Method to get the string representation of the type casting failure."""
        return (
            f'Type Casting Failure: Sheet "{self.sheet}" column '
            f'"{self.column}" couldn\'t cast type from "{self.original_type}" '
            f'to expected type "{self.target_type}"'
        )


@dataclass
class ExtraSheetFailure(ValidationFailure):
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


@dataclass
class EmptySheetFailure(ValidationFailure):
    """Class representing an empty sheet failure."""

    empty_sheet: str

    def __str__(self):
        """Method to get the string representation of the empty sheet failure."""
        return (
            f'Empty Sheets Failure: The sheet named "{self.empty_sheet}" contain no '
            "data."
        )


@dataclass
class ExtraColumnFailure(ValidationFailure):
    """Class representing an extra column failure."""

    sheet: str
    extra_column: str

    def __str__(self):
        """
        Method to get the string representation of the extra column failure.
        """
        return (
            f'Extra Column Failure: Sheet "{self.sheet}" Column'
            f' "{self.extra_column}" is not in the schema.'
        )


@dataclass
class MissingColumnFailure(ValidationFailure):
    """Class representing a missing column failure."""

    sheet: str
    missing_column: str

    def __str__(self):
        """Method to get the string representation of the missing column failure."""
        return (
            f'Missing Column Failure: Sheet "{self.sheet}" Column'
            f' "{self.missing_column}" is missing from the schema.'
        )


@dataclass
class NonUniqueFailure(ValidationFailure):
    """Class representing a non-unique value failure."""

    sheet: str
    column: str

    def __str__(self):
        """Method to get the string representation of the non-unique value failure."""
        return (
            f'Non Unique Failure: Sheet "{self.sheet}" column "{self.column}" should '
            f"contain only unique values."
        )


@dataclass
class WrongTypeFailure(ValidationFailure):
    """Class representing a wrong type failure."""

    sheet: str
    column: str
    expected_type: str
    actual_type: str

    def __str__(self):
        """Method to get the string representation of the wrong type failure."""
        return (
            f'Wrong Type Failure: Sheet "{self.sheet}" column "{self.column}" expected '
            f'type "{self.expected_type}", got type "{self.actual_type}"'
        )


@dataclass
class OrphanedRowFailure(ValidationFailure):
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
            f'Row {self.row} Value "{self.fk_value}" not in parent table '
            f'"{self.parent_table}" where PK "{self.parent_pk}"'
        )
