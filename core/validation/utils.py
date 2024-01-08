from datetime import datetime
from enum import StrEnum
from typing import Any

import pandas as pd

from core.validation.const import NA_VALUES


def remove_duplicate_indexes(df: pd.DataFrame):
    """Removes duplicate indexes, except the first instance.

    Due to the pd.melt during transformation that maps a single spreadsheet row to multiple df rows, here we just keep
    the first of each unique index (this refers to the spreadsheet row number). This ensures we only produce one error
    for a single incorrect row in the spreadsheet.

    :param df: a DataFrame
    :return: the DataFrame without duplicate indexes
    """
    return df[~df.index.duplicated(keep="first")]


def numeric_eval(value: Any) -> int | float | Any:
    """Evaluate value as an int or float. If impossible, return the original value.

    :param value: any value
    :return: the value as an int or a float
    :raises ValueError: if value cannot be evaluated as an int or a float
    """
    try:
        return int(value)
    except ValueError:
        return float(value)


def is_numeric(value: Any) -> bool:
    """Returns True if the value is numerical, otherwise False.

    :param value: value to check is numerical
    :return: True if numerical, else False
    """
    try:
        numeric_eval(value)
        return True
    except ValueError:
        return False


def is_blank(value: Any):
    """Returns True if the value is blank, otherwise False.

    Blank cells will produce either pd.NA or an empty string cell.

    :param value: value to check is blank
    :return: True if blank, else False
    """
    return pd.isna(value) or str(value) == ""


def is_from_dropdown(value: Any, dropdown_enum: StrEnum) -> bool:
    """Returns True if the value is from the dropdown, otherwise False.

    :param value: value to check is blank
    :param dropdown_enum: enum representing the dropdown options
    :return: True if blank, else False
    """
    return value in {dropdown_value for dropdown_value in dropdown_enum}


def get_uk_financial_year_start(start_date: datetime) -> int:
    """
    Gets the start year of the UK financial year based on the provided start date.

    :param start_date: A datetime in the format '%Y-%m-%d %H:%M:%S'.
    :return: An integer representing the start year of the UK financial year.
    """

    financial_year = start_date.year if start_date.month >= 4 else start_date.year - 1
    return financial_year


def find_null_values(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Helper function to find rows with null values in a specified column.

    :param df: DataFrame to search for invalid rows.
    :param column: Column name to check for null values.
    :return: DataFrame containing rows with null values in the specified column.
    """
    return df[df[column].isin(NA_VALUES)]
