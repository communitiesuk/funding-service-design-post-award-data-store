import pandas as pd


def remove_unneeded_submission_ids(workbook: dict[str, pd.DataFrame], round: int) -> dict[str, pd.DataFrame]:
    """Removes unneeded submission IDs.

    Project-level data originally retained a Submission ID, but now does not.
    For historical data, much of our extraction functions rely on specific shapes of DataFrames, and locations of
    columns.
    To avoid changing all the extraction and ingestion functions pertaining to project-level data, this functions
    enables us to simply remove the submission ids at the end of the transformation.

    :param workbook: a dictionary of DataFrames
    :param round: an integer representing the round
    :return workbook: the workbook with the submissions ids removed in specified tables
    """
    if round == 1:
        tables_to_remove_from = [
            "Project Progress",
            "Funding",
            "Funding Comments",
        ]
    if round == 2:
        tables_to_remove_from = [
            "Project Progress",
            "Funding",
            "Output_Data",
        ]

    for table in tables_to_remove_from:
        workbook[table] = workbook[table].drop("Submission ID", axis=1)

    return workbook


def add_temp_submission_id_cols(workbook: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """Adds unneeded submission IDs.

    :param workbook: a dictionary of DataFrames
    :return workbook: the workbook with the submissions ids added
    """
    tables_to_add_to = [
        "Project Progress",
        "Funding",
        "Funding Comments",
    ]

    for table in tables_to_add_to:
        workbook[table].insert(0, "Submission ID", "")

    return workbook


def extract_programme_junction(programme_progress: pd.DataFrame, place_details: pd.DataFrame) -> pd.DataFrame:
    """For historical data, the mapping of all Submission IDs to all Programme IDs for a given round can be located in
    a combination of 'Programme Progress' and 'Place Details'.

    Each Submission has a Programme, and each Programme has a project, and therefore the unique combinations of
    'Submission ID' and 'Programme ID' in 'Programme Progress' and 'Place Details' represents every Programme Junction
    entry for Round 1 and Round 2.

    :param programme_progress: a DataFrame containing Programme Progress Data
    :param place_details: a DataFrame containing Place Details Data
    :return programme_junction_df: a DataFrame with all 'Programme ID's mapped to a 'Submission ID'
    """
    programme_junction_df = pd.concat(
        [programme_progress[["Submission ID", "Programme ID"]], place_details[["Submission ID", "Programme ID"]]],
        ignore_index=True,
    )
    programme_junction_df.drop_duplicates(keep="first", inplace=True)
    return programme_junction_df
