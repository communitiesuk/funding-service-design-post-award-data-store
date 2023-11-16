"""This module defines a set of classes representing different types of validation
failures that can occur while validating a Workbook.

All the below classes are defined as dataclasses with appropriate attributes and methods
to represent the corresponding validation failures.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass

import pandas as pd

from core.const import (
    INTERNAL_COLUMN_TO_FORM_COLUMN_AND_SECTION,
    INTERNAL_TABLE_TO_FORM_TAB,
    INTERNAL_TYPE_TO_MESSAGE_FORMAT,
    TABLE_AND_COLUMN_TO_ORIGINAL_COLUMN_LETTER,
)
from core.extraction.utils import join_as_string
from core.util import get_project_number_by_position
from core.validation import messages as msgs
from core.validation.exceptions import UnimplementedErrorMessageException
from core.validation.utils import get_cell_indexes_for_outcomes


class ValidationFailureMixin(ABC):
    pass


class UserValidationFailure(ValidationFailureMixin, ABC):
    """ABC for User Failures. Concrete classes must implement to_message()."""

    @abstractmethod
    def to_message(self) -> tuple[str | None, str | None, str, str | None]:
        """Abstract method - implementations of this return message components.

        :return: A tuple containing the sheet, subsection, cell index and the message itself.
        """
        pass


@dataclass
class SchemaUserValidationFailure(UserValidationFailure, ABC):
    """ABC for User Failures raised during schema validation. Concrete classes use the attributes defined here."""

    sheet: str
    column: str | list[str]
    row_index: int


@dataclass
class GenericFailure(UserValidationFailure):
    """A generic failure that is instantiated with all to_message() return values.

    Raised with all the context needed to display straight to the user.
    Generic in the sense that it is not specific to a round or type of validation.
    """

    sheet: str
    section: str
    cell_index: str
    message: str

    def __str__(self):
        pass

    def to_message(self) -> tuple[str, str, str, str]:
        return self.sheet, self.section, self.cell_index, self.message


@dataclass
class NonUniqueCompositeKeyFailure(SchemaUserValidationFailure):
    """Class representing a non-unique-composite_key failure that is raised due to duplicate data."""

    row: list

    def __str__(self):
        """Method to get the string representation of the non-unique-composite_key failure."""
        cols_str = join_as_string(self.column)
        row_str = list(self.row)
        return (
            f'Non Unique Row Failure: Sheet "{self.sheet}"; '
            f'Columns "{cols_str}" contains contains a duplicate row consisting of the values: '
            f'"{row_str}"'
        )

    def to_message(self) -> tuple[str, str, str, str]:
        """Generate user-centered components for NonUniqueCompositeKeyFailure.

        This function returns user-centered components in the case of a NonUniqueCompositeKeyFailure.
        When a Unique combination of cell values is required on separate row to act as composite keys this function
        will return a message. The function distinguishes between Funding profiles, Outputs, Outcomes, and Risk Register
        and displays an appropriate message.

        return: tuple[str, str, str]: A tuple containing the sheet name, section, and error message.
        """
        sheet = INTERNAL_TABLE_TO_FORM_TAB[self.sheet]
        message = msgs.DUPLICATION

        if sheet == "Funding Profiles":
            project_number = get_project_number_by_position(self.row_index, self.sheet)
            section = f"Funding Profiles - Project {project_number}"
        elif sheet == "Project Outputs":
            project_number = get_project_number_by_position(self.row_index, self.sheet)
            section = f"Project Outputs - Project {project_number}"
        elif sheet == "Outcomes":
            section = "Outcome Indicators (excluding footfall)"
        elif sheet == "Risk Register":
            project_id = self.row[1]
            section = risk_register_section(project_id, self.row_index, self.sheet)
        else:
            raise UnimplementedErrorMessageException

        # TODO: Can we return a Failure for each column separately and let them be joined together downstream
        cell_index = ", ".join(
            construct_cell_index(table=self.sheet, column=column, row_index=self.row_index)
            for column in self.column
            if column
            not in [
                "Project ID",
                "Programme ID",
                "Start_Date",
                "End_Date",
                "Actual/Forecast",
            ]  # these columns do not translate to the spreadsheet
        )

        return sheet, section, cell_index, message


@dataclass
class WrongTypeFailure(SchemaUserValidationFailure):
    """Class representing a wrong type failure that is raised when data is of an incorrect type."""

    expected_type: str
    actual_type: str
    failed_row: pd.Series | None

    def __str__(self):
        """Method to get the string representation of the wrong type failure."""
        return (
            f'Wrong Type Failure: Sheet "{self.sheet}" column "{self.column}" expected '
            f'type "{self.expected_type}", got type "{self.actual_type}"'
        )

    def to_message(self) -> tuple[str, str, str, str]:
        sheet = INTERNAL_TABLE_TO_FORM_TAB[self.sheet]
        _, section = INTERNAL_COLUMN_TO_FORM_COLUMN_AND_SECTION[self.column]
        actual_type = INTERNAL_TYPE_TO_MESSAGE_FORMAT[self.actual_type]
        cell_index = construct_cell_index(table=self.sheet, column=self.column, row_index=self.row_index)

        if sheet == "Outcomes":
            _, section = "Financial Year 2022/21 - Financial Year 2029/30", (
                "Outcome Indicators (excluding " "footfall) and Footfall Indicator"
            )
            cell_index = get_cell_indexes_for_outcomes(self.failed_row)

        if self.expected_type == "datetime64[ns]":
            message = msgs.WRONG_TYPE_DATE.format(wrong_type=actual_type)
        elif sheet == "PSI":
            message = msgs.WRONG_TYPE_CURRENCY
        elif sheet == "Funding Profiles":
            message = msgs.WRONG_TYPE_CURRENCY
        elif sheet in ["Project Outputs", "Outcomes"]:
            message = msgs.WRONG_TYPE_NUMERICAL
        else:
            message = msgs.WRONG_TYPE_UNKNOWN

        return sheet, section, cell_index, message


@dataclass
class InvalidEnumValueFailure(SchemaUserValidationFailure):
    """Class representing an invalid enum value failure raised when dropdown values have not been used."""

    row_values: tuple

    def to_message(self) -> tuple[str, str, str, str]:
        sheet = INTERNAL_TABLE_TO_FORM_TAB[self.sheet]
        column, section = INTERNAL_COLUMN_TO_FORM_COLUMN_AND_SECTION[self.column]
        message = msgs.DROPDOWN

        # additional logic for outcomes to differentiate between footfall and non-footfall
        if sheet == "Outcomes" and self.row_values[4] == "Year-on-year % change in monthly footfall":
            section = "Footfall Indicator"
            # +5 as GeographyIndicator is 5 rows below Footfall Indicator
            if column == "Geography Indicator":
                actual_index = self.row_index + 5
                cell = f"C{actual_index}"
                return sheet, section, cell, message

        # additional logic for risk location
        if sheet == "Risk Register":
            project_id = self.row_values[1]
            section = risk_register_section(project_id, self.row_index, self.sheet)

        if section == "Project Funding Profiles":
            project_number = get_project_number_by_position(self.row_index, self.sheet)
            section = f"Project Funding Profiles - Project {project_number}"

        cell_index = construct_cell_index(table=self.sheet, column=self.column, row_index=self.row_index)

        return sheet, section, cell_index, message


@dataclass
class NonNullableConstraintFailure(SchemaUserValidationFailure):
    """Class representing a non-nullable constraint failure raised when a required cell is left blank."""

    failed_row: pd.Series | None

    def to_message(self) -> tuple[str, str, str, str]:
        """Generate error message components for NonNullableConstraintFailure.

        This function returns error message components in the case of a NonNullableConstraintFailure.
        In instances where the Unit of Measurement is null, a distinct error message is necessary.
        The function distinguishes between Outputs and Outcomes and adjusts the error message accordingly.

        return: tuple[str, str, str]: A tuple containing the sheet name, section, and error message.
        """
        sheet = INTERNAL_TABLE_TO_FORM_TAB[self.sheet]
        column, section = INTERNAL_COLUMN_TO_FORM_COLUMN_AND_SECTION[self.column]

        cell_index = construct_cell_index(table=self.sheet, column=self.column, row_index=self.row_index)

        message = msgs.BLANK
        if sheet == "Project Outputs":
            if column == "Unit of Measurement":
                message = msgs.BLANK_UNIT_OF_MEASUREMENT
            if column == "Financial Year 2022/21 - Financial Year 2025/26":
                message = msgs.BLANK_ZERO
        elif sheet == "Outcomes":
            if column == "Unit of Measurement":
                message = msgs.BLANK_UNIT_OF_MEASUREMENT
            if column == "Financial Year 2022/21 - Financial Year 2025/26":
                section = "Outcome Indicators (excluding footfall) / Footfall Indicator"
                message = msgs.BLANK_ZERO
                cell_index = get_cell_indexes_for_outcomes(self.failed_row)
        elif sheet == "Funding Profiles":
            message = msgs.BLANK_ZERO
        elif section == "Programme-Wide Progress Summary":
            message = msgs.BLANK

        return sheet, section, cell_index, message


class PreTransFormationFailure(UserValidationFailure, ABC):
    pass


@dataclass
class WrongInputFailure(PreTransFormationFailure):
    """Class representing a wrong input pre-transformation failure."""

    value_descriptor: str
    entered_value: str
    expected_values: set

    def to_message(self) -> tuple[str | None, str | None, str]:
        return None, None, msgs.PRE_TRANSFORMATION_MESSAGES[self.value_descriptor]


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
        places = join_as_string(self.authorised_place_names)
        message = msgs.UNAUTHORISED.format(wrong_place=self.unauthorised_place_name, allowed_places=places)
        return None, None, message


def risk_register_section(project_id, row_index, sheet):
    if pd.notna(project_id):
        # project risk
        project_number = get_project_number_by_position(row_index, sheet)
        section = f"Project Risks - Project {project_number}"
    else:
        # programme risk
        section = "Programme Risks"
    return section


def failures_to_messages(
    validation_failures: list[UserValidationFailure],
) -> dict[str, list[str]] | dict[str, list[dict[str, str | None]]]:
    """Serialises failures into messages, removing any duplicates, and groups them by tab and section.
    :param validation_failures: validation failure objects
    :return: validation failure messages grouped by tab and section and list of error types
    """
    # filter and convert to error messages
    error_messages = [failure.to_message() for failure in validation_failures]
    error_types = [failure.__class__.__name__ for failure in validation_failures]

    # one pre-transformation failure means payload is entirely pre-transformation failures
    if any(isinstance(failure, PreTransFormationFailure) for failure in validation_failures):
        # ignore tab and section for pre-transformation failures
        return {"pre_transformation_errors": [message for _, _, message in error_messages]}

    error_messages = remove_errors_already_caught_by_null_failure(error_messages)
    # remove duplicates resulting from melted rows where we are unable to remove duplicates at time of validation
    error_messages = list(set(error_messages))

    # group cells by sheet, section and desc
    error_messages = group_validation_messages(error_messages)
    error_messages.sort()
    validation_errors = [
        {"sheet": sheet, "section": section, "cell_index": cell_index, "description": message}
        for sheet, section, cell_index, message in error_messages
    ]

    return {"validation_errors": validation_errors, "error_types": error_types}


def group_validation_messages(validation_messages: list[tuple[str, str, str, str]]) -> list[tuple[str, str, str, str]]:
    """Groups validation messages by concatenating the cell indexes together on identical sheet, section and description

    :param validation_messages: a list of tuples representing validation messages: sheet, section, description, cell
    :return: grouped validation messages
    """
    grouped_dict = {}
    for sheet, section, cell, desc in validation_messages:
        key = (sheet, section, desc)  # use sheet, section and description as the key
        value = cell  # use the cell index as the value
        if key in grouped_dict:
            grouped_dict[key].append(value)  # collect cells to concatenate
        else:
            grouped_dict[key] = [value]

    grouped_messages = [
        (sheet, section, ", ".join(sorted(cells)), desc) for (sheet, section, desc), cells in grouped_dict.items()
    ]

    return grouped_messages


def construct_cell_index(table: str, column: str, row_index: int) -> str:
    """Constructs the index of an error from the column and row it occurred in.

    :param table: the internal table name where the error occurred
    :param column: the internal column name where the error occurred
    :param row_index: a row index where the error occurred
    :return: indexes tuple of constructed letter and number indexes
    """
    column_letter = TABLE_AND_COLUMN_TO_ORIGINAL_COLUMN_LETTER[table][column]
    return column_letter.format(i=row_index)


def remove_errors_already_caught_by_null_failure(
    errors: list[tuple[str, str, str, str]]
) -> list[tuple[str, str, str, str]]:
    """
    Removes errors from the list that have already been caught by null failures based on their sheet, section, and
    cell index, and keeps only those present in null_failures. Additionally, includes all null_failures and errors
    not present in null_failures or any part of the cell index is not already captured by a null failure.

    :param errors: List of error tuples (sheet, section, cell_index, message).
    :return: Filtered list of errors, including all null_failures and errors not present in null_failures or any part
    of the cell index is not already captured by a null failure.
    """

    def normalise_risk_section_name(section):
        if "Risks" in section:
            return "Project / Programme Risks"
        return section

    null_messages = [msgs.BLANK, msgs.BLANK_ZERO, msgs.BLANK_PSI, msgs.BLANK_UNIT_OF_MEASUREMENT]

    null_failures = [
        (sheet, section, cell_index.strip(), message)
        for sheet, section, cell_index, message in errors
        if message in null_messages
    ]

    unique_identifiers_from_null_failures = {
        (sheet, normalise_risk_section_name(section), cell_index.strip())
        for sheet, section, cell_index, _ in null_failures
        for cell_index in cell_index.split(",")
    }

    filtered_errors = [
        error
        for error in errors
        if not any(
            ((sheet, normalise_risk_section_name(section), cell_index.strip()) in unique_identifiers_from_null_failures)
            for sheet, section, cell_index, _ in [error]
            for cell_index in error[2].split(",")
        )
    ]

    filtered_errors.extend(null_failures)

    return filtered_errors
