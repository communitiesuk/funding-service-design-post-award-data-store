"""
Methods specifically for extracting data from Round 2 Funding data, historical data spreadsheet.
"""
from typing import Dict

import pandas as pd


def ingest_round_two_data(df_ingest: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Extract data from Consolidated Round 2 data spreadsheet into column headed Pandas DataFrames.

    :param df_ingest: DataFrame of parsed Excel data.
    :return: Dictionary of extracted "tables" as DataFrames
    """
    extracted_data = dict()
    extracted_data["df_place_extracted"] = extract_place_details(df_ingest["December 2022"])


def extract_place_details(df_place: pd.DataFrame) -> pd.DataFrame:
    """
    Extract place detail information from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    :param df_place: Input DataFrame containing data.
    :return: Extracted DataFrame containing place info data.
    """
    df_place = df_place.iloc[:, 10:25].drop_duplicates()
    # TODO: needs transforming / expanding each column into separate questions/answers as per Data Model
    # TODO: Also will need Submission ID, and Programme ID

    return df_place
