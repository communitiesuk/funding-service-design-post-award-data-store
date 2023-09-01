"""This module defines a set of classes representing different types of validation
failures that can occur while validating a Workbook.

All the below classes are defined as dataclasses with appropriate attributes and methods
to represent the corresponding validation failures.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from core.const import (
    INTERNAL_COLUMN_TO_FORM_COLUMN_AND_SECTION,
    INTERNAL_TABLE_TO_FORM_TAB,
    PRETRANSFORMATION_FAILURE_UC_MESSAGE_BANK,
)
from core.util import group_by_first_element


class ValidationFailure(ABC):
    """Abstract base class representing a validation failure."""

    @abstractmethod
    def __str__(self):
        """Abstract method to get the string representation of the failure."""


class PreTransFormationFailure(ValidationFailure, ABC):
    pass


class TFUCFailureMessage(ABC):
    """Abstract base class representing a Towns Fund User-Centered Failure message."""

    @abstractmethod
    def to_user_centered_components(self) -> tuple[str | None, str | None, str]:
        """Abstract method that returns the User-Centered failure message components.

        :return: A tuple containing the sheet, subsection, and the message itself.
        """


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
        return f'Empty Sheets Failure: The sheet named "{self.empty_sheet}" contains no ' "data."


@dataclass
class ExtraColumnFailure(ValidationFailure):
    """Class representing an extra column failure."""

    sheet: str
    extra_column: str

    def __str__(self):
        """
        Method to get the string representation of the extra column failure.
        """
        return f'Extra Column Failure: Sheet "{self.sheet}" Column' f' "{self.extra_column}" is not in the schema.'


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
        return f'Non Unique Failure: Sheet "{self.sheet}" column "{self.column}" should ' f"contain only unique values."


@dataclass
class NonUniqueCompositeKeyFailure(ValidationFailure, TFUCFailureMessage):
    """Class representing a non-unique-composite_key failure."""

    sheet: str
    cols: tuple
    row: list

    def __str__(self):
        """Method to get the string representation of the non-unique-composite_key failure."""
        cols_str = ", ".join(str(i) for i in self.cols)
        row_str = list(self.row)
        return (
            f'Non Unique Row Failure: Sheet "{self.sheet}"; '
            f'Columns "{cols_str}" contains contains a duplicate row consisting of the values: '
            f'"{row_str}"'
        )

    def to_user_centered_components(self) -> tuple[str, str, str, str]:
        # Funding, Outputs and Outcomes
        # Funding - Project, Funding Source Name, Funding Source, and
        # Messages
        # Funding: You have repeated funding information. You must use a new row for each project, funding source name,
        # funding type and if its been secured.
        # Outputs: You must use a new row for each project, funding source name, funding type and if its been secured.
        # Outcomes
        return "Unimplemented", "Unimplemented", "Unimplemented", "Unimplemented"


@dataclass
class WrongTypeFailure(ValidationFailure, TFUCFailureMessage):
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

    def to_user_centered_components(self) -> tuple[str, str, str, str]:
        # Numbers - 1. Outcomes/Outputs is just numerical (e.g not m^2), 2. Funding/PSI is Monetary
        # Dates - Programme Progress sheet: Start, Completion and Date of Most Important...
        return "Unimplemented", "Unimplemented", "Unimplemented", "Unimplemented"


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
            f"Row {self.row + 2} "  # +2 for Excel 1-index and table header row
            f'Value "{self.fk_value}" not in parent table '
            f'"{self.parent_table}" where PK "{self.parent_pk}"'
        )


@dataclass
class InvalidEnumValueFailure(ValidationFailure, TFUCFailureMessage):
    """Class representing an invalid enum value failure."""

    sheet: str
    column: str
    row: int
    row_values: tuple
    value: Any

    def __str__(self):
        """Method to get the string representation of the invalid enum value failure."""
        return (
            f'Enum Value Failure: Sheet "{self.sheet}" Column "{self.column}" '
            f"Row {self.row + 2} "  # +2 for Excel 1-index and table header row
            f'Value "{self.value}" is not a valid enum value.'
        )

    def to_user_centered_components(self) -> tuple[str, str, str]:
        sheet = INTERNAL_TABLE_TO_FORM_TAB[self.sheet]
        column, section = INTERNAL_COLUMN_TO_FORM_COLUMN_AND_SECTION[self.column]
        message = (
            f'For column "{column}", you have entered "{self.value}" which isn\'t correct. You must select an '
            f"option from the list provided"
        )

        # additional logic for outcomes to differentiate between footfall and non-footfall
        if sheet == "Outcomes" and self.row_values[4] == "Year-on-year % change in monthly footfall":
            section = "Footfall Indicator"

        # additional logic for risk location
        if sheet == "Risk Register":
            if self.row_values[1]:
                # project risk
                section = f"Project {int(self.row_values[1].split('-')[2])} Risks"
            else:
                # programme risk
                section = "Programme Risks"

        return sheet, section, message


@dataclass
class NonNullableConstraintFailure(ValidationFailure, TFUCFailureMessage):
    """Class representing a non-nullable constraint failure."""

    sheet: str
    column: str

    def __str__(self):
        """Method to get the string representation of the non-nullable constraint failure."""
        return (
            f'Non-nullable Constraint Failure: Sheet "{self.sheet}" Column "{self.column}" '
            f"is non-nullable but contains a null value(s)."
        )

    def to_user_centered_components(self) -> tuple[str, str, str]:
        """Generate user-centered components for NonNullableConstraintFailure.

        This function returns user-centered components in the case of a NonNullableConstraintFailure.
        In instances where the Unit of Measurement is null, a distinct error message is necessary.
        The function distinguishes between Outputs and Outcomes and adjusts the error message accordingly.

        return: tuple[str, str, str]: A tuple containing the sheet name, section, and error message.
        """
        sheet = INTERNAL_TABLE_TO_FORM_TAB[self.sheet]
        column, section = INTERNAL_COLUMN_TO_FORM_COLUMN_AND_SECTION[self.column]

        message = (
            f'There are blank cells in column: "{column}". '
            f"Use the space provided to tell us the relevant information"
        )

        if sheet == "Project Outputs":
            section = "Project Outputs"
            if column == "Unit of Measurement":
                message = (
                    "There are blank cells in column: Unit of Measurement."
                    " Please ensure you have selected valid indicators for all Outputs on the Project Outputs tab,"
                    " and that the Unit of Measurement is correct for this output"
                )
        elif sheet == "Outcomes" and column == "Unit of Measurement":
            message = (
                "There are blank cells in column: Unit of Measurement."
                " Please ensure you have selected valid indicators for all Outcomes on the Outcomes tab,"
                " and that the Unit of Measurement is correct for this outcome"
            )
        return sheet, section, message


@dataclass
class WrongInputFailure(PreTransFormationFailure, TFUCFailureMessage):
    """Class representing a wrong input pre-transformation failure."""

    value_descriptor: str
    entered_value: str
    expected_values: set

    def __str__(self):
        """
        Method to get the string representation of the wrong input pre-transformation failure.
        """
        return (
            f"Pre-transformation Failure: The workbook failed a pre-transformation check for {self.value_descriptor} "
            f'where the entered value "{self.entered_value}" '
            f'was outside of the expected values [{", ".join(self.expected_values)}].'
        )

    def to_user_centered_components(self) -> tuple[str | None, str | None, str]:
        return None, None, PRETRANSFORMATION_FAILURE_UC_MESSAGE_BANK[self.value_descriptor]


@dataclass
class NoInputFailure(PreTransFormationFailure, TFUCFailureMessage):
    """Class representing a no input failure."""

    value_descriptor: str

    def __str__(self):
        """
        Method to get the string representation of the no input failure.
        """
        return f"No Input Failure: Expected an input value for {self.value_descriptor}"

    def to_user_centered_components(self) -> tuple[str | None, str | None, str]:
        return None, None, PRETRANSFORMATION_FAILURE_UC_MESSAGE_BANK[self.value_descriptor]


@dataclass
class InvalidSheetFailure(ValidationFailure):
    """Class representing an invalid sheet failure."""

    invalid_sheet: str

    def __str__(self):
        """Method to get the string representation of the empty sheet failure."""
        return (
            f"Invalid Sheets Failure: The sheet named {self.invalid_sheet} is invalid "
            f"as it is missing expected values"
        )


@dataclass
class InvalidOutcomeProjectFailure(ValidationFailure):
    """Class representing an invalid project related to an outcome."""

    invalid_project: str

    def __str__(self):
        """Method to get the string representation of the invalid outcome project failure."""
        return (
            f"Invalid Project Failure: The project '{self.invalid_project}' on the sheet "
            f"'6 - Outcomes' selected under the 'Relevant project(s)' header is invalid. "
            f"Please ensure you select all projects from the drop-down provided."
        )


def serialise_user_centered_failures(
    validation_failures: list[ValidationFailure],
) -> dict[str, dict[str, list[str]]] | dict[str, dict]:
    """Serialises failures into messages and groups them by tab and section.

    :param validation_failures: validation failure objects
    :return: validation failure messages grouped by tab and section
    """
    # filter and convert to user centered components
    uc_failures = [
        failure.to_user_centered_components()
        for failure in validation_failures
        if isinstance(failure, TFUCFailureMessage)
    ]

    # one pre-transformation failure means payload is entirely pre-transformation failures
    if any(isinstance(failure, PreTransFormationFailure) for failure in validation_failures):
        # ignore tab and section for pre-transformation failures
        return {"PreTransformationErrors": [message for _, _, message in uc_failures]}

    # group by tab and section
    failures_grouped_by_tab = group_by_first_element(uc_failures)
    failures_grouped_by_tab_and_section = {
        tab: group_by_first_element(failures) for tab, failures in failures_grouped_by_tab.items()
    }
    return {"TabErrors": failures_grouped_by_tab_and_section}
