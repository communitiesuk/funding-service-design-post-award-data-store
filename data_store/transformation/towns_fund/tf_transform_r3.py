"""
Methods specifically for extracting data from Towns Fund Round 3 reporting template used for Reporting Round
1 October 2022 to 31 March 2023.
"""

import typing
from datetime import datetime

import numpy as np
import pandas as pd

import data_store.validation.towns_fund.failures.user as uf
from data_store.const import (
    OUTCOME_CATEGORIES,
    OUTPUT_CATEGORIES,
    TF_PLACE_NAMES_TO_ORGANISATIONS,
)
from data_store.exceptions import OldValidationError
from data_store.messaging import SharedMessages as msgs
from data_store.transformation.towns_fund import common
from data_store.transformation.utils import (
    convert_financial_halves,
    drop_empty_rows,
    extract_postcodes,
)


def transform(df_ingest: dict[str, pd.DataFrame], reporting_round: int = 3) -> dict[str, pd.DataFrame]:
    """
    Extract data from Towns Fund Reporting Template into column headed Pandas DataFrames.

    :param df_ingest: DataFrame of parsed Excel data.
    :return: Dictionary of extracted "tables" as DataFrames, and str representing reporting period for the form
    """

    towns_fund_extracted: dict[str, pd.DataFrame] = dict()
    towns_fund_extracted["Submission_Ref"] = common.get_submission_details()
    towns_fund_extracted["Place Details"] = extract_place_details(df_ingest["2 - Project Admin"])
    fund_code = common.get_fund_code(towns_fund_extracted["Place Details"])
    project_lookup = extract_project_lookup(
        df_ingest["Project Identifiers"], towns_fund_extracted["Place Details"], fund_code
    )
    programme_id = get_programme_id(df_ingest["Place Identifiers"], towns_fund_extracted["Place Details"], fund_code)
    # append Programme ID onto "Place Details" DataFrame
    towns_fund_extracted["Place Details"]["Programme ID"] = programme_id
    towns_fund_extracted["Programme_Ref"] = extract_programme(
        towns_fund_extracted["Place Details"], programme_id, fund_code
    )
    towns_fund_extracted["Organisation_Ref"] = extract_organisation(towns_fund_extracted["Place Details"])
    towns_fund_extracted["Project Details"] = extract_project(
        df_ingest["2 - Project Admin"],
        project_lookup,
        programme_id,
    )
    towns_fund_extracted["Programme Progress"] = extract_programme_progress(
        df_ingest["3 - Programme Progress"],
        programme_id,
    )
    towns_fund_extracted["Project Progress"] = extract_project_progress(
        df_ingest["3 - Programme Progress"],
        project_lookup,
    )
    towns_fund_extracted["Programme Management"] = extract_programme_management(
        df_ingest["4a - Funding Profiles"],
        programme_id,
    )
    towns_fund_extracted["Funding Questions"] = extract_funding_questions(
        df_ingest["4a - Funding Profiles"],
        programme_id,
    )
    towns_fund_extracted["Funding Comments"] = extract_funding_comments(
        df_ingest["4a - Funding Profiles"],
        project_lookup,
    )
    towns_fund_extracted["Funding"] = extract_funding_data(
        df_ingest["4a - Funding Profiles"],
        project_lookup,
        reporting_round,
    )
    towns_fund_extracted["Private Investments"] = extract_psi(df_ingest["4b - PSI"], project_lookup)
    towns_fund_extracted["Output_Data"] = extract_outputs(df_ingest["5 - Project Outputs"], project_lookup)
    towns_fund_extracted["Outputs_Ref"] = extract_output_categories(towns_fund_extracted["Output_Data"])
    towns_fund_extracted["Outcome_Data"] = combine_outcomes(
        df_ingest["6 - Outcomes"],
        project_lookup,
        programme_id,
    )
    towns_fund_extracted["Outcome_Ref"] = extract_outcome_categories(towns_fund_extracted["Outcome_Data"])
    towns_fund_extracted["RiskRegister"] = extract_risks(
        df_ingest["7 - Risk Register"],
        project_lookup,
        programme_id,
    )

    return towns_fund_extracted


def extract_place_details(df_place: pd.DataFrame) -> pd.DataFrame:
    """
    Extract place information from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Project work sheet, parsed as dataframe.

    :param df_place: Input DataFrame containing data.
    :return: Extracted DataFrame containing place detail data.
    """
    # strip out everything other than "SECTION A..." in spreadsheet.
    df_place = df_place.iloc[6:21, 2:5]

    # rename col headers for ease
    df_place.columns = pd.Index([0, 1, 2])

    # fill in blank (merged) cells
    field_names_first = []
    x = ""
    for y in df_place[0]:
        if y is not np.nan:
            x = y

        field_names_first.append(x)

    df_place[0] = field_names_first
    df_place.columns = pd.Index(["Question", "Indicator", "Answer"])

    return df_place


def extract_project_lookup(df_lookup: pd.DataFrame, df_place: pd.DataFrame, fund_code: str) -> dict:
    """
    Extract relevant project code lookups for the current ingest instance.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Project Identifiers work sheet, parsed as dataframe.

    :param df_lookup: The input DataFrame containing project data.
    :param df_place: Extracted place_names DataFrame.
    :param fund_code: The fund code for this ingest.
    :return: Dict of project_id's mapped to project names for this ingest. .
    """
    place_name = df_place.loc[df_place["Question"] == "Please select your place name"]["Answer"].values[0]

    # fetch either "Town Deal" or "Future High Streets Fund" project_id lookup table
    df_lookup = df_lookup.iloc[3:, 1:4] if fund_code == "TD" else df_lookup.iloc[3:296, 8:11]
    # hard-code column headers rather than extract from spreadsheet headers due to typo's in the latter.
    df_lookup.columns = pd.Index(["Unique Project Identifier", "Town", "Project Name"])

    # filter on current place / programme and convert to dict
    df_lookup = df_lookup.loc[df_lookup["Town"].str.lower().str.strip() == str(place_name).lower().strip()]
    project_lookup = dict(zip(df_lookup["Project Name"], df_lookup["Unique Project Identifier"], strict=False))

    return project_lookup


def get_programme_id(df_lookup: pd.DataFrame, df_place: pd.DataFrame, fund_code: str) -> str:
    """
    Calculate programme code for the current ingest instance.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Place Identifiers work sheet, parsed as dataframe.

    :param df_lookup: The input DataFrame containing place id data.
    :param df_place: Extracted place_names DataFrame.
    :param fund_code: The fund code for this ingest.
    :return: programme code.
    """
    place_name = df_place.loc[df_place["Question"] == "Please select your place name"]["Answer"].values[0]

    # fetch either "Town Deal" or "Future High Streets Fund" place name/code lookup table
    df_lookup = df_lookup.iloc[2:, 1:3] if fund_code == "TD" else df_lookup.iloc[2:74, 4:6]
    df_lookup.columns = pd.Index(["place", "code"])

    # If a non-valid fund_type is ingested, nothing will be prefixed to the programme_id (error we catch later)

    if fund_code:
        code = df_lookup.loc[df_lookup["place"].str.lower().str.strip() == str(place_name).lower().strip()][
            "code"
        ].values[0]
    else:
        code = ""

    return "-".join([fund_code, code])


def get_canonical_organisation_name(df_place: pd.DataFrame) -> str:
    """
    Get the canonical organisation name as mapped from the place name.

    The canonical organisation name refers to the current standardised name of the organisation,
    and is how it should appear in the database.

    :param df_place: Extracted place information.
    :return: A string with the canonincal organisation name.

    """
    place_question = "Please select your place name"
    place_value: str = [df_place.loc[df_place["Question"] == place_question]["Answer"].values[0]][0]
    # Strip whitespace which breaks matching
    return TF_PLACE_NAMES_TO_ORGANISATIONS[place_value.strip()]


def extract_programme(df_place: pd.DataFrame, programme_id: str, fund_code: str) -> pd.DataFrame:
    """
    Extract programme row from ingest Data.

    :param df_place: Extracted place information.
    :param programme_id: ID of the programme for this ingest.
    :param fund_code: The fund code for this ingest.
    :return: A new DataFrame containing the extracted programme.
    """
    df_programme = pd.DataFrame.from_dict(
        {
            "Programme ID": programme_id,
            "Programme Name": [
                df_place.loc[df_place["Question"] == "Please select your place name"]["Answer"].values[0]
            ],
            "FundType_ID": fund_code or np.nan,
            "Organisation": [get_canonical_organisation_name(df_place)],
        }
    )

    return df_programme


def extract_organisation(df_place: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Organisation ref data (1 row) from ingest data.

    :param df_place: Extracted place information.
    :return: A new DataFrame containing the extracted organisation info.
    """
    organisation_name = get_canonical_organisation_name(df_place)

    df_org = pd.DataFrame.from_dict(
        {
            "Organisation": [organisation_name],
        }
    )
    return df_org


def extract_project(df_project: pd.DataFrame, project_lookup: dict, programme_id: str) -> pd.DataFrame:
    """
    Extract project rows from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Project work sheet, parsed as dataframe.

    :param df_project: The input DataFrame containing project data.
    :param project_lookup: Dict of project_name / project_id mappings for this ingest.
    :param programme_id: ID of the programme for this ingest
    :return: A new DataFrame containing the extracted project rows.
    """

    # strip out everything except Section B
    df_project = df_project.iloc[24:46, 4:12]

    # in first header row, replace empty strings with preceding value.
    header_row_1 = []
    x = ""
    for y in df_project.iloc[0]:
        if y is not np.nan:
            x = y

        header_row_1.append(x)

    # replace NaN with ""
    header_row_2 = [field if field is not np.nan else "" for field in list(df_project.iloc[1])]
    # zip together headers (deals with merged cells issues)
    header_row_combined = ["__".join([x, y]).rstrip("_") for x, y in zip(header_row_1, header_row_2, strict=False)]
    # apply header to df with top rows stripped
    df_project = pd.DataFrame(df_project.values[2:], columns=header_row_combined)

    df_project = drop_empty_rows(df_project, ["Project Name"])

    # rename some long column headers
    multiplicity_header = (
        "Does the project have a single location (e.g. one site) or "
        "multiple (e.g. multiple sites or across a number of post codes)? "
    )
    df_project.rename(
        columns={
            multiplicity_header: "Single or Multiple Locations",
            "Multiple locations __Are you providing a GIS map (see guidance) with your return?": "GIS Provided",
        },
        inplace=True,
    )

    # combine columns based on Single / multiple conditional
    single_postcode = "Single location __Project Location - Post Code (e.g. SW1P 4DF) "
    multiple_postcode = "Multiple locations __Project Locations - Post Code (e.g. SW1P 4DF) "
    df_project["Locations"] = df_project.apply(
        lambda row: row[single_postcode] if row["Single or Multiple Locations"] == "Single" else row[multiple_postcode],
        axis=1,
    )
    df_project["Postcodes"] = [extract_postcodes(x) for x in df_project["Locations"]]

    single_lat_long = "Single location __Project Location - Lat/Long Coordinates (3.d.p e.g. 51.496, -0.129)"
    multiple_lat_long = "Multiple locations __Project Locations - Lat/Long Coordinates (3.d.p e.g. 51.496, -0.129)"
    df_project["Lat/Long"] = df_project.apply(
        lambda row: row[single_lat_long] if row["Single or Multiple Locations"] == "Single" else row[multiple_lat_long],
        axis=1,
    )

    # drop old columns no longer required
    df_project = df_project.drop([single_postcode, multiple_postcode, single_lat_long, multiple_lat_long], axis=1)

    # lookup / add project ID
    df_project["Project ID"] = df_project["Project Name"].map(project_lookup)

    # replace default excel values (unselected option)
    df_project["GIS Provided"] = df_project["GIS Provided"].replace("< Select >", np.nan)

    # add programme id (for fk lookups in DB ingest)
    df_project["Programme ID"] = programme_id

    # Project 1 always starts at row 27 in the spreadsheet, but the df is 0-indexed, so we need to add 26
    df_project.index = df_project.index + 26

    return df_project


def extract_programme_progress(df_data: pd.DataFrame, programme_id: str) -> pd.DataFrame:
    """
    Extract Programme progress questions/answers from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Programme Progress work sheet, parsed as dataframe.

    :param df_data: The input DataFrame containing progress data.
    :param programme_id: Programme id for this ingest.
    :return: A new DataFrame containing the extracted programme progress rows.
    """
    df_data = df_data.iloc[6:13, 2:4]
    df_data.columns = pd.Index(["Question", "Answer"])
    df_data["Programme ID"] = programme_id
    return df_data


def extract_project_progress(df_data: pd.DataFrame, project_lookup: dict, reporting_round: int = 3) -> pd.DataFrame:
    """
    Extract Project progress rows from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Programme Progress work sheet, parsed as dataframe.

    :param df_data: The input DataFrame containing project data.
    :param project_lookup: Dict of project_name / project_id mappings for this ingest.
    :param round_four: if True, ingest two additional columns
    :return: A new DataFrame containing the extracted project progress rows.
    """
    # if round 4 or 5, ingest two additional columns
    df_data = df_data.iloc[18:39, 2:15] if reporting_round >= 4 else df_data.iloc[18:39, 2:13]
    df_data = df_data.rename(columns=df_data.iloc[0].to_dict()).iloc[1:]
    df_data = drop_empty_rows(df_data, ["Project Name"])
    df_data["Project ID"] = df_data["Project Name"].map(project_lookup)

    # rename and drop columns to match "load" mappings. Carriage returns for windows/linux style (for tests)
    df_data = df_data.rename(
        columns={
            "Start Date -\n mmm/yy (e.g. Dec-22)": "Start Date",
            "Completion Date -\n mmm/yy (e.g. Dec-22)": "Completion Date",
            "Start Date -\r\n mmm/yy (e.g. Dec-22)": "Start Date",
            "Completion Date -\r\n mmm/yy (e.g. Dec-22)": "Completion Date",
        }
    )
    df_data = df_data.drop(["Project Name"], axis=1)
    df_data = df_data.replace("< Select >", "")

    whole_nums_to_integers_cols = ("Delivery (RAG)", "Spend (RAG)", "Risk (RAG)")

    # RAG ratings of user input '4' can be read into a DataFrame as '4.0'
    for col in whole_nums_to_integers_cols:
        for idx, val in df_data[col].items():
            if pd.isna(val):
                continue  # skip NA values
            else:
                df_data.loc[idx, col] = str(val).rstrip(".0")
    return df_data


def extract_programme_management(df_data: pd.DataFrame, programme_id: str) -> pd.DataFrame:
    if programme_id.split("-")[0] != "TD":  # Return an empty DataFrame if the programme ID is not Town Deal
        return pd.DataFrame(
            columns=[
                "Programme ID",
                "Payment Type",
                "Spend for Reporting Period",
                "Actual/Forecast",
                "Start_Date",
                "End_Date",
            ]
        )
    header_prefix = ["Payment Type"]

    header_row_1 = []
    x = ""
    for y in df_data.iloc[22, 6:24]:
        if y is not np.nan:
            x = y

        header_row_1.append(x)

    header_row_2 = [field if field is not np.nan else "" for field in list(df_data.iloc[23, 6:24])]
    header_row_3 = [field if field is not np.nan else "" for field in list(df_data.iloc[24, 6:24])]
    header_row_combined = [
        "__".join([x, y, z]).rstrip("_") for x, y, z in zip(header_row_1, header_row_2, header_row_3, strict=False)
    ]
    header = header_prefix + header_row_combined
    transformed_df = df_data.iloc[25:27, [2] + list(range(6, 24))]
    transformed_df.columns = pd.Index(header)
    transformed_df.insert(0, "Programme ID", programme_id)
    columns_to_drop = [col for col in transformed_df.columns if col.endswith("__Total")]
    transformed_df.drop(columns=columns_to_drop, inplace=True)
    transformed_df = pd.melt(
        transformed_df,
        id_vars=["Programme ID", "Payment Type"],
        var_name="Reporting Period",
        value_name="Spend for Reporting Period",
        ignore_index=False,
    )

    # hacky (but effective) methods to extract "Reporting Period" & "Actual/Forecast" columns
    # Regex everything after "__" in string
    transformed_df["Actual/Forecast"] = transformed_df["Reporting Period"].str.extract(r".*__(.*)")
    transformed_df["Reporting Period"] = [
        x.split(" (£s)__")[1][:3] + x[17:22] if "__" in x else x for x in transformed_df["Reporting Period"]
    ]

    transformed_df = convert_financial_halves(transformed_df, "Reporting Period")

    transformed_df.reset_index(drop=True, inplace=True)
    return transformed_df


def extract_funding_questions(df_input: pd.DataFrame, programme_id: str) -> pd.DataFrame:
    """
    Extract funding questions data from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Funding Profiles work sheet, parsed as dataframe.

    :param df_input: The input DataFrame containing funding profiles data.
    :param programme_id: Programme id for this ingest.
    :return: A new DataFrame containing the extracted funding questions.
    """
    if programme_id.split("-")[0] == "HS":
        # return empty dataframe if fund_type is Future High Street Fund
        return pd.DataFrame(columns=["Question", "Guidance Notes", "Indicator", "Response", "Programme ID"])

    df_input = df_input.iloc[13:20, 2:13]
    first_row = df_input.iloc[0]
    df_input = df_input.dropna(axis=1, how="all", subset=[first_row.name])

    # Use the first row as the column headers
    fund_questions_df = df_input.rename(columns=df_input.iloc[0].to_dict()).iloc[1:]

    # unpivot the data, ignoring first line.
    fund_questions_df = pd.melt(
        fund_questions_df.iloc[1:],
        id_vars=[fund_questions_df.columns[0], "Guidance Notes"],
        var_name="Indicator",
        value_name="Response",
        ignore_index=False,
    )
    fund_questions_df = fund_questions_df.rename(columns={fund_questions_df.columns[0]: "Question"})
    # first row of input table needs extracting separately from melt, as it has no "indicators".
    non_pivot_row = [df_input.iloc[1, 0], df_input.iloc[1, -1], np.nan, df_input.iloc[1, 1], 14]

    fund_questions_df["original_index"] = fund_questions_df.index
    fund_questions_df.reset_index(drop=True, inplace=True)

    # Create a DataFrame from non_pivot_row
    new_row = pd.DataFrame([non_pivot_row], columns=fund_questions_df.columns)

    # Use pd.concat to add the new row
    fund_questions_df = pd.concat([fund_questions_df, new_row], ignore_index=True)

    fund_questions_df.index = pd.Index(fund_questions_df["original_index"])
    fund_questions_df.drop("original_index", axis=1, inplace=True)

    fund_questions_df.sort_values(["Question", "Indicator"], inplace=True)

    fund_questions_df["Response"].replace("< Select >", "", inplace=True)
    fund_questions_df["Response"] = fund_questions_df["Response"].astype(str).str.strip()
    fund_questions_df["Programme ID"] = programme_id
    return fund_questions_df


def extract_funding_comments(df_input: pd.DataFrame, project_lookup: dict) -> pd.DataFrame:
    """
    Extract funding comments data from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Funding Profiles work sheet, parsed as dataframe.

    :param df_input: The input DataFrame containing funding profiles data.
    :param project_lookup: Dict of project_name / project_id mappings for this ingest.
    :return: A new DataFrame containing the extracted funding comments.
    """
    df_input = df_input.iloc[32:, 2:26]
    df_input["original_index"] = df_input.index
    header = ["Project name", "Comment", "original_index"]
    df_fund_comments = pd.DataFrame(columns=header)

    for idx in range(len(project_lookup)):
        line_idx = 28 * idx
        current_project = ": ".join(str(df_input.iloc[line_idx, 0]).split(": ")[1:])  # omit the "Project X: " prefix
        comment = df_input.iloc[line_idx + 26, 0]
        original_index = df_input.iloc[line_idx + 26]["original_index"]
        fund_row = pd.DataFrame([[current_project, comment, original_index]], columns=header)
        df_fund_comments = pd.concat([df_fund_comments, fund_row])

    df_fund_comments["Project ID"] = df_fund_comments["Project name"].map(project_lookup)

    df_fund_comments = df_fund_comments.drop(["Project name"], axis=1)
    df_fund_comments.index = pd.Index(df_fund_comments["original_index"])
    df_fund_comments.drop("original_index", axis=1, inplace=True)
    return df_fund_comments


def extract_funding_data(df_input: pd.DataFrame, project_lookup: dict, reporting_round: int = 3) -> pd.DataFrame:
    """
    Extract funding data (excluding comments) from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Funding Profiles work sheet, parsed as dataframe.

    :param df_input: The input DataFrame containing funding profiles data.
    :param project_lookup: Dict of project_name / project_id mappings for this ingest.
    :param round_four: if True, ingest two additional columns
    :return: A new DataFrame containing the extracted funding data.
    """
    fund_type = next(iter(project_lookup.values())).split("-")[0]
    check_programme_only = df_input.iloc[18, 4] == "Programme only"
    df_input = df_input.iloc[32:, 2:25]

    header_prefix = ["Funding Source Name", "Funding Source Type", "Secured"]

    # construct header rows out of 3 rows (merged cells), and add to empty init dataframe
    header_row_1 = []
    x = ""
    for y in df_input.iloc[2, 3:]:
        if y is not np.nan:
            x = y

        header_row_1.append(x)

    header_row_2 = [field if field is not np.nan else "" for field in list(df_input.iloc[3, 3:])]
    header_row_3 = [field if field is not np.nan else "" for field in list(df_input.iloc[4, 3:])]
    header_row_combined = [
        "__".join([x, y, z]).rstrip("_") for x, y, z in zip(header_row_1, header_row_2, header_row_3, strict=False)
    ]
    header = header_prefix + header_row_combined
    header.append("Project Name")
    df_funding = pd.DataFrame()

    for idx in range(len(project_lookup)):
        line_idx = 28 * idx
        current_project = ": ".join(str(df_input.iloc[line_idx, 0]).split(": ")[1:])  # omit the "Project X: " prefix

        # Extract only pertinent parts of each subsection
        current_profile = pd.concat(
            [
                df_input.iloc[line_idx + 5 : line_idx + 8],
                df_input.iloc[line_idx + 9 : line_idx + 11],
            ]
        )
        # Add "Towns Fund" as Funding Source value for 1st 5 (mandatory) sources for each project.
        current_profile.iloc[:, 1] = "Towns Fund"
        current_profile = pd.concat([current_profile, df_input.iloc[line_idx + 17 : line_idx + 22]])

        # Add current project (for iteration), lookup ID and add to another col.
        current_profile[""] = current_project
        current_profile.columns = pd.Index(header)
        current_profile.insert(0, "Project ID", current_profile["Project Name"].map(project_lookup))

        # Drop "total" columns along with redundant "Project Name"
        columns_to_drop = [col for col in current_profile.columns if col.endswith("__Total")]
        columns_to_drop.append("Project Name")
        current_profile = current_profile.drop(columns_to_drop, axis=1)
        # rename for consistency
        current_profile.rename(
            columns={"Before 2020/21": "Before 20/21"},
            inplace=True,
        )
        df_funding = pd.concat([df_funding, current_profile])

    # drop spare rows from ingest form (ie ones with no "Ingest source name" filled out.
    df_funding = drop_empty_rows(df_funding, ["Funding Source Name"])

    # unpivot the table around reporting periods/spend, and sort
    df_funding = pd.melt(
        df_funding,
        id_vars=list(df_funding.columns[:4]),
        var_name="Reporting Period",
        value_name="Spend for Reporting Period",
        ignore_index=False,
    )
    df_funding.sort_values(["Project ID", "Funding Source Name"], inplace=True)

    # hacky (but effective) methods to extract "Reporting Period" & "Actual/Forecast" columns
    # Regex everything after "__" in string
    df_funding["Actual/Forecast"] = df_funding["Reporting Period"].str.extract(r".*__(.*)")
    df_funding["Reporting Period"] = [
        x.split(" (£s)__")[1][:3] + x[17:22] if "__" in x else x for x in df_funding["Reporting Period"]
    ]
    df_funding["Funding Source Name"] = df_funding["Funding Source Name"].astype(str).str.strip()

    df_funding = convert_financial_halves(df_funding, "Reporting Period")
    df_funding["original_index"] = df_funding.index
    df_funding.reset_index(drop=True, inplace=True)

    # keep the logic for former rounds - TODO: ideally soon to be removed
    if reporting_round < 6:
        # drop always unused cells for funding secured before 2020 and beyond 2026
        unused_mask = df_funding.loc[
            (
                (df_funding["Funding Source Type"] == "Towns Fund")
                & (df_funding["Start_Date"].isna() | (df_funding["End_Date"].isna()))
            )
        ]
        df_funding.drop(unused_mask.index, inplace=True)

    if fund_type == "HS":
        # Round 3 collects up to H2 23/24, round 4 collects up to H1 24/25, round 5 collects up to H2 24/25
        start_date_cut_off_mapping = {
            3: datetime(2023, 10, 1),
            4: datetime(2024, 4, 1),
            5: datetime(2024, 10, 1),
        }
        start_date_cut_off = start_date_cut_off_mapping.get(reporting_round)
        unused_fhsf_mask = df_funding.loc[
            # drop unused FHSF Questions
            (
                (df_funding["Funding Source Type"] == "Towns Fund")
                & (
                    df_funding["Funding Source Name"].isin(
                        [
                            "Town Deals 5% CDEL Pre-Payment",
                            "Towns Fund RDEL Payment which is being utilised on TF project related activity",
                            "How much of your RDEL forecast is contractually committed?",
                        ]
                    )
                )
            )
            |
            # drop unused FHSF forcast cells
            (
                (df_funding["Funding Source Type"] == "Towns Fund")
                & ((start_date_cut_off is not None) and (df_funding["Start_Date"] > start_date_cut_off))
            )
            # TODO: Review logic for future forcast in reporting round 5
        ]
        df_funding.drop(unused_fhsf_mask.index, inplace=True)

    if fund_type == "TD" and check_programme_only:
        unused_td_mask = df_funding.loc[
            # drop unused TD Questions in the case of Programme Only
            (
                (df_funding["Funding Source Type"] == "Towns Fund")
                & df_funding["Funding Source Name"].isin(["Town Deals 5% CDEL Pre-Payment"])
            )
        ]
        df_funding.drop(unused_td_mask.index, inplace=True)

    # Swap values where "Funding Source Type" is "Towns Fund"
    mask = df_funding["Funding Source Type"] == "Towns Fund"
    df_funding.loc[mask, ["Funding Source Type", "Funding Source Name"]] = df_funding.loc[
        mask, ["Funding Source Name", "Funding Source Type"]
    ].values

    df_funding.index = pd.Index(df_funding["original_index"])
    df_funding.drop("original_index", axis=1, inplace=True)

    return df_funding


def extract_psi(df_psi: pd.DataFrame, project_lookup: dict) -> pd.DataFrame:
    """
    Extract Project PSI rows from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically PSI work sheet, parsed as dataframe.

    :param df_psi: The input DataFrame containing project data.
    :param project_lookup: Dict of project_name / project_id mappings for this ingest.
    :return: A new DataFrame containing the extracted PSI rows.
    """
    df_psi = df_psi.iloc[12:32, 3:]
    headers = [
        "Project name",
        "Total Project Value",
        "Townsfund Funding",
        "Private Sector Funding Required",
        "Private Sector Funding Secured",
        "gap",
        "Additional Comments",
    ]
    df_psi.columns = pd.Index(headers)
    df_psi = drop_empty_rows(df_psi, ["Project name"])
    df_psi.insert(0, "Project ID", df_psi["Project name"].map(project_lookup))
    df_psi = df_psi.drop(["gap", "Project name"], axis=1)
    return df_psi


def extract_risks(
    df_risk: pd.DataFrame, project_lookup: dict, programme_id: str, reporting_round: int = 3
) -> pd.DataFrame:
    """
    Extract Programme specific risk register rows from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Risk Register work sheet, parsed as dataframe.

    :param df_risk: The input DataFrame containing risk data.
    :param project_lookup: Dict of project_name / project_id mappings for this ingest.
    :param programme_id: ID of the programme for this ingest
    :return: A new DataFrame containing the extracted programme/risk rows.
    """
    df_risk_programme = df_risk.iloc[9:14, 2:16]
    df_risk_programme = df_risk_programme.rename(columns=df_risk_programme.iloc[0].to_dict()).iloc[2:]
    df_risk_programme.insert(0, "Project ID", np.nan)
    df_risk_programme.insert(0, "Programme ID", programme_id)

    df_risk_all = pd.concat([df_risk_programme, extract_project_risks(df_risk, project_lookup)])
    risk_columns = [
        "Programme ID",
        "Project ID",
        "RiskName",
        "RiskCategory",
        "Short Description",
        "Full Description",
        "Consequences",
        "Pre-mitigatedImpact",
        "Pre-mitigatedLikelihood",
        "Mitigatons",  # typo in DM v3.7
        "PostMitigatedImpact",
        "PostMitigatedLikelihood",
        "Proximity",
        "RiskOwnerRole",
    ]
    df_risk_all.drop(["Pre-mitigated Raw Total Score", "Post-mitigated Raw Total Score"], axis=1, inplace=True)
    df_risk_all.columns = pd.Index(risk_columns)
    if reporting_round == 3:
        # Round 3 ingests were completed using the behaviour of discarding any rows with no Risk Name
        # This is preserved to ensure previously valid R3 subs remain valid
        df_risk_all = drop_empty_rows(df_risk_all, ["RiskName"])
    else:
        # Round 4 and 5 ingests behaviour requires all non id columns to be empty in order to drop the row
        drop_if_all_empty = [column for column in risk_columns if column not in ["Programme ID", "Project ID"]]
        df_risk_all = drop_empty_rows(df_risk_all, drop_if_all_empty)
    return df_risk_all


def extract_project_risks(df_input: pd.DataFrame, project_lookup: dict) -> pd.DataFrame:
    """
    Extract Project specific risk register rows from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Risk Register work sheet, parsed as dataframe.

    :param df_input: The input DataFrame containing risk data.
    :param project_lookup: Dict of project_name / project_id mappings for this ingest.
    :return: A new DataFrame containing the extracted project/risk rows.
    """
    # strip unwanted border bloat
    df_input = df_input.iloc[18:, 2:16]

    # setup header vals
    risk_header = df_input.iloc[2, :].tolist()
    risk_header.append("Project Name")
    risk_df = pd.DataFrame(columns=risk_header)

    # iterate through spreadsheet sections and extract relevant rows.
    for idx in range(len(project_lookup)):
        line_idx = 8 * idx
        if idx >= 3:
            line_idx += 1  # hacky fix to inconsistent spreadsheet format (extra row at line 42)
        current_project = df_input.iloc[line_idx, 1]
        project_risks = df_input.iloc[line_idx + 4 : line_idx + 7].copy()
        project_risks[""] = current_project
        project_risks.columns = pd.Index(risk_header)
        risk_df = pd.concat([risk_df, project_risks])

    risk_df.insert(0, "Project ID", risk_df["Project Name"].map(project_lookup))
    risk_df.insert(0, "Programme ID", np.nan)

    risk_df = risk_df.drop(["Project Name"], axis=1)
    return risk_df


def extract_outputs(df_input: pd.DataFrame, project_lookup: dict) -> pd.DataFrame:
    """
    Extract Project Output rows from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Projects Outputs work sheet, parsed as dataframe.

    :param df_input: The input DataFrame containing output data.
    :param project_lookup: Dict of project_name / project_id mappings for this ingest.
    :return: A new DataFrame containing the extracted project output rows.
    """

    df_input = df_input.iloc[15:, 2:-1]

    # construct header rows out of 3 rows (merged cells), and add to empty init dataframe
    header_row_1 = []
    x = ""
    for y in df_input.iloc[3]:
        if y is not np.nan:
            x = y

        header_row_1.append(x)

    header_row_2 = [field if field is not np.nan else "" for field in list(df_input.iloc[5])]
    header_row_3 = [field if field is not np.nan else "" for field in list(df_input.iloc[6])]
    header_row_combined = [
        "__".join([x, y, z]).rstrip("_") for x, y, z in zip(header_row_1, header_row_2, header_row_3, strict=False)
    ]
    header_row_combined.append("Project Name")
    outputs_df = pd.DataFrame()

    # iterate over project sections, based on number of projects.
    for idx in range(len(project_lookup)):
        line_idx = 38 * idx

        if idx >= 1:  # hacky fix to allow for hidden line part way through section for project 1
            line_idx += 1

        # TODO: write tests for this logic (or preferably for the whole of extract and transform)
        current_project = ": ".join(df_input.iloc[line_idx, 0].split(": ")[1:])  # type: ignore     # omit the "Project X: " prefix

        if idx >= 1:  # hacky fix to allow for hidden line part way through section for project 1
            line_idx -= 1

        # combine extracted sections for each sub-table, add column headers
        project_outputs = pd.concat(
            [
                df_input.iloc[line_idx + 8 : line_idx + 11],
                df_input.iloc[line_idx + 12 : line_idx + 27],
                df_input.iloc[line_idx + 28 : line_idx + 38],
            ]
        )
        project_outputs[""] = current_project
        project_outputs.columns = pd.Index(header_row_combined)

        # TODO: Are we correct to drop rows with no Outcome name (indicator here)? What if form has no outcome name,
        #  but valid dat in other columns. Save without fk ref to Outcome_data table, just linked to submission?
        project_outputs = drop_empty_rows(project_outputs, ["Indicator Name"])
        add_info_name = (
            "Additional Information (only relevant for specific output indicators - see indicator guidance document)"
        )
        project_outputs.rename(
            columns={
                "Beyond April 2026__TOTAL": "Beyond 25/26",
                add_info_name: "Additional Information",
                "Indicator Name": "Output",
            },
            inplace=True,
        )
        project_outputs.insert(0, "Project ID", project_outputs["Project Name"].map(project_lookup))

        # Drop "TOTAL" columns along with redundant "Project Name"
        columns_to_drop = [col for col in project_outputs.columns if col.endswith("__TOTAL")]
        columns_to_drop.append("Project Name")
        columns_to_drop.append("Grand Total")
        project_outputs = project_outputs.drop(columns_to_drop, axis=1)

        # move final column to front of DF, for ease
        project_outputs = project_outputs[
            ["Additional Information"] + [col for col in project_outputs.columns if col != "Additional Information"]
        ]

        outputs_df = pd.concat([outputs_df, project_outputs])

    # unpivot the table around reporting periods/output measurable, and sort
    outputs_df = pd.melt(
        outputs_df,
        id_vars=list(outputs_df.columns[:4]),
        var_name="Reporting Period",
        value_name="Amount",
        ignore_index=False,
    )
    outputs_df.sort_values(["Project ID", "Reporting Period"], inplace=True)

    # hacky (but effective) methods to extract "Reporting Period" & "Actual/Forecast" columns
    # Regex everything after "__" in string
    outputs_df["Actual/Forecast"] = outputs_df["Reporting Period"].str.extract(r".*__(.*)")
    outputs_df["Reporting Period"] = [x[24:27] + x[17:22] if "__" in x else x for x in outputs_df["Reporting Period"]]

    outputs_df = convert_financial_halves(outputs_df, "Reporting Period")
    return outputs_df


def extract_output_categories(df_outputs: pd.DataFrame) -> pd.DataFrame:
    """
    Extract unique Output rows from Output Data and map to categories.

    Input dataframe is "Outputs" DataFrame as extracted from "Towns Fund reporting template".

    :param df_outputs: DataFrame containing extracted output data.
    :return: A new DataFrame containing unique extracted outputs mapped to categories.
    """
    df_outputs = pd.DataFrame(df_outputs["Output"]).drop_duplicates()
    df_outputs.columns = pd.Index(["Output Name"])

    # default (ie any outputs not in the provided list are assumed to be "custom"
    df_outputs["Output Category"] = df_outputs["Output Name"].map(OUTPUT_CATEGORIES).fillna("Custom")
    return df_outputs


def combine_outcomes(
    df_input: pd.DataFrame, project_lookup: dict, programme_id: str, reporting_period=3
) -> pd.DataFrame:
    """
    Extract different outcome types from DataFrame and combine into a single DataFrame

    :param df_input: The input DataFrame containing outcomes data.
    :param project_lookup: Dict of project_name / project_id mappings for this ingest.
    :param programme_id: ID of the programme for this ingest
    :param reporting_period: reporting period number default 3
    :return: A new DataFrame containing the combined project outcome rows.
    """
    df_outcomes = extract_outcomes(df_input, project_lookup, programme_id, reporting_period)
    df_outcomes = pd.concat([df_outcomes, extract_footfall_outcomes(df_input, project_lookup, programme_id)])
    return df_outcomes


def extract_outcomes(df_input: pd.DataFrame, project_lookup: dict, programme_id: str, reporting_period) -> pd.DataFrame:
    """
    Extract Outcome rows from a DataFrame.

    This includes all Outputs except "Footfall Indicator" (extracted separately)

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Projects Outputs work sheet, parsed as dataframe.

    :param df_input: The input DataFrame containing outcomes data.
    :param project_lookup: Dict of project_name / project_id mappings for this ingest.
    :param programme_id: ID of the programme for this ingest
    :param reporting_period: reporting period number to toggle alternate behavior between rounds default 3,
    :return: A new DataFrame containing the extracted project outcome rows.
    """
    df_input = df_input.iloc[15:, 1:]

    header_row_1 = list(df_input.iloc[0])
    header_row_2 = [field if field is not np.nan else "" for field in list(df_input.iloc[1])]
    header_row_combined = ["__".join([x, y]).rstrip("_") for x, y in zip(header_row_1, header_row_2, strict=False)]

    outcomes_df = pd.DataFrame(df_input.values[6:26], columns=header_row_combined, index=df_input.index[6:26])
    custom_outcomes_df = pd.DataFrame(df_input.values[27:37], columns=header_row_combined, index=df_input.index[27:37])
    outcomes_df = pd.concat([outcomes_df, custom_outcomes_df])
    # If indicator name or project ref is empty - drop row (cannot map to DB table)
    outcomes_df = drop_empty_rows(outcomes_df, ["Indicator Name"])
    if reporting_period == 3:
        outcomes_df = drop_empty_rows(outcomes_df, ["Relevant project(s)"])
    relevant_projects = set(outcomes_df["Relevant project(s)"])
    relevant_projects.discard("Multiple")
    if invalid_projects := relevant_projects - set(project_lookup.keys()):
        raise OldValidationError(
            [
                uf.GenericFailure(
                    table="Outcome_Data",
                    section="Outcome Indicators (excluding footfall)",
                    column="Relevant project(s)",
                    # +1 to account for Excel files being 1-indexed
                    row_index=typing.cast(int, idx) + 1,
                    message=msgs.DROPDOWN,
                )
                for idx, _ in outcomes_df.loc[outcomes_df["Relevant project(s)"].isin(invalid_projects)].iterrows()
            ]
        )

    # Drop rows with Section header selected as the outcome from dropdown on form - This is not a valid outcome option.
    outcomes_df.drop(outcomes_df[outcomes_df["Relevant project(s)"] == "*** ORIGINAL: ***"].index, inplace=True)
    outcomes_df.insert(0, "Project ID", outcomes_df["Relevant project(s)"].map(project_lookup))
    # if ingest form has "multiple" selected for project, then set at programme level instead.
    outcomes_df.insert(1, "Programme ID", outcomes_df["Relevant project(s)"].map({"Multiple": programme_id}))

    long_string = "Please specify if you are able to provide this metric at a higher frequency level than annually"
    outcomes_df.rename(
        columns={
            "Indicator Name": "Outcome",
            "Unit of Measurement": "UnitofMeasurement",
            "Geography indicator refers to": "GeographyIndicator",
            long_string: "Higher Frequency",
        },
        inplace=True,
    )
    outcomes_df = outcomes_df.drop(["Relevant project(s)"], axis=1)

    # move final column to front of DF, for ease
    outcomes_df = outcomes_df[["Higher Frequency"] + [col for col in outcomes_df.columns if col != "Higher Frequency"]]

    # unpivot the table around reporting periods/outcome measurable, and sort
    outcomes_df = pd.melt(
        outcomes_df,
        id_vars=list(outcomes_df.columns[:6]),
        var_name="Reporting Period",
        value_name="Amount",
        ignore_index=False,
    )
    outcomes_df.sort_values(["Project ID", "Reporting Period"], inplace=True)

    # split out Actual or Forecast values
    outcomes_df["Actual/Forecast"] = outcomes_df["Reporting Period"].str.split("__").str[1]
    # split out start and end dates for financial years
    outcomes_df["Start_Date"] = (outcomes_df["Reporting Period"].str[15:19] + "-04-01").astype("datetime64[ns]")
    outcomes_df["End_Date"] = outcomes_df["Start_Date"].apply(lambda x: x + pd.offsets.MonthEnd(12))

    outcomes_df = outcomes_df.drop(["Reporting Period"], axis=1)

    return outcomes_df


def extract_footfall_outcomes(df_input: pd.DataFrame, project_lookup: dict, programme_id: str) -> pd.DataFrame:
    """
    Extract Footfall specific Outcome rows from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Projects Outputs work sheet, parsed as dataframe.

    :param df_input: The input DataFrame containing outcome data.
    :param project_lookup: Dict of project_name / project_id mappings for this ingest.
    :param programme_id: ID of the programme for this ingest
    :return: A new DataFrame containing the extracted footfall outcome rows.
    """
    df_input = df_input.iloc[53:, 1:]

    # Build the header. It is very long, and calculated dynamically, as the values are dynamically generated in Excel
    header = list(pd.concat([df_input.iloc[2, :2], df_input.iloc[7, :2]]))

    # within each footfall section data/header is spread over 6 lines, each 5 cells apart
    for year_idx in range(0, 30, 5):
        header_monthly_row_1 = [
            x := y if y is not np.nan else x  # noqa: F841, F821
            for y in df_input.iloc[(year_idx + 2), 2:-1]  # noqa: F841,F821
        ]
        header_monthly_row_2 = [str(field) for field in df_input.iloc[(year_idx + 4), 2:-1]]
        header_monthly_row_3 = list(df_input.iloc[year_idx + 5, 2:-1])
        header_monthly_combined = [
            "__".join([x, y, z]).rstrip("_")
            for x, y, z in zip(header_monthly_row_1, header_monthly_row_2, header_monthly_row_3, strict=False)
        ]
        header.extend(header_monthly_combined)

    footfall_df = pd.DataFrame(columns=header)

    # there is a max of 15 possible footfall outcome sections in spreadsheet, each 32 lines apart
    for footfall_idx in range(0, (15 * 32), 32):
        footfall_instance = pd.concat([df_input.iloc[footfall_idx + 6, :2], df_input.iloc[footfall_idx + 11, :2]])

        # within each footfall section data is spread over 6 lines, each 5 cells apart
        for year_idx in range(footfall_idx, footfall_idx + 30, 5):
            footfall_instance = pd.concat([footfall_instance, df_input.iloc[(year_idx + 6), 2:-1]])

        footfall_instance_df = pd.DataFrame(footfall_instance).T
        # footfall_idx + 6 for the index to match the index of the row for "Footfall Indicator" in original spreadsheet
        footfall_instance_df.index = pd.Index([df_input.index[footfall_idx + 6]])
        footfall_instance_df.columns = pd.Index(header)
        footfall_df = pd.concat([footfall_df, footfall_instance_df])

    footfall_df = drop_empty_rows(footfall_df, ["Relevant Project(s)"])
    relevant_projects = set(footfall_df["Relevant Project(s)"])
    relevant_projects.discard("Multiple")
    if invalid_projects := relevant_projects - set(project_lookup.keys()):
        # validation error raised here as post-transformation the project lookup information is lost
        raise OldValidationError(
            [
                uf.GenericFailure(
                    table="Outcome_Data",
                    section="Footfall Indicator",
                    # +1 to account for Excel files being 1-indexed, extra +5 for Outcome -> Project row
                    cell_index=f"B{typing.cast(int, idx) + 1 + 5}",
                    message=msgs.DROPDOWN,
                )
                for idx, _ in footfall_df.loc[footfall_df["Relevant Project(s)"].isin(invalid_projects)].iterrows()
            ]
        )

    # These cells not "locked" in Excel sheet. Assuming (from context of spreadsheet) they should be.
    # Hard-coding here as a precaution (to prevent un-mappable data ingest)
    footfall_df["Indicator Name"] = "Year on Year monthly % change in footfall"
    footfall_df["Unit of Measurement"] = "Year-on-year % change in monthly footfall"

    footfall_df.insert(0, "Project ID", footfall_df["Relevant Project(s)"].map(project_lookup))
    # if ingest form has "multiple" selected for project, then set at programme level instead.
    footfall_df.insert(1, "Programme ID", footfall_df["Relevant Project(s)"].map({"Multiple": programme_id}))
    footfall_df.rename(
        columns={
            "Indicator Name": "Outcome",
            "Unit of Measurement": "UnitofMeasurement",
            "Geography of indicator / measurement": "GeographyIndicator",
        },
        inplace=True,
    )
    footfall_df = footfall_df.drop(["Relevant Project(s)"], axis=1)
    # "Higher Frequency" is not a field in footfall section, but required (set to nan) to append to other Outcome types.
    footfall_df.insert(0, "Higher Frequency", np.nan)

    # unpivot the table around reporting periods/outcome measurable, and sort
    footfall_df = pd.melt(
        footfall_df,
        id_vars=list(footfall_df.columns[:6]),
        var_name="Reporting Period",
        value_name="Amount",
        ignore_index=False,
    )
    footfall_df.sort_values(["Project ID", "Reporting Period"], inplace=True)

    # split out Actual or Forecast values
    footfall_df["Actual/Forecast"] = footfall_df["Reporting Period"].str.split("__").str[-1]
    # split out start and end dates for months of financial years
    footfall_df["Start_Date"] = footfall_df["Reporting Period"].str.split("__").str[1].astype("datetime64[ns]")
    footfall_df["End_Date"] = footfall_df["Start_Date"].apply(lambda x: x + pd.offsets.MonthEnd(0))

    footfall_df = footfall_df.drop(["Reporting Period"], axis=1)

    return footfall_df


def extract_outcome_categories(df_outcomes: pd.DataFrame) -> pd.DataFrame:
    """
    Extract unique Outcome rows from Outcome Data and map to categories.

    Input dataframe is "Outcomes" DataFrame as extracted from "Towns Fund reporting template".

    :param df_outcomes: DataFrame containing extracted outcome data.
    :return: A new DataFrame containing unique extracted outcomes mapped to categories.
    """
    df_outcomes = pd.DataFrame(df_outcomes["Outcome"]).drop_duplicates()
    df_outcomes.columns = pd.Index(["Outcome_Name"])

    # default (ie any outcomes not in the provided list are assumed to be "custom"
    df_outcomes["Outcome_Category"] = df_outcomes["Outcome_Name"].map(OUTCOME_CATEGORIES).fillna("Custom")

    return df_outcomes
