import numpy as np
import pandas as pd

import core.validation.failures as vf
from core.const import (
    EXPECTED_ROUND_THREE_SHEETS,
    GET_FORM_VERSION_AND_REPORTING_PERIOD,
    TF_PLACE_NAMES_TO_ORGANISATIONS,
)
from core.exceptions import ValidationError


def validate_before_transformation(workbook: dict[str, pd.DataFrame], reporting_round: int, place_names: list[str]):
    """High-level validation of the workbook before transformation.

    :param workbook: a DataFrame containing the extracted contents of the submission
    :param reporting_round: the reporting round
    :param place_names: a list of valid places for this ingest
    :raises: ValidationError: if the workbook fails validation
    :return: the extracted and transformed data from the submission into the data model
    """
    pre_transformation_details = extract_submission_details(
        workbook=workbook, reporting_round=reporting_round, place_names=place_names
    )
    file_validation_failures = pre_transformation_check(pre_transformation_details)
    if reporting_round == 4:
        sign_off_failures = validate_sign_off(workbook)
        file_validation_failures = [*file_validation_failures, *sign_off_failures]
    if file_validation_failures:
        raise ValidationError(validation_failures=file_validation_failures)


def extract_submission_details(
    workbook: dict[str, pd.DataFrame],
    reporting_round: int,
    place_names: list[str] | None,
) -> dict[str, tuple[str]]:
    """
    Extract submission details from the given workbook.

    This function takes a dictionary of sheets from an Excel workbook and a reporting round identifier as input.
    If the sheets are correct, it extracts values from specified cells, and adds these to a tuple alongside
    a set representing the range of values a given cell's value is expected to belong to.

    Keys for each of the value's names are added to a dictionary with the tuples representing actual values and
    expected values as the values in the dictionary.

    :param workbook: A dictionary where keys are sheet names and values are pandas DataFrames.
    :param reporting_round: Integer representing the round being ingested.
    :param place_names: A tuple of place names a given user can submit for.
    :return: A dictionary containing inputs outside expected values for the cell, or
    a list of missing or invalid sheets.
    """
    wrong_input_checks = {}

    missing_sheets = check_missing_sheets(EXPECTED_ROUND_THREE_SHEETS, workbook)

    if missing_sheets:
        return {"Missing Sheets": missing_sheets}

    invalid_sheets = []

    form_version, reporting_period = GET_FORM_VERSION_AND_REPORTING_PERIOD[reporting_round]

    sheet_a1 = workbook.get("1 - Start Here")
    sheet_a2 = workbook.get("2 - Project Admin")
    try:
        wrong_input_checks["Form Version"] = (
            sheet_a1.iloc[6][1],
            {form_version},
        )
        wrong_input_checks["Reporting Period"] = (sheet_a1.iloc[4][1], {reporting_period})
    except IndexError:
        invalid_sheets.append("1 - Start Here")

    try:
        wrong_input_checks["Fund Type"] = (sheet_a2.iloc[5][4], {"Town_Deal", "Future_High_Street_Fund"})
        wrong_input_checks["Place Name"] = (
            sheet_a2.iloc[6][4].strip(),
            set(TF_PLACE_NAMES_TO_ORGANISATIONS.keys()),
        )
    except IndexError:
        invalid_sheets.append("2 - Project Admin")

    if invalid_sheets:
        return {"Invalid Sheets": missing_sheets}

    # if None, then user is submitting via API
    if reporting_round == 4 and place_names is not None:
        # check if the place name is valid but unauthorised so the error is not mistaken for a WrongInputFailure
        if (
            wrong_input_checks["Place Name"][0] not in place_names
            and wrong_input_checks["Place Name"][0] in TF_PLACE_NAMES_TO_ORGANISATIONS.keys()
        ):
            return {"Unauthorised Place Name": (wrong_input_checks["Place Name"][0], place_names)}

    return wrong_input_checks


def pre_transformation_check(submission_details: dict[str, dict[str, dict]]) -> list[vf.ValidationFailure]:
    """
    Perform pre-transformation checks on the given workbook.

    :param submission_details: A dictionary containing submission details.
    :return: A list of validation failures encountered during pre-transformation checks.
    """

    if missing_sheets := submission_details.get("Missing Sheets"):
        return [vf.EmptySheetFailure(empty_sheet) for empty_sheet in missing_sheets]

    if invalid_sheets := submission_details.get("Invalid Sheets"):
        return [vf.InvalidSheetFailure(invalid_sheet) for invalid_sheet in invalid_sheets]

    if place_names := submission_details.get("Unauthorised Place Name"):
        unauthorised_place_name, authorised_place_names = place_names
        return [vf.UnauthorisedSubmissionFailure(unauthorised_place_name, authorised_place_names)]

    failures = []

    for value_descriptor, (entered_value, expected_values) in submission_details.items():
        if failure := check_values(value_descriptor, entered_value, expected_values):
            failures.append(failure)

    return failures


def check_values(value_descriptor: str, entered_value: str, expected_values: set) -> vf.WrongInputFailure | None:
    """
    Check the form input for pre-transformation failures.

    :param value_descriptor: A string describing the form input value.
    :param entered_value: A string containing the entered value
    :param expected_values: A set containing the set of expected values.
    :return: A ValidationFailure object representing the failure, if any.
    """

    if entered_value not in expected_values:
        return vf.WrongInputFailure(
            value_descriptor=value_descriptor, entered_value=entered_value, expected_values=expected_values
        )


def check_missing_sheets(expected_sheets: list[str], workbook: dict[str, pd.DataFrame]) -> list[str]:
    """
    Check for missing sheets in the workbook.

    :param expected_sheets: A list of expected sheet names.
    :param workbook: A dictionary where keys are sheet names and values are pandas DataFrames.
    :return: A list of missing sheets.
    """
    missing_sheets = []
    for sheet in expected_sheets:
        if workbook.get(sheet) is None or workbook.get(sheet).empty:
            missing_sheets.append(sheet)

    return missing_sheets


def validate_sign_off(workbook: dict[str, pd.DataFrame]) -> list[vf.SignOffFailure] | None:
    """Validates Name, Role, and Date for the Review & Sign-Off Section

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    sheet = workbook["8 - Review & Sign-Off"]
    sheet.replace(r"", np.nan, inplace=True)

    section_151_text_cells = [6, 7, 9]
    town_board_chair_cells = [13, 14, 16]

    failures = []

    for y_axis in section_151_text_cells:
        if pd.isnull(sheet.iloc[y_axis, 2]):
            failures.append(
                vf.SignOffFailure(
                    tab="Review & Sign-Off",
                    section="Section 151 Officer / Chief Finance Officer",
                    missing_value=str(sheet.iloc[y_axis, 1]).strip(),
                    sign_off_officer="an S151 Officer or Chief Finance Officer",
                )
            )

    for y_axis in town_board_chair_cells:
        if pd.isnull(sheet.iloc[y_axis, 2]):
            failures.append(
                vf.SignOffFailure(
                    tab="Review & Sign-Off",
                    section="Town Board Chair",
                    missing_value=str(sheet.iloc[y_axis, 1]).strip(),
                    sign_off_officer="a programme SRO",
                )
            )

    return failures
