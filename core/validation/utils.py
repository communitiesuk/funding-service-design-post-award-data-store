from datetime import datetime
from enum import StrEnum
from typing import Any

import pandas as pd

from core.const import (
    FINANCIAL_YEAR_TO_ORIGINAL_COLUMN_LETTER_FOR_NON_FOOTFALL_OUTCOMES,
    MONTH_TO_ORIGINAL_COLUMN_LETTER_FOR_FOOTFALL_OUTCOMES,
)


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


def get_cell_indexes_for_outcomes(failed_row: pd.Series) -> str:
    """
    Constructs cell indexes for outcomes based on the provided failed row.

    The function determines whether the error occurred in footfall outcomes (starting from row 60)
    or non-footfall outcomes. If the index is greater than or equal to 60, it calculates the cell
    index for footfall outcomes based on the provided 'Start_Date'. If the index is less than 60,
    it calculates the cell index for non-footfall outcomes.

    For footfall outcomes, the cell index is determined by adding a row index gap calculated from
    the start year of the UK financial year as each year represents an additional 5 rows in the
    original spreadsheet from the row where the entry for a given footfall outcome's data begins.

    :param failed_row: A pandas Series representing a row where an error has occurred.
    :return: A string containing the constructed cell index for outcomes.
    """
    start_date = failed_row["Start_Date"]
    financial_year = get_uk_financial_year_start(start_date)
    index = failed_row.name

    # footfall outcomes starts from row 60
    if index >= 60:
        # row for 'Amount' column is end number of start year of financial year * 5 + 'Footfall Indicator' index
        row_index_gap = int(str(financial_year)[-1]) * 5
        index = int(index) + row_index_gap
        cell_index = MONTH_TO_ORIGINAL_COLUMN_LETTER_FOR_FOOTFALL_OUTCOMES[start_date.month].format(i=index)
    else:
        cell_index = FINANCIAL_YEAR_TO_ORIGINAL_COLUMN_LETTER_FOR_NON_FOOTFALL_OUTCOMES[financial_year].format(i=index)

    return cell_index


def get_uk_financial_year_start(start_date: datetime) -> int:
    """
    Gets the start year of the UK financial year based on the provided start date.

    :param start_date: A datetime in the format '%Y-%m-%d %H:%M:%S'.
    :return: An integer representing the start year of the UK financial year.
    """

    financial_year = start_date.year if start_date.month >= 4 else start_date.year - 1
    return financial_year
