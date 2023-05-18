"""
Methods specifically for extracting data from Towns Fund reporting template (Excel Spreadsheet)
"""
import numpy as np
import pandas as pd


def ingest_towns_fund_data(df_ingest: pd.DataFrame) -> dict[pd.DataFrame]:
    """
    Extract data from Towns Fund Reporting Template into column headed Pandas DataFrames.

    :param df_ingest: DataFrame of parsed Excel data.
    :return: Dictionary of extracted "tables" as DataFrames.
    """

    towns_fund_extracted = {"df_package_extracted": extract_package(df_ingest["2 - Project Admin"])}
    towns_fund_extracted["df_projects_extracted"] = extract_project(df_ingest["2 - Project Admin"])
    number_of_projects = len(towns_fund_extracted["df_projects_extracted"].index)

    # risks: cancelled projects show up, with nan cells in their section.
    towns_fund_extracted["df_risks_extracted"] = extract_project_risks(
        df_ingest["7 - Risk Register"], number_of_projects
    )

    return towns_fund_extracted


def extract_package(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts package information from a DataFrame.

    Input dataframe is parsed specifically from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Project work sheet, parsed as dataframe.

    :param df: Input DataFrame containing data.
    :return: Extracted DataFrame containing package data.
    """

    # strip out ecerything other than "SECTION A..." in spreadsheet.
    section_label_start = (df.iloc[:, 1] == "A1").idxmax()
    section_label_end = (df.iloc[:, 1] == "SECTION B: Project Details").idxmax()
    df = df.loc[section_label_start:section_label_end, :].iloc[:-2, 2:5]

    # rename col headers for ease
    df.columns = [0, 1, 2]

    # combine first 2 cols into 1, filling in blank (merged) cells
    field_names_first = [x := y if y is not np.nan else x for y in df[0]]  # noqa: F841,F821
    field_names_combined = ["__".join([x, y]) for x, y in zip(field_names_first, df[1])]

    df[0] = field_names_combined
    df = df.drop(1, axis=1)

    # transpose to "standard" orientation
    df = df.set_index(0).T

    return df


def extract_project(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts project rows from a DataFrame.

    Input dataframe is parsed specifically from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Project work sheet, parsed as dataframe.

    :param df: The input DataFrame containing project data.
    :return: A new DataFrame containing the extracted project rows.
    """

    section_label = (df.iloc[:, 1] == "SECTION B: Project Details").idxmax()
    # strip out everything before section label
    df = df.loc[section_label:, :].iloc[2:, 4:]

    # in first header row, replace empty strings with preceding value.
    header_row_1 = [x := y if y is not np.nan else x for y in df.iloc[0]]  # noqa: F841,F821
    # replace NaN with ""
    header_row_2 = [x := y if y is not np.nan else "" for y in list(df.iloc[1])]  # noqa: F841,F821
    # zip together headers (merged cells)
    header_row_combined = [x + y for x, y in zip(header_row_1, header_row_2)]
    # apply header to df with top rows stripped
    df = pd.DataFrame(df.values[2:], columns=header_row_combined)

    # Find the index of the first row with no "Project Name" and slice the dataframe up to that row
    last_nan_idx = df["Project Name"].isnull().idxmax()
    df = df.iloc[:last_nan_idx]

    return df


def extract_project_risks(df: pd.DataFrame, n_projects: int) -> pd.DataFrame:
    """
    Extracts risk register rows from a DataFrame.

    Input dataframe is parsed specifically from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Risk Register work sheet, parsed as dataframe.

    :param df: The input DataFrame containing project data.
    :param n_projects: The number of projects in this ingest.
    :return: A new DataFrame containing the extracted project/risk rows.
    """
    # TODO: check we definitely don't wan to extract "package/programme risks"
    # strip unwanted border bloat
    df = df.iloc[17:, 2:-1]

    # setup header vals
    risk_header = df.iloc[2, :].tolist()
    risk_header.append("Project Name")
    risk_df = pd.DataFrame(columns=risk_header)

    # iterate through spreadsheet sections and extract relevant rows.
    for idx in range(n_projects):
        line_idx = 8 * idx
        if idx >= 3:
            line_idx += 1  # hacky fix to inconsistent spreadsheet format (extra row at line 42)
        current_project = df.iloc[line_idx, 1]
        project_risks = df.iloc[line_idx + 4 : line_idx + 7]
        project_risks[""] = current_project
        project_risks.columns = risk_header
        risk_df = risk_df.append(project_risks)

    return risk_df
