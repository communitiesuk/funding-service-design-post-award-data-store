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

    towns_fund_extracted = {"df_programme_extracted": extract_programme(df_ingest["2 - Project Admin"])}
    towns_fund_extracted["df_projects_extracted"] = extract_project(df_ingest["2 - Project Admin"])
    number_of_projects = len(towns_fund_extracted["df_projects_extracted"].index)
    towns_fund_extracted["df_programme_progress_extracted"] = extract_programme_progress(
        df_ingest["3 - Programme Progress"]
    )
    towns_fund_extracted["df_project_progress_extracted"] = extract_project_progress(
        df_ingest["3 - Programme Progress"]
    )

    # TODO: Funding questions -> cartesian product of rows vs columns (mainly) in section B of form. Medium
    # TODO: Funding comments -> One row from each project section (dynamically generated). Easy-medium
    # TODO: Funding -> 5 lines per project section. Concatenating headers. Medium.

    towns_fund_extracted["df_psi_extracted"] = extract_psi(df_ingest["4b - PSI"])

    towns_fund_extracted["df_outputs_extracted"] = extract_outputs(df_ingest["5 - Project Outputs"], number_of_projects)
    towns_fund_extracted["df_outcomes_extracted"] = extract_outcomes(df_ingest["6 - Outcomes"])

    # separated from "outcomes" as these are in a different format, with greater date period granularity
    towns_fund_extracted["df_outcomes_footfall_extracted"] = extract_footfall_outcomes(df_ingest["6 - Outcomes"])
    towns_fund_extracted["df_programme_risks_extracted"] = extract_programme_risks(df_ingest["7 - Risk Register"])

    # risks: cancelled projects show up, with nan cells in their section.
    towns_fund_extracted["df_project_risks_extracted"] = extract_project_risks(
        df_ingest["7 - Risk Register"], number_of_projects
    )

    return towns_fund_extracted


def extract_programme(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract package information from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Project work sheet, parsed as dataframe.

    :param df: Input DataFrame containing data.
    :return: Extracted DataFrame containing programme data.
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
    df = df.reset_index(drop=True)
    return df


def extract_project(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract project rows from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
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
    header_row_2 = [field if field is not np.nan else "" for field in list(df.iloc[1])]
    # zip together headers (merged cells)
    header_row_combined = ["__".join([x, y]).rstrip("_") for x, y in zip(header_row_1, header_row_2)]
    # apply header to df with top rows stripped
    df = pd.DataFrame(df.values[2:], columns=header_row_combined)

    # Find the index of the first row with no "Project Name" and slice the dataframe up to that row
    last_nan_idx = df["Project Name"].isnull().idxmax()
    df = df.iloc[:last_nan_idx]

    return df


def extract_programme_progress(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Programme progress questions/answers from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Programme Progress work sheet, parsed as dataframe.

    :param df: The input DataFrame containing progress data.
    :return: A new DataFrame containing the extracted programme progress rows.
    """
    df = df.iloc[5:12, 2:4]
    df.columns = ["Question", "Answer"]
    df = df.reset_index(drop=True)
    return df


def extract_project_progress(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Project progress rows from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Programme Progress work sheet, parsed as dataframe.

    :param df: The input DataFrame containing project data.
    :return: A new DataFrame containing the extracted project progress rows.
    """
    df = df.iloc[17:38, 2:13]
    df = df.rename(columns=df.iloc[0]).iloc[1:]
    df = drop_empty_rows(df, "Project name")
    df = df.reset_index(drop=True)
    return df


def extract_psi(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Project PSI rows from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically PSI work sheet, parsed as dataframe.

    :param df: The input DataFrame containing project data.
    :return: A new DataFrame containing the extracted PSI rows.
    """
    df = df.iloc[10:31, 3:]
    df = df.rename(columns=df.iloc[0]).iloc[1:]
    df = drop_empty_rows(df, "Project name")
    df = df.reset_index(drop=True)
    return df


def extract_programme_risks(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Programme specific risk register rows from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Risk Register work sheet, parsed as dataframe.

    :param df: The input DataFrame containing risk data.
    :return: A new DataFrame containing the extracted programme/risk rows.
    """
    df = df.iloc[8:13, 2:-1]
    df = df.rename(columns=df.iloc[0]).iloc[2:]
    df = df.reset_index(drop=True)
    return df


def extract_project_risks(df: pd.DataFrame, n_projects: int) -> pd.DataFrame:
    """
    Extract Project specific risk register rows from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Risk Register work sheet, parsed as dataframe.

    :param df: The input DataFrame containing risk data.
    :param n_projects: The number of projects in this ingest.
    :return: A new DataFrame containing the extracted project/risk rows.
    """
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

    risk_df = risk_df.reset_index(drop=True)
    return risk_df


def extract_outputs(df: pd.DataFrame, n_projects: int) -> pd.DataFrame:
    """
    Extract Project Output rows from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Projects Outputs work sheet, parsed as dataframe.

    :param df: The input DataFrame containing output data.
    :param n_projects: The number of projects in this ingest.
    :return: A new DataFrame containing the extracted project output rows.
    """

    df = df.iloc[14:, 2:-1]

    # construct header rows out of 3 rows (merged cells), and add to empty init dataframe
    header_row_1 = [x := y if y is not np.nan else x for y in df.iloc[3]]  # noqa: F841,F821
    header_row_2 = [field if field is not np.nan else "" for field in list(df.iloc[5])]
    header_row_3 = [field if field is not np.nan else "" for field in list(df.iloc[6])]
    header_row_combined = [
        "__".join([x, y, z]).rstrip("_") for x, y, z in zip(header_row_1, header_row_2, header_row_3)
    ]
    header_row_combined.append("Project Name")
    outputs_df = pd.DataFrame(columns=header_row_combined)

    # iterate over project sections, based on number of projects.
    for idx in range(n_projects):
        line_idx = 38 * idx

        if idx >= 1:  # hacky fix to allow for hidden line part way through section for project 1
            line_idx += 1

        current_project = df.iloc[line_idx, 0].split(": ")[1]

        if idx >= 1:  # hacky fix to allow for hidden line part way through section for project 1
            line_idx -= 1

        # combine extracted sections for each sub-table, add column headers
        project_outputs = (
            df.iloc[line_idx + 8 : line_idx + 11]
            .append(df.iloc[line_idx + 12 : line_idx + 27])
            .append(df.iloc[line_idx + 28 : line_idx + 38])
        )
        project_outputs[""] = current_project
        project_outputs.columns = header_row_combined

        project_outputs = drop_empty_rows(project_outputs, "Indicator Name")

        outputs_df = outputs_df.append(project_outputs)

    outputs_df = outputs_df.reset_index(drop=True)
    return outputs_df


def extract_outcomes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Outcome rows from a DataFrame.

    This includes all Outputs except "Footfall Indicator" (extracted separately)

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Projects Outputs work sheet, parsed as dataframe.

    :param df: The input DataFrame containing outcomes data.
    :return: A new DataFrame containing the extracted project outcome rows.
    """
    df = df.iloc[14:, 1:]

    header_row_1 = [field for field in df.iloc[0]]
    header_row_2 = [field if field is not np.nan else "" for field in list(df.iloc[1])]
    header_row_combined = ["__".join([x, y]).rstrip("_") for x, y in zip(header_row_1, header_row_2)]

    outcomes_df = pd.DataFrame(df.values[6:26], columns=header_row_combined)
    outcomes_df = outcomes_df.append(pd.DataFrame(df.values[27:37], columns=header_row_combined))
    outcomes_df = drop_empty_rows(outcomes_df, "Indicator Name")

    outcomes_df = outcomes_df.reset_index(drop=True)
    return outcomes_df


def extract_footfall_outcomes(df: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Footfall specific Outcome rows from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Projects Outputs work sheet, parsed as dataframe.

    :param df: The input DataFrame containing outcome data.
    :return: A new DataFrame containing the extracted footfall outcome rows.
    """
    df = df.iloc[52:, 1:]

    # Build the header. It is very long, and calculated dynamically, as the values are dynamically generated in Excel
    header = [field for field in df.iloc[2, :2].append(df.iloc[7, :2])]

    # within each footfall section data/header is spread over 6 lines, each 5 cells apart
    for year_idx in range(0, 30, 5):
        header_monthly_row_1 = [
            x := y if y is not np.nan else x for y in df.iloc[(year_idx + 2), 2:-1]  # noqa: F841,F821
        ]
        header_monthly_row_2 = [str(field) for field in df.iloc[(year_idx + 4), 2:-1]]
        header_monthly_row_3 = [field for field in df.iloc[(year_idx + 5), 2:-1]]
        header_monthly_combined = [
            "__".join([x, y, z]).rstrip("_")
            for x, y, z in zip(header_monthly_row_1, header_monthly_row_2, header_monthly_row_3)
        ]
        header.extend(header_monthly_combined)

    footfall_df = pd.DataFrame(columns=header)

    # there is a max of 15 possible footfall outcome sections in spreadsheet, each 32 lines apart
    for footfall_idx in range(0, (15 * 32), 32):
        footfall_instance = df.iloc[footfall_idx + 6, :2].append(df.iloc[footfall_idx + 11, :2])

        # within each footfall section data is spread over 6 lines, each 5 cells apart
        for year_idx in range(footfall_idx, footfall_idx + 30, 5):
            footfall_instance = footfall_instance.append(df.iloc[(year_idx + 6), 2:-1])

        footfall_instance = pd.DataFrame(footfall_instance).T
        footfall_instance.columns = header
        footfall_df = footfall_df.append(footfall_instance)

    footfall_df = drop_empty_rows(footfall_df, "Relevant Project(s)")

    # TODO: These cells not "locked" in Excel sheet. Assuming (from context of spreadsheet) they should be.
    # TODO: Hard-coding here as a precaution (to prevent un-mappable data ingest)
    footfall_df["Indicator Name"] = "Change in footfall"
    footfall_df["Unit of Measurement"] = "Year-on-year % change in monthly footfall"

    footfall_df = footfall_df.reset_index(drop=True)
    return footfall_df


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
