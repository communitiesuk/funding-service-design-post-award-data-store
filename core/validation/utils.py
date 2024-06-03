from enum import StrEnum
from typing import Any, Type

import numpy as np
import pandas as pd


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


def is_from_dropdown(value: Any, dropdown_enum: Type[StrEnum]) -> bool:
    """Returns True if the value is from the dropdown, otherwise False.

    :param value: value to check is blank
    :param dropdown_enum: enum representing the dropdown options
    :return: True if blank, else False
    """
    return value in {dropdown_value for dropdown_value in dropdown_enum}


def find_null_values(df: pd.DataFrame, column: str) -> pd.DataFrame:
    """
    Helper function to find rows with null values in a specified column.

    :param df: DataFrame to search for invalid rows.
    :param column: Column name to check for null values.
    :return: DataFrame containing rows with null values in the specified column.
    """
    na_values = {"", np.nan, None, pd.NA, pd.NaT}
    return df[df[column].isin(na_values)]
