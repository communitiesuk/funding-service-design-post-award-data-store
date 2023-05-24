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
    extracted_data["df_funding_questions_extracted"] = extract_funding_questions(df_ingest)

    # TODO: Funding DataFrame very large - needs logic to split into DM separate rows
    extracted_data["df_funding_extracted"] = extract_funding_data(df_ingest)

    # Note: No data fields for funding comments in Round 2 data-set
    # Note: No data for PSI in Round 2 data-set

    # TODO: Outputs are all one line per project, need to split into separate line per proj/output combo
    extracted_data["df_outputs_extracted"] = extract_outputs(df_ingest)
    extracted_data["df_outcomes_extracted"] = extract_outcomes(df_ingest)

    return extracted_data


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
    index_1 = "Tab 3 - Programme Progress - Project Progress  Start Date"
    index_2 = "Tab 3 - Programme Progress - Project Progress Commentary"
    df_project_progress = df_data.loc[:, index_1:index_2]
    df_project_progress = join_to_project(df_data, df_project_progress)
    return df_project_progress


def extract_funding_questions(df_input: pd.DataFrame) -> pd.DataFrame:
    """
    Extract funding questions data from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    :param df_input: Input DataFrame containing consolidated data.
    :return: A new DataFrame containing the extracted funding questions.
    """
    index_1 = "Tab 4 - Funding Profiles B - B1 Q1 - TD 5% CDEL Pre-payment"
    index_2 = "Tab 4 - Funding Profiles B - B1 Q6 - Guidance Notes"
    df_funding_questions = df_input.loc[:, index_1:index_2]
    df_funding_questions = join_to_programme(df_input, df_funding_questions)
    df_funding_questions = df_funding_questions.dropna(
        subset=["Tab 4 - Funding Profiles B - B1 Q1 - TD 5% CDEL Pre-payment"]
    )

    return df_funding_questions


def extract_funding_data(df_input: pd.DataFrame) -> pd.DataFrame:
    """
    Extract funding data from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    :param df_input: Input DataFrame containing consolidated data.
    :return: A new DataFrame containing the extracted funding data.
    """
    # TODO: what does the section between columns
    #  "Tab 4 - Funding Profiles B2 CDEL Prog Mngmt - Pre-20/21 H1 - CDEL Prog Mngmt" and
    #  "Tab 4 - Funding Profiles B2  Prog Mngmt Totals - Grand Total - Prog Mngmt Totals"
    #  translate to? There seems to be no matching data in the TF form?

    index_1 = "Tab 4 - Funding Profiles C 1st Row - Pre-20/21 H1 - CDEL Utilised"
    index_2 = "Tab 4 - Funding Profiles C 8th Row - Grand Total - TF Funding Total"
    df_funding = df_input.loc[:, index_1:index_2]
    index_1 = "Tab 4 - Funding Profiles Other Funding Sources 1 -  Funding Source - OFS 1"
    index_2 = "Tab 4 - Funding Profiles Other Funding Sources 28 - Grand Total - OFS 5"
    df_funding = pd.concat([df_funding, df_input.loc[:, index_1:index_2]], axis=1)
    df_funding = join_to_project(df_input, df_funding)
    return df_funding


def extract_outputs(df_input: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Project Output rows from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    :param df_input: Input DataFrame containing consolidated data.
    :return: A new DataFrame containing the extracted outputs data.
    """
    index_1 = "Tab 5 - Project Outputs - Project Name"
    index_2 = "Tab 5 - Project Outputs - Project Specific Custom Output 10 Grand Total"
    df_outputs = df_input.loc[:, index_1:index_2]
    df_outputs = join_to_project(df_input, df_outputs)
    return df_outputs


def extract_outcomes(df_input: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Project Outcome rows from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    Un-flattens project data from 1 row per programme, to 1 row per populated project.

    :param df_input: Input DataFrame containing consolidated data.
    :return: A new DataFrame containing the extracted outcome data.
    """
    index_1 = "Tab 6 - Outcomes: Section B - Outcome 1 - Indicator Name"
    index_2 = "Tab 6 - Outcomes: Section B - Custom Outcome 10 - Higher Frequency"
    df_outcomes = df_input.loc[:, index_1:index_2]
    # joined to programme, as all outcomes returned on first line for each ingest
    df_outcomes = join_to_programme(df_input, df_outcomes)
    # drop irrelevant rows - these contain no actual data
    df_outcomes = df_outcomes.dropna(subset=["Tab 6 - Outcomes: Section B - Outcome 1 - Indicator Name"])
    # headers hard-coded as 10 different sets of header vals in table (150 headers)
    col_headers = [
        "Tab 6 - Outcomes: Section B - Indicator Name",
        "Tab 6 - Outcomes: Section B - Unit of Measurement",
        "Tab 6 - Outcomes: Section B - Relevant Projects ",
        "Tab 6 - Outcomes: Section B - Geography",
        "Tab 6 - Outcomes: Section B - FY 20/21",
        "Tab 6 - Outcomes: Section B - FY 21/22",
        "Tab 6 - Outcomes: Section B - FY 22/23",
        "Tab 6 - Outcomes: Section B - FY 23/24",
        "Tab 6 - Outcomes: Section B - FY 24/25",
        "Tab 6 - Outcomes: Section B - FY 25/26",
        "Tab 6 - Outcomes: Section B - FY 26/27",
        "Tab 6 - Outcomes: Section B - FY 27/28",
        "Tab 6 - Outcomes: Section B  - FY 28/29",
        "Tab 6 - Outcomes: Section B - FY 29/30",
        "Tab 6 - Outcomes: Section B - Higher Frequency",
    ]
    df_outcomes_out = pd.DataFrame()
    for _, flat_row in df_outcomes.iterrows():
        prog_proj_outcomes = pd.DataFrame()
        # TODO: do we actually need programme ref? could possibly drop
        temp_programme = pd.DataFrame().append(
            flat_row.loc["Tab 2 - Project Admin - TD / FHSF":"Tab 2 - Project Admin - Grant Recipient Organisation"]
        )
        # up to 10 projects per row
        for idx in range(0, 10):
            # 15 cols per project "section"
            col_idx = idx * 15
            proj_outcome = pd.DataFrame().append(flat_row.iloc[col_idx + 3 : col_idx + 18])

            # skip iteration if project field is empty
            if not proj_outcome.iloc[:, 2].any():
                continue
            proj_outcome.columns = col_headers
            proj_outcome = pd.concat([temp_programme, proj_outcome], axis=1)
            prog_proj_outcomes = prog_proj_outcomes.append(proj_outcome, ignore_index=True)

        df_outcomes_out = df_outcomes_out.append(prog_proj_outcomes)

    return df_outcomes_out


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
