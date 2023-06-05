"""Module for reusable DataFrame transformation functions."""
import pandas as pd


def drop_empty_rows(df: pd.DataFrame, column_name: str) -> pd.DataFrame:
    """
    Drop any rows of a dataframe that have empty or unwanted cell values in the given column.

    Unwanted cell values are:
    - Pandas None types. Usually where empty Excel cells are ingested.
    - Strings with value "< Select >", these are unwanted Excel left-overs

    :param df: The DataFrame to clean.
    :param column_name: The name of the column to check for unwanted values in.
    :return: Dataframe with removed rows.
    """
    df = df.dropna(subset=[column_name])
    df.drop(df[df[column_name] == "< Select >"].index, inplace=True)
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
    start_dates = {"H1": "04-01", "H2": "10-01", "Beyond 25/26": "2026-04-01"}
    end_dates = {"H1": "09-30", "H2": "03-31", "Before 20/21": "2020-03-31"}

    # TODO: Falls over here with a None type in dataframe. Potentially needs a fix?
    # hacky fix to insert start date
    df["Start_Date"] = [
        "20" + period[3:5] + "-" + start_dates[period[:2]]
        if period[:2] in ["H1", "H2"]
        else start_dates.get(period, None)
        for period in df[financial_half_col]
    ]

    # super-hacky fix to insert end date including +1 year for end date of H2. (hacked into 1 comp for performance)
    df["End_Date"] = [
        "20" + str(period[(3 * int(period[1])) : (3 * int(period[1])) + 2]) + "-" + end_dates[period[:2]]
        if period[:2] in ["H1", "H2"]
        else end_dates.get(period, None)
        for period in df[financial_half_col]
    ]

    # convert to datetime
    df[["Start_Date", "End_Date"]] = df[["Start_Date", "End_Date"]].apply(pd.to_datetime)
    df = df.drop([financial_half_col], axis=1)
    return df
