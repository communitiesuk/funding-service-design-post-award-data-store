from typing import Any

import numpy as np
import pandas as pd

import core.validation.failures as vf
from core.const import (
    EXPECTED_ROUND_THREE_SHEETS,
    GET_FORM_VERSION_AND_REPORTING_PERIOD,
)


def extract_submission_details(
    workbook: dict[str, pd.DataFrame],
    reporting_round: int,
) -> dict[str, list[str]] | dict[str, dict[Any, Any]]:
    """
    Extract submission details from the given workbook.

    :param workbook: A dictionary where keys are sheet names and values are pandas DataFrames.
    :param reporting_round: Integer representing the round being ingested.
    :return: A dictionary containing the extracted submission details.
    """
    details_dict = {"ValueChecks": {}, "NullChecks": {}}

    missing_sheets = check_missing_sheets(EXPECTED_ROUND_THREE_SHEETS, workbook)

    if missing_sheets:
        return {"Missing Sheets": missing_sheets}

    invalid_sheets = []

    form_version, reporting_period = GET_FORM_VERSION_AND_REPORTING_PERIOD[reporting_round]

    sheet_a1 = workbook.get("1 - Start Here")
    sheet_a2 = workbook.get("2 - Project Admin")
    try:
        details_dict["ValueChecks"]["Form Version"] = (
            sheet_a1.iloc[6][1],
            {form_version},
        )
        details_dict["ValueChecks"]["Reporting Period"] = (sheet_a1.iloc[4][1], {reporting_period})
    except IndexError:
        invalid_sheets.append("1 - Start Here")

    try:
        details_dict["ValueChecks"]["Fund Type"] = (sheet_a2.iloc[5][4], {"Town_Deal", "Future_High_Street_Fund"})
        details_dict["NullChecks"]["Place Name"] = sheet_a2.iloc[6][4]
    except IndexError:
        invalid_sheets.append("2 - Project Admin")

    if invalid_sheets:
        return {"Invalid Sheets": missing_sheets}

    return details_dict


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

    failures = []

    for value_descriptor, (entered_value, expected_values) in submission_details["ValueChecks"].items():
        if failure := check_values(value_descriptor, entered_value, expected_values):
            failures.append(failure)

    for value_descriptor, value in submission_details["NullChecks"].items():
        if failure := check_nulls(value_descriptor, value):
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


def check_nulls(value_descriptor: str, value: str) -> vf.NoInputFailure | None:
    """
    Check the form input for pre-transformation failures.

    :param value_descriptor: A string describing the form input value.
    :param value: A string containing the form input value.
    :return: A ValidationFailure object representing the failure, if any.
    """

    if value in ["", np.nan]:
        return vf.NoInputFailure(value_descriptor=value_descriptor)


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
