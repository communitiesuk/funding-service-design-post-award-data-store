"""
Methods specifically for extracting data from Round 2 Funding data, historical data spreadsheet.
"""
from typing import Dict

import pandas as pd


def ingest_round_two_data(df_ingest: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Extract data from Consolidated Round 2 data spreadsheet into column headed Pandas DataFrames.

    :param df_ingest: DataFrame of parsed Excel data - specifically sheet "December 2022"
    :return: Dictionary of extracted "tables" as DataFrames
    """
    # TODO convert Excel datetimes to Python, preferably on ingest of initial DataFrame, but might have to
    #  do on specific columns to avoid false-postives

    # TODO: Do we need to extract any data from any other tabs?
    extracted_data = dict()
    extracted_data["df_place_extracted"] = extract_place_details(df_ingest)
    extracted_data["df_projects_extracted"] = extract_project(df_ingest)
    extracted_data["df_programme_progress_extracted"] = extract_programme_progress(df_ingest)
    # Round 2, project progress data missing "Most Important Upcoming Comms Milestone" columns
    extracted_data["df_project_progress_extracted"] = extract_project_progress(df_ingest)


def extract_place_details(df_place: pd.DataFrame) -> pd.DataFrame:
    """
    Extract place detail information from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    :param df_place: Input DataFrame containing consolidated data.
    :return: Extracted DataFrame containing place info data.
    """
    df_place = df_place.iloc[:, 10:25].drop_duplicates()
    # TODO: needs transforming / expanding each column into separate questions/answers as per Data Model
    # TODO: Also will need Submission ID - possibly create based on input file name
    #  , and Programme ID

    return df_place


def extract_project(df_data: pd.DataFrame) -> pd.DataFrame:
    """
    Extract project rows from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    :param df_project: Input DataFrame containing consolidated data.
    :return: A new DataFrame containing the extracted project rows.
    """
    df_project = df_data.loc[
        :, "Tab 2 - Project Admin - Index Codes":"Tab 2 - Project Admin - Correct Project Names Info"
    ]
    df_project = join_to_programme(df_data, df_project)
    return df_project


def extract_programme_progress(df_data: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Programme progress questions/answers from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    :param df_data: Input DataFrame containing consolidated data.
    :return: A new DataFrame containing the extracted programme progress rows.
    """
    # slice only relevant columns
    df_programme_progress = df_data.loc[
        :, "Tab 3 - Programme Progress - Programme Progress  A1":"Tab 3 - Programme Progress - Programme Progress  A7"
    ]
    df_programme_progress = join_to_programme(df_data, df_programme_progress)
    df_programme_progress = df_programme_progress.dropna(subset=["Tab 3 - Programme Progress - Programme Progress  A1"])
    return df_programme_progress


def extract_project_progress(df_data: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Project progress rows from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    :param df_data: Input DataFrame containing consolidated data.
    :return: A new DataFrame containing the extracted project progress rows.
    """
    df_project_progress = df_data.loc[
        :,
        "Tab 3 - Programme Progress - Project Progress  Start Date":"Tab 3 - Programme Progress - Project Progress Commentary",  # noqa: E501
    ]
    df_project_progress = join_to_project(df_data, df_project_progress)
    return df_project_progress


# assuming this slice of 3 cols is the most suitable to identify programme by
def join_to_programme(df_data: pd.DataFrame, df_to_join) -> pd.DataFrame:
    """
    Extract just the columns that identify a programme instance and join these to given subset of columns.

    :param df_data: Input DataFrame containing consolidated data.
    :param df_to_join: DataFrame containing only columns to join with Programme identifiers.
    :return: DataFrame joined with the 3 identifier rows for a Programme.
    """

    df_prog_id = df_data.loc[
        :, "Tab 2 - Project Admin - TD / FHSF":"Tab 2 - Project Admin - Grant Recipient Organisation"
    ]
    df_joined = pd.concat([df_prog_id, df_to_join], axis=1)
    return df_joined


# assuming this slice of 3 cols is the most suitable to identify programme by
def join_to_project(df_data: pd.DataFrame, df_to_join) -> pd.DataFrame:
    """
    Extract just the columns that identify a project instance and join these to given subset of columns.

    :param df_data: Input DataFrame containing consolidated data.
    :param df_to_join: DataFrame containing only columns to join with Project identifiers.
    :return: DataFrame joined with the 2 identifier rows for a Programme.
    """

    df_prog_id = df_data.loc[:, "Tab 2 - Project Admin - Index Codes":"Tab 2 - Project Admin - Project Name"]
    df_joined = pd.concat([df_prog_id, df_to_join], axis=1)
    return df_joined
