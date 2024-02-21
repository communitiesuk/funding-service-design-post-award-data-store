"""This module defines a set of classes representing different types of validation
failures that can occur while validating a Workbook.

All the below classes are defined as dataclasses with appropriate attributes and methods
to represent the corresponding validation failures.
"""

from abc import ABC
from dataclasses import dataclass
from datetime import datetime

import pandas as pd

from core.validation.failures import ValidationFailureBase


class UserValidationFailure(ValidationFailureBase, ABC):
    """ABC for User Failures. Concrete classes must implement to_message().

    These highlight issues in the data caused by user input.
    """


@dataclass
class SchemaUserValidationFailure(UserValidationFailure, ABC):
    """ABC for User Failures raised during schema validation. Concrete classes use the attributes defined here."""

    table: str
    column: str | list[str]
    row_index: int


@dataclass
class GenericFailure(UserValidationFailure):
    """A generic failure that is instantiated so that all to_message() return values are either passed directly or
    cell index can be constructed from a column and row index.

    Raised with all the context needed to display straight to the user.
    Generic in the sense that it is not specific to a round or type of validation.
    """

    table: str
    section: str
    message: str
    cell_index: str = None
    column: str = None
    row_index: int = None

    def __post_init__(self):
        if not (self.cell_index or self.column):
            raise ValueError("GenericFailure must be instantiated with either cell_index or column and row_index")
            # row_index not included in the check because in some cases this can be instantiated with only column


@dataclass
class NonUniqueCompositeKeyFailure(SchemaUserValidationFailure):
    """Class representing a non-unique-composite_key failure that is raised due to duplicate data."""

    row: list


@dataclass
class WrongTypeFailure(SchemaUserValidationFailure):
    """Class representing a wrong type failure that is raised when data is of an incorrect type."""

    expected_type: str | float | int | datetime | object | bool | list
    actual_type: str
    failed_row: pd.Series | None


@dataclass
class InvalidEnumValueFailure(SchemaUserValidationFailure):
    """Class representing an invalid enum value failure raised when dropdown values have not been used."""

    row_values: tuple


@dataclass
class NonNullableConstraintFailure(SchemaUserValidationFailure):
    """Class representing a non-nullable constraint failure raised when a required cell is left blank."""

    failed_row: pd.Series | None


class PreTransFormationFailure(UserValidationFailure, ABC):
    pass


@dataclass
class WrongInputFailure(PreTransFormationFailure):
    """Class representing a wrong input pre-transformation failure."""

    value_descriptor: str
    entered_value: str
    expected_values: tuple


@dataclass
class UnauthorisedSubmissionFailure(PreTransFormationFailure):
    """Class representing an unauthorised submission failure."""

    value_descriptor: str
    entered_value: str
    expected_values: tuple
