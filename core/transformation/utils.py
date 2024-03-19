"""Module for reusable DataFrame transformation functions."""

import re

import numpy as np
import pandas as pd
from pandas.tseries.offsets import MonthEnd

POSTCODE_REGEX = r"[A-Z]{1,2}[0-9][A-Z0-9]? ?[0-9][A-Z]{2}"


def drop_empty_rows(df: pd.DataFrame, column_names: list[str]) -> pd.DataFrame:
    """
    Drop any rows of a dataframe that have entirely empty or unwanted cell values in the given columns.

    Unwanted cell values are:
    - Pandas None types. Usually where empty Excel cells are ingested.
    - Strings with value "< Select >", these are unwanted Excel left-overs

    :param df: The DataFrame to clean.
    :param column_names: The name of the columns to check for unwanted values in.
    :return: Dataframe with removed rows.
    """
    empty_values = ("< Select >", np.nan, None)
    condition = df[column_names].isin(empty_values).all(axis=1)
    df = df[~condition]
    return df


def convert_financial_halves(df: pd.DataFrame, financial_half_col: str) -> pd.DataFrame:
    """
    Converts a column of UK financial halves to corresponding start and end dates.

    Only works for financial periods defined in the format "H1 23/24".
    Also accepts 'Beyond 25/26' or 'Before 20/21' which leaves end date and start date null respectively.
    Other strings that do not match, will return empty dates.
    NOTE: Function does not work with Null/None values in DataFrame Column.

    :param df: DataFrame containing financial periods column.
    :param financial_half_col: The name of the column to be converted.
    :return: The modified DataFrame with added "Start Date" and "End Date" columns.
    """
    # Map of H1 / H2 to partial dates.
    start_dates = {"H1": "04-01", "H2": "10-01", "Before 20/21": np.nan, "Beyond 25/26": "2026-04-01"}
    end_dates = {"H1": "09-30", "H2": "03-31", "Before 20/21": "2020-03-31", "Beyond 25/26": np.nan}

    # insert start date
    df["Start_Date"] = [
        (
            None
            if period is None or period is np.nan
            else (
                "20" + period[3:5] + "-" + start_dates[period[:2]]
                if period[:2] in ["H1", "H2"]
                else start_dates.get(period, None)
            )
        )
        for period in df[financial_half_col]
    ]

    # insert end date
    df["End_Date"] = [
        (
            None
            if period is None or period is np.nan
            else (
                "20" + period[3:5] + "-" + end_dates[period[:2]]
                if period[:2] in ["H1", "H2"]
                else end_dates.get(period, None)
            )
        )
        for period in df[financial_half_col]
    ]
    # convert cols to datetime
    df[["Start_Date", "End_Date"]] = df[["Start_Date", "End_Date"]].apply(pd.to_datetime)

    # Increment end date by 1 year if it's an H2 period
    df["End_Date"] = np.where(
        (df[financial_half_col].str.startswith("H2")), df["End_Date"] + MonthEnd(12), df["End_Date"]
    )

    df = df.drop([financial_half_col], axis=1)
    return df


def datetime_excel_to_pandas(excel_dates_column: pd.Series) -> pd.Series:
    """
    Convert a Pandas Series (Dataframe Column) from Excel Datetime to Python Datetime.

    :param excel_dates_column: Column to convert.
    :return: Column/Series containing datetime objects (or NaT if null)
    """
    # remove null values
    excel_dates_column = excel_dates_column.replace(0, np.nan)
    # Excel timestamp uses days since 1900
    python_dates_column = pd.to_datetime(excel_dates_column, unit="D", origin="1899-12-30")
    return python_dates_column


def extract_postcodes(s: str) -> list[str] | None:
    """Extract postcodes from a string.

    This function uses a regex to extract all postcodes present in a string,
    and returns them as an array if any are present.

    :param s: A string from which postcode areas will be extracted.
    :return: A list of postcode areas extracted from the string.
    """
    if s is np.nan or s == "":
        postcode_area_matches = None
    else:
        postcode_area_matches = re.findall(POSTCODE_REGEX, str(s))

        if postcode_area_matches == []:
            return None
    return postcode_area_matches


def create_dataframe(data: dict[str, pd.Series | list | tuple]) -> pd.DataFrame:
    """
    Creates a DataFrame from a dictionary of Series or lists, aligning the indices. For example:

    create_dataframe({
        "A": pd.Series([1, 2, 3]),
        "B": [4, 5, 6],
        "C": (7, 8, 9),
    })

    Produces a DataFrame with aligned indices:

       A  B  C
    0  1  4  7
    1  2  5  8
    2  3  6  9

    This function exists because if you create a DataFrame directly from a dictionary of Series or lists with different
    indices, the resulting DataFrame will have NaN values where the indices do not align. For example:

    pd.DataFrame({
        "A": pd.Series([1, 2, 3], index=[0, 1, 2]),
        "B": pd.Series([4, 5, 6], index=[3, 4, 5]),
    })

    Produces a DataFrame with NaN values where the indices do not align:

       A   B
    0 1.0 NaN
    1 2.0 NaN
    2 3.0 NaN
    3 NaN 4.0
    4 NaN 5.0
    5 NaN 6.0

    :param data: Dictionary of Series, lists or tuples
    :return: DataFrame with aligned indices
    """
    return pd.DataFrame(
        {
            column: val.reset_index(drop=True) if isinstance(val, pd.Series) else pd.Series(val)
            for column, val in data.items()
        }
    )
