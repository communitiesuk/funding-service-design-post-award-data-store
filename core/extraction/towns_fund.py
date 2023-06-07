"""
Methods specifically for extracting data from Towns Fund reporting template (Excel Spreadsheet)
"""
from typing import Dict, Tuple

import numpy as np
import pandas as pd
from pandas.tseries.offsets import MonthEnd

from core.extraction.utils import convert_financial_halves, drop_empty_rows
from core.util import extract_postcodes


def ingest_towns_fund_data(df_ingest: pd.DataFrame) -> Tuple[Dict[str, pd.DataFrame], str]:
    """
    Extract data from Towns Fund Reporting Template into column headed Pandas DataFrames.

    :param df_ingest: DataFrame of parsed Excel data.
    :return: Dictionary of extracted "tables" as DataFrames, and str representing reporting period for the form
    """

    towns_fund_extracted = {"Place Details": extract_place_details(df_ingest["2 - Project Admin"])}
    project_lookup = extract_project_lookup(df_ingest["Project Identifiers"], towns_fund_extracted["Place Details"])
    programme_id = get_programme_id(df_ingest["Place Identifiers"], towns_fund_extracted["Place Details"])
    # append Programme ID onto "Place Details" DataFrame
    towns_fund_extracted["Place Details"]["Programme ID"] = programme_id
    towns_fund_extracted["Programme_Ref"] = extract_programme(towns_fund_extracted["Place Details"], programme_id)
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
    # TODO: add in Outcomes ref data (with placeholder for dict lookup as per Outputs)
    # TOdO: Switch existing hacky methods of end date calculation to use MonthEnd method
    reporting_period = df_ingest["1 - Start Here"].iloc[4, 1]

    return towns_fund_extracted, reporting_period


def extract_place_details(df_place: pd.DataFrame) -> pd.DataFrame:
    """
    Extract place information from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Project work sheet, parsed as dataframe.

    :param df_place: Input DataFrame containing data.
    :return: Extracted DataFrame containing place detail data.
    """

    # strip out everything other than "SECTION A..." in spreadsheet.
    df_place = df_place.iloc[5:20, 2:5]

    # rename col headers for ease
    df_place.columns = [0, 1, 2]

    # fill in blank (merged) cells
    field_names_first = [x := y if y is not np.nan else x for y in df_place[0]]  # noqa: F841,F821

    df_place[0] = field_names_first
    df_place.columns = ["Question", "Answer", "Indicator"]

    df_place = df_place.reset_index(drop=True)
    return df_place


def extract_project_lookup(df_lookup: pd.DataFrame, df_place: pd.DataFrame) -> dict:
    """
    Extract relevant project code lookups for the current ingest instance.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Project Identifiers work sheet, parsed as dataframe.

    :param df_lookup: The input DataFrame containing project data.
    :param df_place: Extracted place_names DataFrame.
    :return: Dict of project_id's mapped to project names for this ingest. .
    """
    fund_type = df_place.loc[
        df_place["Question"] == "Are you filling this in for a Town Deal or Future High Street Fund?"
    ]["Indicator"].values[0]
    place_name = df_place.loc[df_place["Question"] == "Please select your place name"]["Indicator"].values[0]

    # fetch either "Town Deal" or "Future High Streets Fund" project_id lookup table
    df_lookup = df_lookup.iloc[1:, 1:4] if fund_type == "Town_Deal" else df_lookup.iloc[1:295, 8:11]
    df_lookup = df_lookup.rename(columns=df_lookup.iloc[0]).loc[2:]

    # filter on current place / programme and convert to dict
    df_lookup = df_lookup.loc[df_lookup["Town "] == place_name]
    project_lookup = dict(zip(df_lookup["Project Name "], df_lookup["Unique Project Identifier"]))
    return project_lookup


def get_programme_id(df_lookup: pd.DataFrame, df_place: pd.DataFrame) -> str:
    """
    Calculate programme code for the current ingest instance.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Place Identifiers work sheet, parsed as dataframe.

    :param df_lookup: The input DataFrame containing place id data.
    :param df_place: Extracted place_names DataFrame.
    :return: programme code.
    """
    fund_type = df_place.loc[
        df_place["Question"] == "Are you filling this in for a Town Deal or Future High Street Fund?"
    ]["Indicator"].values[0]
    place_name = df_place.loc[df_place["Question"] == "Please select your place name"]["Indicator"].values[0]

    # fetch either "Town Deal" or "Future High Streets Fund" place name/code lookup table
    df_lookup = df_lookup.iloc[1:, 1:3] if fund_type == "Town_Deal" else df_lookup.iloc[1:73, 4:6]
    df_lookup.columns = ["place", "code"]

    prefix = {
        "Town_Deal": "TD",
        "Future_High_Street_Fund": "HS",
    }[fund_type]
    code = df_lookup.loc[df_lookup["place"] == place_name]["code"].values[0]

    return "-".join([prefix, code])


def extract_programme(df_place: pd.DataFrame, programme_id: str) -> pd.DataFrame:
    """
    Extract programme row from ingest Data.

    :param df_place: Extracted place information.
    :param programme_id:
    :return: A new DataFrame containing the extracted programme.
    """
    org_field = "Grant Recipient:\n(your organisation's name)"
    df_programme = pd.DataFrame.from_dict(
        {
            "Programme ID": programme_id,
            "Programme Name": [
                df_place.loc[df_place["Question"] == "Please select your place name"]["Indicator"].values[0]
            ],
            "FundType_ID": programme_id.split("-")[0],
            "Organisation Name": [df_place.loc[df_place["Question"] == org_field]["Indicator"].values[0]],
        }
    )

    return df_programme


def extract_organisation(df_place: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Organisation ref data (1 row) from ingest data.

    :param df_place: Extracted place information.
    :return: A new DataFrame containing the extracted organisation info.
    """
    # TODO: Organisation currently set to None, as we have no robust way of ingesting / tracking this at the moment
    org_field = "Grant Recipient:\n(your organisation's name)"
    df_org = pd.DataFrame.from_dict(
        {
            "Organisation": [df_place.loc[df_place["Question"] == org_field]["Indicator"].values[0]],
            "Geography": None,
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
    df_project = df_project.iloc[23:45, 4:]

    # in first header row, replace empty strings with preceding value.
    header_row_1 = [x := y if y is not np.nan else x for y in df_project.iloc[0]]  # noqa: F841,F821
    # replace NaN with ""
    header_row_2 = [field if field is not np.nan else "" for field in list(df_project.iloc[1])]
    # zip together headers (deals with merged cells issues)
    header_row_combined = ["__".join([x, y]).rstrip("_") for x, y in zip(header_row_1, header_row_2)]
    # apply header to df with top rows stripped
    df_project = pd.DataFrame(df_project.values[2:], columns=header_row_combined)

    df_project = drop_empty_rows(df_project, "Project Name")
    df_project = df_project.reset_index(drop=True)

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
    df_project["Postcodes"] = df_project.apply(
        lambda row: ",".join(extract_postcodes(row["Locations"])), axis=1
    )  # TODO: keep as a list and store as array of strings in db (not supported by SQLite)
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
    df_data = df_data.iloc[5:12, 2:4]
    df_data.columns = ["Question", "Answer"]
    df_data = df_data.reset_index(drop=True)
    df_data["Programme ID"] = programme_id
    return df_data


def extract_project_progress(df_data: pd.DataFrame, project_lookup: dict) -> pd.DataFrame:
    """
    Extract Project progress rows from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Programme Progress work sheet, parsed as dataframe.

    :param df_data: The input DataFrame containing project data.
    :param project_lookup: Dict of project_name / project_id mappings for this ingest.
    :return: A new DataFrame containing the extracted project progress rows.
    """
    df_data = df_data.iloc[17:38, 2:13]
    df_data = df_data.rename(columns=df_data.iloc[0]).iloc[1:]
    df_data = drop_empty_rows(df_data, "Project name")
    df_data = df_data.reset_index(drop=True)
    df_data["Project ID"] = df_data["Project name"].map(project_lookup)

    # rename and drop columns to match "load" mappings
    df_data = df_data.rename(
        columns={
            "Start Date -\n mmm/yy (e.g. Dec-22)": "Start Date",
            "Completion Date -\n mmm/yy (e.g. Dec-22)": "Completion Date",
        }
    )
    df_data = df_data.drop(["Project name"], axis=1)

    return df_data


def extract_funding_questions(df_input: pd.DataFrame, programme_id: str) -> pd.DataFrame:
    """
    Extract funding questions data from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Funding Profiles work sheet, parsed as dataframe.

    :param df_input: The input DataFrame containing funding profiles data.
    :param programme_id: Programme id for this ingest.
    :return: A new DataFrame containing the extracted funding questions.
    """
    header_row = ["Question", "Indicator", "Response", "Guidance Notes"]
    df_input = df_input.iloc[12:19, 2:13].dropna(axis=1, how="all")

    # first row is different, manually extract
    fund_questions_df = pd.DataFrame(
        [[df_input.iloc[1, 0], np.nan, df_input.iloc[1, 1], df_input.iloc[1, 4]]], columns=header_row
    )

    # flatten 2-axis table into rows
    for _, row in df_input.iloc[2:].iterrows():
        temp_rows_df = pd.DataFrame(columns=header_row)
        for idx, col in enumerate(df_input.iloc[0, 1:4]):
            temp_rows_df = temp_rows_df.append(
                pd.DataFrame([[list(row)[0], col, list(row)[idx + 1], list(row)[4]]], columns=header_row)
            )
        fund_questions_df = fund_questions_df.append(temp_rows_df)

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
    df_input = df_input.iloc[31:, 2:26]
    header = ["Project name", "Comment"]
    df_fund_comments = pd.DataFrame(columns=header)

    for idx in range(len(project_lookup)):
        line_idx = 28 * idx
        current_project = df_input.iloc[line_idx, 0].split(": ")[1]
        comment = df_input.iloc[line_idx + 26, 0]
        fund_row = pd.DataFrame([[current_project, comment]], columns=header)
        df_fund_comments = df_fund_comments.append(fund_row)

    df_fund_comments["Project ID"] = df_fund_comments["Project name"].map(project_lookup)

    df_fund_comments = df_fund_comments.drop(["Project name"], axis=1)
    df_fund_comments = df_fund_comments.reset_index(drop=True)
    return df_fund_comments


def extract_funding_data(df_input: pd.DataFrame, project_lookup: dict) -> pd.DataFrame:
    """
    Extract fundin data (excluding comments) from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Funding Profiles work sheet, parsed as dataframe.

    :param df_input: The input DataFrame containing funding profiles data.
    :param project_lookup: Dict of project_name / project_id mappings for this ingest.
    :return: A new DataFrame containing the extracted funding data.
    """
    df_input = df_input.iloc[31:, 2:25]

    header_prefix = ["Funding Source Name", "Funding Source Type", "Secured"]
    # construct header rows out of 3 rows (merged cells), and add to empty init dataframe
    header_row_1 = [x := y if y is not np.nan else x for y in df_input.iloc[2, 3:]]  # noqa: F841,F821
    header_row_2 = [field if field is not np.nan else "" for field in list(df_input.iloc[3, 3:])]
    header_row_3 = [field if field is not np.nan else "" for field in list(df_input.iloc[4, 3:])]
    header_row_combined = [
        "__".join([x, y, z]).rstrip("_") for x, y, z in zip(header_row_1, header_row_2, header_row_3)
    ]
    header = header_prefix + header_row_combined
    header.append("Project Name")
    df_funding = pd.DataFrame()

    for idx in range(len(project_lookup)):
        line_idx = 28 * idx
        current_project = df_input.iloc[line_idx, 0].split(": ")[1]

        # Extract only pertinent parts of each subsection
        current_profile = df_input.iloc[line_idx + 5 : line_idx + 8].append(df_input.iloc[line_idx + 9 : line_idx + 11])
        # Add "Towns Fund" as Funding Source value for 1st 5 (mandatory) sources for each project.
        current_profile.iloc[:, 1] = "Towns Fund"
        current_profile = current_profile.append(df_input.iloc[line_idx + 17 : line_idx + 22])

        # Add current project (for iteration), lookup ID and add to another col.
        current_profile[""] = current_project
        current_profile.columns = header
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
        df_funding = df_funding.append(current_profile)

    # drop spare rows from ingest form (ie ones with no "Ingest source name" filled out.
    df_funding = drop_empty_rows(df_funding, "Funding Source Name")

    # unpivot the table around reporting periods/spend, and sort
    df_funding = pd.melt(
        df_funding,
        id_vars=list(df_funding.columns[:4]),
        var_name="Reporting Period",
        value_name="Spend for Reporting Period",
    )
    df_funding.sort_values(["Project ID", "Funding Source Name"], inplace=True)

    # hacky (but effective) methods to extract "Reporting Period" & "Actual / Forecast" columns
    # Regex everything after "__" in string
    df_funding["Actual / Forecast"] = df_funding["Reporting Period"].str.extract(r".*__(.*)")
    df_funding["Actual / Forecast"].fillna(np.nan, inplace=True)
    df_funding["Reporting Period"] = [
        x.split(" (£s)__")[1][:3] + x[17:22] if "__" in x else x for x in df_funding["Reporting Period"]
    ]

    df_funding = convert_financial_halves(df_funding, "Reporting Period")

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
    df_psi = df_psi.iloc[11:31, 3:]
    headers = [
        "Project name",
        "Total Project Value",
        "Townsfund Funding",
        "Private Sector Funding Required",
        "Private Sector Funding Secured",
        "gap",
        "Additional Comments",
    ]
    df_psi.columns = headers
    df_psi = drop_empty_rows(df_psi, "Project name")
    df_psi = df_psi.reset_index(drop=True)
    df_psi.insert(0, "Project ID", df_psi["Project name"].map(project_lookup))
    df_psi = df_psi.drop(["gap", "Project name"], axis=1)
    return df_psi


def extract_risks(df_risk: pd.DataFrame, project_lookup: dict, programme_id: str) -> pd.DataFrame:
    """
    Extract Programme specific risk register rows from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Risk Register work sheet, parsed as dataframe.

    :param df_risk: The input DataFrame containing risk data.
    :param project_lookup: Dict of project_name / project_id mappings for this ingest.
    :param programme_id: ID of the programme for this ingest
    :return: A new DataFrame containing the extracted programme/risk rows.
    """
    df_risk_programme = df_risk.iloc[8:13, 2:-1]
    df_risk_programme = df_risk_programme.rename(columns=df_risk_programme.iloc[0]).iloc[2:]
    df_risk_programme.insert(0, "Project ID", np.nan)
    df_risk_programme.insert(0, "Programme ID", programme_id)

    df_risk_all = df_risk_programme.append(extract_project_risks(df_risk, project_lookup))

    df_risk_all.drop(["Pre-mitigated Raw Total Score", "Post-mitigated Raw Total Score"], axis=1, inplace=True)
    df_risk_all.columns = [
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

    df_risk_all = drop_empty_rows(df_risk_all, "RiskName")
    df_risk_all = df_risk_all.reset_index(drop=True)
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
    df_input = df_input.iloc[17:, 2:-1]

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
        project_risks = df_input.iloc[line_idx + 4 : line_idx + 7]
        project_risks[""] = current_project
        project_risks.columns = risk_header
        risk_df = risk_df.append(project_risks)

    risk_df = risk_df.reset_index(drop=True)

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

    df_input = df_input.iloc[14:, 2:-1]

    # construct header rows out of 3 rows (merged cells), and add to empty init dataframe
    header_row_1 = [x := y if y is not np.nan else x for y in df_input.iloc[3]]  # noqa: F841,F821
    header_row_2 = [field if field is not np.nan else "" for field in list(df_input.iloc[5])]
    header_row_3 = [field if field is not np.nan else "" for field in list(df_input.iloc[6])]
    header_row_combined = [
        "__".join([x, y, z]).rstrip("_") for x, y, z in zip(header_row_1, header_row_2, header_row_3)
    ]
    header_row_combined.append("Project Name")
    outputs_df = pd.DataFrame()

    # iterate over project sections, based on number of projects.
    for idx in range(len(project_lookup)):
        line_idx = 38 * idx

        if idx >= 1:  # hacky fix to allow for hidden line part way through section for project 1
            line_idx += 1

        current_project = df_input.iloc[line_idx, 0].split(": ")[1]

        if idx >= 1:  # hacky fix to allow for hidden line part way through section for project 1
            line_idx -= 1

        # combine extracted sections for each sub-table, add column headers
        project_outputs = (
            df_input.iloc[line_idx + 8 : line_idx + 11]
            .append(df_input.iloc[line_idx + 12 : line_idx + 27])
            .append(df_input.iloc[line_idx + 28 : line_idx + 38])
        )
        project_outputs[""] = current_project
        project_outputs.columns = header_row_combined

        project_outputs = drop_empty_rows(project_outputs, "Indicator Name")
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

        outputs_df = outputs_df.append(project_outputs)

    # unpivot the table around reporting periods/output measurable, and sort
    outputs_df = pd.melt(
        outputs_df,
        id_vars=list(outputs_df.columns[:4]),
        var_name="Reporting Period",
        value_name="Amount",
    )
    outputs_df.sort_values(["Project ID", "Reporting Period"], inplace=True)

    # hacky (but effective) methods to extract "Reporting Period" & "Actual / Forecast" columns
    # Regex everything after "__" in string
    outputs_df["Actual / Forecast"] = outputs_df["Reporting Period"].str.extract(r".*__(.*)")
    outputs_df["Actual / Forecast"].fillna(np.nan, inplace=True)
    outputs_df["Reporting Period"] = [x[24:27] + x[17:22] if "__" in x else x for x in outputs_df["Reporting Period"]]

    outputs_df = convert_financial_halves(outputs_df, "Reporting Period")
    outputs_df = outputs_df.reset_index(drop=True)
    return outputs_df


def extract_output_categories(df_outputs: pd.DataFrame) -> pd.DataFrame:
    """
    Extract unique Output rows from Output Data and map to categories.

    Input dataframe is "Outputs" DataFrame as extracted from "Towns Fund reporting template".

    :param df_outputs: DataFrame containing extracted output data.
    :return: A new DataFrame containing unique extracted outputs mapped to categories.
    """
    df_outputs = pd.DataFrame(df_outputs["Output"]).drop_duplicates()
    df_outputs.columns = ["Output Name"]

    # TODO: add a lookup to a dict of outputs to categories, and map to this column. Default (get) ~ "custom"
    df_outputs["Output Category"] = np.nan
    return df_outputs


def combine_outcomes(df_input: pd.DataFrame, project_lookup: dict, programme_id: str) -> pd.DataFrame:
    """
    Extract different outcome types from DataFrame and combine into a single DataFrame

    :param df_input: The input DataFrame containing outcomes data.
    :param project_lookup: Dict of project_name / project_id mappings for this ingest.
    :param programme_id: ID of the programme for this ingest
    :return: A new DataFrame containing the combined project outcome rows.
    """
    df_outcomes = extract_outcomes(df_input, project_lookup, programme_id)
    df_outcomes = df_outcomes.append(extract_footfall_outcomes(df_input, project_lookup, programme_id))
    return df_outcomes


def extract_outcomes(df_input: pd.DataFrame, project_lookup: dict, programme_id: str) -> pd.DataFrame:
    """
    Extract Outcome rows from a DataFrame.

    This includes all Outputs except "Footfall Indicator" (extracted separately)

    Input dataframe is parsed from Excel spreadsheet: "Towns Fund reporting template".
    Specifically Projects Outputs work sheet, parsed as dataframe.

    :param df_input: The input DataFrame containing outcomes data.
    :param project_lookup: Dict of project_name / project_id mappings for this ingest.
    :param programme_id: ID of the programme for this ingest
    :return: A new DataFrame containing the extracted project outcome rows.
    """
    df_input = df_input.iloc[14:, 1:]

    header_row_1 = list(df_input.iloc[0])
    header_row_2 = [field if field is not np.nan else "" for field in list(df_input.iloc[1])]
    header_row_combined = ["__".join([x, y]).rstrip("_") for x, y in zip(header_row_1, header_row_2)]

    outcomes_df = pd.DataFrame(df_input.values[6:26], columns=header_row_combined)
    outcomes_df = outcomes_df.append(pd.DataFrame(df_input.values[27:37], columns=header_row_combined))
    outcomes_df = drop_empty_rows(outcomes_df, "Indicator Name")

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
    )
    outcomes_df.sort_values(["Project ID", "Reporting Period"], inplace=True)

    # split out Actual or Forecast values
    outcomes_df["Actual/Forecast"] = outcomes_df["Reporting Period"].str.split("__").str[1]
    # split out start and end dates for financial years
    outcomes_df["Start_Date"] = (outcomes_df["Reporting Period"].str[15:19] + "-04-01").astype("datetime64[ns]")
    outcomes_df["End_Date"] = (
        (outcomes_df["Reporting Period"].str[15:19].astype("int") + 1).astype("str") + "-03-31"
    ).astype("datetime64[ns]")

    outcomes_df = outcomes_df.drop(["Reporting Period"], axis=1)

    outcomes_df = outcomes_df.reset_index(drop=True)

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
    df_input = df_input.iloc[52:, 1:]

    # Build the header. It is very long, and calculated dynamically, as the values are dynamically generated in Excel
    header = list(df_input.iloc[2, :2].append(df_input.iloc[7, :2]))

    # within each footfall section data/header is spread over 6 lines, each 5 cells apart
    for year_idx in range(0, 30, 5):
        header_monthly_row_1 = [
            x := y if y is not np.nan else x for y in df_input.iloc[(year_idx + 2), 2:-1]  # noqa: F841,F821
        ]
        header_monthly_row_2 = [str(field) for field in df_input.iloc[(year_idx + 4), 2:-1]]
        header_monthly_row_3 = list(df_input.iloc[year_idx + 5, 2:-1])
        header_monthly_combined = [
            "__".join([x, y, z]).rstrip("_")
            for x, y, z in zip(header_monthly_row_1, header_monthly_row_2, header_monthly_row_3)
        ]
        header.extend(header_monthly_combined)

    footfall_df = pd.DataFrame(columns=header)

    # there is a max of 15 possible footfall outcome sections in spreadsheet, each 32 lines apart
    for footfall_idx in range(0, (15 * 32), 32):
        footfall_instance = df_input.iloc[footfall_idx + 6, :2].append(df_input.iloc[footfall_idx + 11, :2])

        # within each footfall section data is spread over 6 lines, each 5 cells apart
        for year_idx in range(footfall_idx, footfall_idx + 30, 5):
            footfall_instance = footfall_instance.append(df_input.iloc[(year_idx + 6), 2:-1])

        footfall_instance = pd.DataFrame(footfall_instance).T
        footfall_instance.columns = header
        footfall_df = footfall_df.append(footfall_instance)

    # assuming that no project id (or "multiple") is not to be ingested
    footfall_df = drop_empty_rows(footfall_df, "Relevant Project(s)")

    # TODO: These cells not "locked" in Excel sheet. Assuming (from context of spreadsheet) they should be.
    # TODO: Hard-coding here as a precaution (to prevent un-mappable data ingest)
    footfall_df["Indicator Name"] = "Change in footfall"
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
    )
    footfall_df.sort_values(["Project ID", "Reporting Period"], inplace=True)

    # split out Actual or Forecast values
    footfall_df["Actual/Forecast"] = footfall_df["Reporting Period"].str.split("__").str[-1]
    # split out start and end dates for months of financial years
    footfall_df["Start_Date"] = footfall_df["Reporting Period"].str.split("__").str[1].astype("datetime64[ns]")
    footfall_df["End_Date"] = footfall_df["Start_Date"] + MonthEnd(0)

    footfall_df = footfall_df.drop(["Reporting Period"], axis=1)

    footfall_df = footfall_df.reset_index(drop=True)
    return footfall_df


def extract_outcome_categories(df_outcomes: pd.DataFrame) -> pd.DataFrame:
    """
    Extract unique Outcome rows from Outcome Data and map to categories.

    Input dataframe is "Outcomes" DataFrame as extracted from "Towns Fund reporting template".

    :param df_outcomes: DataFrame containing extracted outcome data.
    :return: A new DataFrame containing unique extracted outcomes mapped to categories.
    """
    df_outcomes = pd.DataFrame(df_outcomes["Outcome"]).drop_duplicates()
    df_outcomes.columns = ["Outcome_Name"]

    # TODO: add a lookup to a dict of outcomes to categories, and map to this column. Default (get) ~ "custom"
    df_outcomes["Outcome_Category"] = np.nan
    return df_outcomes
