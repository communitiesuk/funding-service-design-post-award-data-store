"""This module defines a set of classes representing different types of validation
failures that can occur while validating a Workbook.

All the below classes are defined as dataclasses with appropriate attributes and methods
to represent the corresponding validation failures.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

import pandas as pd

from core.const import (
    INTERNAL_COLUMN_TO_FORM_COLUMN_AND_SECTION,
    INTERNAL_TABLE_TO_FORM_TAB,
    INTERNAL_TYPE_TO_MESSAGE_FORMAT,
    PRETRANSFORMATION_FAILURE_MESSAGE_BANK,
)
from core.util import get_project_number, group_by_first_element
from core.validation.exceptions import UnimplementedErrorMessageException


class ValidationFailure(ABC):
    """Abstract base class representing a validation failure."""

    @abstractmethod
    def __str__(self):
        """Abstract method to get the string representation of the failure.

        NOTE: This representation of validation failures is outdated and replaced by the "to_message" function.
            This is retained because it will be useful for debugging if we ever need to ingest additional historical
            data sets.
        """

    @abstractmethod
    def to_message(self) -> tuple[str | None, str | None, str]:
        """Abstract method - implementations of this return message components.

        :return: A tuple containing the sheet, subsection, and the message itself.
        """


class PreTransFormationFailure(ValidationFailure, ABC):
    pass


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

    def to_message(self) -> tuple[str | None, str | None, str]:
        raise UnimplementedErrorMessageException


@dataclass
class EmptySheetFailure(ValidationFailure):
    """Class representing an empty sheet failure."""

    empty_sheet: str

    def __str__(self):
        """Method to get the string representation of the empty sheet failure."""
        return f'Empty Sheets Failure: The sheet named "{self.empty_sheet}" contains no ' "data."

    def to_message(self) -> tuple[str | None, str | None, str]:
        raise UnimplementedErrorMessageException


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

    def to_message(self) -> tuple[str | None, str | None, str]:
        raise UnimplementedErrorMessageException


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

    def to_message(self) -> tuple[str | None, str | None, str]:
        raise UnimplementedErrorMessageException


@dataclass
class NonUniqueFailure(ValidationFailure):
    """Class representing a non-unique value failure."""

    sheet: str
    column: str

    def __str__(self):
        """Method to get the string representation of the non-unique value failure."""
        return f'Non Unique Failure: Sheet "{self.sheet}" column "{self.column}" should ' f"contain only unique values."

    def to_message(self) -> tuple[str | None, str | None, str]:
        raise UnimplementedErrorMessageException


@dataclass
class NonUniqueCompositeKeyFailure(ValidationFailure):
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

    def to_message(self) -> tuple[str, str, str]:
        """Generate user-centered components for NonUniqueCompositeKeyFailure.

        This function returns user-centered components in the case of a NonUniqueCompositeKeyFailure.
        When a Unique combination of cell values is required on separate row to act as composite keys this function
        will return a message. The function distinguishes between Funding profiles, Outputs, Outcomes, and Risk Register
        and displays an appropriate message.

        return: tuple[str, str, str]: A tuple containing the sheet name, section, and error message.
        """
        sheet = INTERNAL_TABLE_TO_FORM_TAB[self.sheet]

        if sheet == "Funding Profiles":
            row_str = ", ".join(self.row[1:4])
            project_number = get_project_number(self.row[0])
            section = f"Funding Profiles - Project {project_number}"
            message = (
                f"You have repeated funding information. You must use a new row for each project, "
                f"funding source name, funding type and if its been secured. You have"
                f' repeat entries for "{row_str}"'
            )
        elif sheet == "Project Outputs":
            project_number = get_project_number(self.row[0])
            section = f"Project Outputs - Project {project_number}"
            message = (
                f'You have entered the indicator "{self.row[1]}" repeatedly. Only enter an indicator once per project'
            )
        elif sheet == "Outcomes":
            section = "Outcome Indicators (excluding footfall)"
            message = (
                f'You have entered the indicator "{self.row[1]}" repeatedly for the same project and geography '
                f"indicator. Only enter an indicator once per project"
            )
        elif sheet == "Risk Register":
            if pd.notna(self.row[1]):
                project_number = get_project_number(self.row[1])
                section = f"Project Risks - Project {project_number}"
            else:
                section = "Programme Risks"
            message = f'You have entered the risk "{self.row[2]}" repeatedly. Only enter a risk once per project'
        else:
            raise UnimplementedErrorMessageException

        return sheet, section, message


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

    def to_message(self) -> tuple[str, str, str]:
        sheet = INTERNAL_TABLE_TO_FORM_TAB[self.sheet]
        column, section = INTERNAL_COLUMN_TO_FORM_COLUMN_AND_SECTION[self.column]
        expected_type = INTERNAL_TYPE_TO_MESSAGE_FORMAT[self.expected_type]
        actual_type = INTERNAL_TYPE_TO_MESSAGE_FORMAT[self.actual_type]
        if sheet == "Outcomes":
            column, section = "Financial Year 2022/21 - Financial Year 2029/30", (
                "Outcome Indicators (excluding " "footfall) and Footfall Indicator"
            )

        if self.expected_type == "datetime64[ns]":
            message = (
                f'For column "{column}" you entered {actual_type} when we expected {expected_type}. '
                f"You must enter dates in the correct format, for example, Dec-22, Jun-23"
            )
        elif sheet == "PSI":
            message = (
                f'For column "{column}" you entered {actual_type} when we expected {expected_type}. '
                f"You must enter the required data in the correct format, for example, £5,588.13 or £238,"
                f"062.50"
            )
        elif sheet == "Funding Profiles":
            message = (
                f'Between columns "{column}" you entered {actual_type} when we expected {expected_type}. '
                f"You must enter the required data in the correct format, for example, £5,588.13 or £238,"
                f"062.50"
            )
        elif sheet in ["Project Outputs", "Outcomes"]:
            message = (
                f'Between columns "{column}" you entered {actual_type} when we expected {expected_type}. '
                f"You must enter data using the correct format, for example, 9 rather than 9m2. Only use numbers"
            )
        else:
            raise UnimplementedErrorMessageException

        return sheet, section, message


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

    def to_message(self) -> tuple[str | None, str | None, str]:
        raise UnimplementedErrorMessageException


@dataclass
class InvalidEnumValueFailure(ValidationFailure):
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

    def to_message(self) -> tuple[str, str, str]:
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
            project_id = self.row_values[1]
            if pd.notna(project_id):
                # project risk
                project_number = get_project_number(self.row_values[1])
                section = f"Project Risks - Project {project_number}"
            else:
                # programme risk
                section = "Programme Risks"

        if section == "Project Funding Profiles":
            project_number = get_project_number(self.row_values[0])
            section = f"Project Funding Profiles - Project {project_number}"

        return sheet, section, message


@dataclass
class NonNullableConstraintFailure(ValidationFailure):
    """Class representing a non-nullable constraint failure."""

    sheet: str
    column: str

    def __str__(self):
        """Method to get the string representation of the non-nullable constraint failure."""
        return (
            f'Non-nullable Constraint Failure: Sheet "{self.sheet}" Column "{self.column}" '
            f"is non-nullable but contains a null value(s)."
        )

    def to_message(self) -> tuple[str, str, str]:
        """Generate error message components for NonNullableConstraintFailure.

        This function returns error message components in the case of a NonNullableConstraintFailure.
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

        # display alternative message if Unit of Measurement is null - this means the user hasn't selected an indicator
        if column == "Unit of Measurement":
            if sheet == "Project Outputs":
                message = (
                    "There are blank cells in column: Unit of Measurement."
                    " Please ensure you have selected valid indicators for all Outputs on the Project Outputs tab,"
                    " and that the Unit of Measurement is correct for this output"
                )
            elif sheet == "Outcomes":
                message = (
                    "There are blank cells in column: Unit of Measurement."
                    " Please ensure you have selected valid indicators for all Outcomes on the Outcomes tab,"
                    " and that the Unit of Measurement is correct for this outcome"
                )
        elif section == "Programme-Wide Progress Summary":
            message = "Do not leave this blank. Use the space provided to tell us the relevant information"

        return sheet, section, message


@dataclass
class WrongInputFailure(PreTransFormationFailure):
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

    def to_message(self) -> tuple[str | None, str | None, str]:
        return None, None, PRETRANSFORMATION_FAILURE_MESSAGE_BANK[self.value_descriptor]


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

    def to_message(self) -> tuple[str | None, str | None, str]:
        raise UnimplementedErrorMessageException


@dataclass
class InvalidOutcomeProjectFailure(ValidationFailure):
    """Class representing an invalid project related to an outcome."""

    invalid_project: str
    section: str

    def __str__(self):
        """Method to get the string representation of the invalid outcome project failure."""
        return (
            f"Invalid Project Failure: The project '{self.invalid_project}' on the sheet "
            f"'6 - Outcomes' selected under the 'Relevant project(s)' header is invalid. "
            f"Please ensure you select all projects from the drop-down provided."
        )

    def to_message(self) -> tuple[str, str, str]:
        sheet = "Outcomes"
        section = self.section
        message = (
            "You must select a project from the drop-down provided for 'Relevant project(s)'. "
            "Do not populate the cell with your own content"
        )

        return sheet, section, message


@dataclass
class UnauthorisedSubmissionFailure(PreTransFormationFailure):
    """Class representing an unauthorised submission failure."""

    unauthorised_place_name: str
    authorised_place_names: tuple[str]

    def __str__(self):
        """Method to get the string representation of the unauthorised submission failure."""
        return (
            f"User is not authorised to submit for {self.unauthorised_place_name}"
            f"User can only submit for {self.authorised_place_names}"
        )

    def to_message(self) -> tuple[str | None, str | None, str]:
        places = ", ".join(self.authorised_place_names)
        message = (
            f"You are not authorised to submit for {self.unauthorised_place_name}. "
            "Please ensure you submit for a place within your local authority. "
            f"You can submit for the following places: {places}"
        )
        return None, None, message


def failures_to_messages(
    validation_failures: list[ValidationFailure],
) -> dict[str, dict[str, list[str]]] | dict[str, dict]:
    """Serialises failures into messages, removing any duplicates, and groups them by tab and section.
    :param validation_failures: validation failure objects
    :return: validation failure messages grouped by tab and section
    """
    # filter and convert to error messages
    error_messages = [failure.to_message() for failure in validation_failures]

    # one pre-transformation failure means payload is entirely pre-transformation failures
    if any(isinstance(failure, PreTransFormationFailure) for failure in validation_failures):
        # ignore tab and section for pre-transformation failures
        return {"PreTransformationErrors": [message for _, _, message in error_messages]}

    # remove duplicate failure messages
    error_messages = list(set(error_messages))
    error_messages.sort()

    # group by tab and section
    failures_grouped_by_tab = group_by_first_element(error_messages)
    failures_grouped_by_tab_and_section = {
        tab: group_by_first_element(failures) for tab, failures in failures_grouped_by_tab.items()
    }
    return {"TabErrors": failures_grouped_by_tab_and_section}
