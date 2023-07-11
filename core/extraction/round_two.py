"""
Methods specifically for extracting data from Round 2 Funding data, historical data spreadsheet.
"""
import re
from datetime import datetime, timedelta
from typing import Dict

import numpy as np
import pandas as pd

from core.const import FundTypeIdEnum

# isort: off
from core.extraction.utils import convert_financial_halves, datetime_excel_to_pandas

# isort: on
from core.util import extract_postcodes


def ingest_round_two_data(df_ingest: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Extract data from Consolidated Round 2 data spreadsheet into column headed Pandas DataFrames.

    :param df_ingest: DataFrame of parsed Excel data - specifically sheet "December 2022"
    :return: Dictionary of extracted "tables" as DataFrames
    """

    # Add programme and submission id's to every row
    df_ingest["Programme ID"] = df_ingest["Tab 2 - Project Admin - Index Codes"].str.extract("^([^-]+-[^-]+)")
    df_ingest["Submission ID"] = "S-R01-" + df_ingest["Index"].astype(str)

    extracted_data = dict()
    extracted_data["Submission_Ref"] = extract_submission_data(df_ingest)
    extracted_data["Place Details"] = extract_place_details(df_ingest)
    extracted_data["Project Details"] = extract_project(df_ingest)
    extracted_data["Programme_Ref"] = extract_programme(df_ingest)
    extracted_data["Organisation_Ref"] = extract_organisation(df_ingest)
    extracted_data["Programme Progress"] = extract_programme_progress(df_ingest)
    extracted_data["Project Progress"] = extract_project_progress(df_ingest)
    extracted_data["Funding Questions"] = extract_funding_questions(df_ingest)
    extracted_data["Funding"] = extract_funding_data(df_ingest)
    # Note: No data fields for funding comments in Round 2 data-set
    # Note: No data for PSI in Round 2 data-set
    extracted_data["Outputs"] = extract_outputs(df_ingest)

    extracted_data["df_outcomes_extracted"] = extract_outcomes(df_ingest)

    # TODO: some project ID's are "multiple". Add ref to programme.
    extracted_data["df_outcomes_footfall_extracted"] = extract_footfall_outcomes(df_ingest)

    # TODO: some rows have no risk name and other non-nullable fields. Add "Field not provided." to these?
    extracted_data["df_programme_risks_extracted"] = extract_programme_risks(df_ingest)
    extracted_data["df_project_risks_extracted"] = extract_project_risks(df_ingest)

    return extracted_data


def extract_submission_data(df_submission: pd.DataFrame) -> pd.DataFrame:
    """
    Extract form submission information/meta from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    :param df_submission: Input DataFrame containing consolidated data.
    :return: Extracted DataFrame containing submission info data.
    """
    # column headers have specific place names in for this section
    df_submission = df_submission[
        [
            "24/01/2023 15:49:40",
            "TF Reporting Template - HS - Barnsley - 130123.xlsx",
            "Submission ID",
        ]
    ]
    df_submission = df_submission.drop_duplicates(
        subset=["TF Reporting Template - HS - Barnsley - 130123.xlsx"], keep="first"
    )
    # build the submission id from standard prefix plus the index number in the data
    df_submission["reporting_round"] = 1
    df_submission["Reporting Period Start"] = datetime.strptime("1 April 2022", "%d %B %Y")
    df_submission["Reporting Period End"] = datetime.strptime("30 September 2022", "%d %B %Y")

    # set column headers to match mapping
    column_headers = [
        "Submission Date",
        "submission_filename",
        "Submission ID",
        "Reporting Round",
        "Reporting Period Start",
        "Reporting Period End",
    ]
    df_submission.columns = column_headers
    df_submission.reset_index(drop=True, inplace=True)
    return df_submission


def extract_place_details(df_input: pd.DataFrame) -> pd.DataFrame:
    """
    Extract place detail information from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    :param df_input: Input DataFrame containing consolidated data.
    :return: Extracted DataFrame containing place info data.
    """
    df_place = df_input.iloc[:, 10:25]
    df_place = join_to_programme(df_input, df_place)
    df_place = df_place.drop_duplicates()

    # un-pivot the data
    df_place = pd.melt(df_place, id_vars=["Submission ID", "Programme ID"], var_name="Question", value_name="Answer")
    df_place.sort_values(["Programme ID", "Question"], inplace=True)

    # hacky direct lookups to save dev time
    indicator_lookups = {
        "Tab 2 - Project Admin - TD / FHSF": "Please select from the drop list provided",
        "Tab 2 - Project Admin - Place Name": "Please select from the drop list provided",
        "Tab 2 - Project Admin - Grant Recipient Organisation": "Organisation Name",
        "Tab 2 - Project Admin - Single Conact Name ": "Name",
        "Tab 2 - Project Admin - Single Conact Email ": "Email",
        "Tab 2 - Project Admin - Single Conact Telephone ": "Telephone",
        "Tab 2 - Project Admin - Programme SRO Name": "Name",
        "Tab 2 - Project Admin - Programme SRO Email": "Email",
        "Tab 2 - Project Admin - Programme SRO Telephone": "Telephone",
        "Tab 2 - Project Admin - S151 Officer Name": "Name",
        "Tab 2 - Project Admin - S151 Officer Email": "Email",
        "Tab 2 - Project Admin - S151 Officer Telephone": "Telephone",
        "Tab 2 - Project Admin - M&E Contact Name": "Name",
        "Tab 2 - Project Admin - M&E Contact Email": "Email",
        "Tab 2 - Project Admin - M&E Contact Telephone": "Telephone",
    }
    question_lookups = {
        "Tab 2 - Project Admin - TD / FHSF": "Are you filling this in for a Town Deal or Future High Street Fund?",
        "Tab 2 - Project Admin - Place Name": "Please select your place name",
        "Tab 2 - Project Admin - Grant Recipient Organisation": "Grant Recipient:",
        "Tab 2 - Project Admin - Single Conact Name ": "Grant Recipient's Single Point of Contact",
        "Tab 2 - Project Admin - Single Conact Email ": "Grant Recipient's Single Point of Contact",
        "Tab 2 - Project Admin - Single Conact Telephone ": "Grant Recipient's Single Point of Contact",
        "Tab 2 - Project Admin - Programme SRO Name": "Programme Senior Responsible Owner",
        "Tab 2 - Project Admin - Programme SRO Email": "Programme Senior Responsible Owner",
        "Tab 2 - Project Admin - Programme SRO Telephone": "Programme Senior Responsible Owner",
        "Tab 2 - Project Admin - S151 Officer Name": "S151 Officer / Chief Finance Officer",
        "Tab 2 - Project Admin - S151 Officer Email": "S151 Officer / Chief Finance Officer",
        "Tab 2 - Project Admin - S151 Officer Telephone": "S151 Officer / Chief Finance Officer",
        "Tab 2 - Project Admin - M&E Contact Name": "Monitoring and Evaluation Contact",
        "Tab 2 - Project Admin - M&E Contact Email": "Monitoring and Evaluation Contact",
        "Tab 2 - Project Admin - M&E Contact Telephone": "Monitoring and Evaluation Contact",
    }
    df_place["Indicator"] = df_place["Question"].map(indicator_lookups)
    df_place["Question"] = df_place["Question"].map(question_lookups)

    df_place.reset_index(drop=True, inplace=True)
    return df_place


def extract_project(df_data: pd.DataFrame) -> pd.DataFrame:
    """
    Extract project rows from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    :param df_data: Input DataFrame containing consolidated data.
    :return: A new DataFrame containing the extracted project rows.
    """
    df_project = df_data.loc[
        :, "Tab 2 - Project Admin - Index Codes":"Tab 2 - Project Admin - Multiple Location - Lat/Long Coordinates"
    ]
    df_project = join_to_programme(df_data, df_project)

    single_postcode = "Tab 2 - Project Admin - Single Location - Postcode"
    multiple_postcode = "Tab 2 - Project Admin - Multiple Location - Postcode"

    # Leaving open-ended else, as there is an edge case with no multiplicity entry but a postcode in "multiple" section
    df_project["Locations"] = df_project.apply(
        lambda row: row[single_postcode]
        if row["Tab 2 - Project Admin - Single Location??"] == "Single"
        else row[multiple_postcode],
        axis=1,
    )
    df_project["Postcodes"] = df_project.apply(lambda row: ",".join(extract_postcodes(str(row["Locations"]))), axis=1)

    single_lat_long = "Tab 2 - Project Admin - Single Location - Lat/Long Coordinates"
    multiple_lat_long = "Tab 2 - Project Admin - Multiple Location - Lat/Long Coordinates"
    df_project["Lat/Long"] = df_project.apply(
        lambda row: row[single_lat_long]
        if row["Tab 2 - Project Admin - Single Location??"] == "Single"
        else row[multiple_lat_long],
        axis=1,
    )
    df_project = df_project.drop([single_postcode, multiple_postcode, single_lat_long, multiple_lat_long], axis=1)

    # replace default excel values (unselected option)
    df_project["Single or Multiple Locations"] = df_project["Tab 2 - Project Admin - Single Location??"].replace(
        "< Select >", np.nan
    )
    df_project["GIS Provided"] = df_project["Tab 2 - Project Admin - Multiple Location - GIS Map"].replace(
        "< Select >", np.nan
    )

    columns_to_rename = {
        "Tab 2 - Project Admin - Index Codes": "Project ID",
        "Tab 2 - Project Admin - Project Name": "Project Name",
        "Tab 2 - Project Admin - Primary Intervention Theme": "Primary Intervention Theme",
    }
    df_project.rename(columns=columns_to_rename, inplace=True)
    columns_to_drop = [
        "Tab 2 - Project Admin - Single Location??",
        "Tab 2 - Project Admin - Multiple Location - GIS Map",
    ]
    df_project = df_project.drop(columns_to_drop, axis=1)

    df_project.reset_index(drop=True, inplace=True)
    return df_project


def extract_programme(df_data: pd.DataFrame) -> pd.DataFrame:
    """
    Extract programme rows from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    :param df_data: Input DataFrame containing consolidated data.
    :return: A new DataFrame containing the extracted programme rows.
    """
    # get the pertinent columns
    df_programme = df_data[
        [
            "Programme ID",
            "Tab 2 - Project Admin - Place Name",
            "Tab 2 - Project Admin - TD / FHSF",
            "Tab 2 - Project Admin - Grant Recipient Organisation",
        ]
    ].drop_duplicates()

    # rename to match the mapping module
    df_programme.rename(
        columns={
            "Tab 2 - Project Admin - Place Name": "Programme Name",
            "Tab 2 - Project Admin - TD / FHSF": "FundType_ID",
            "Tab 2 - Project Admin - Grant Recipient Organisation": "Organisation",
        },
        inplace=True,
    )

    # Lookup fund type code from Enum (for consistency with validation)
    fund_type_lookup = {
        "Town_Deal": FundTypeIdEnum.TOWN_DEAL.value,
        "Future_High_Street_Fund": FundTypeIdEnum.HIGH_STREET_FUND.value,
    }
    df_programme["FundType_ID"] = df_programme["FundType_ID"].map(fund_type_lookup)

    df_programme.reset_index(drop=True, inplace=True)
    return df_programme


def extract_organisation(df_data: pd.DataFrame) -> pd.DataFrame:
    """
    Extract organisation rows from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    :param df_data: Input DataFrame containing consolidated data.
    :return: A new DataFrame containing the extracted organisation rows.
    """
    df_organisation = df_data[["Tab 2 - Project Admin - Grant Recipient Organisation"]].drop_duplicates()
    df_organisation.columns = ["Organisation"]
    # no information in data for this field
    df_organisation["Geography"] = np.nan

    df_organisation.reset_index(drop=True, inplace=True)
    return df_organisation


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
    # Map back to questions in the form: Assumption that these are the same as in Round 3 form.
    questions = {
        "A1": "How is your programme progressing against your original profile / forecast? ",
        "A2": "Please provide a progress update covering the 6 month reporting period",
        "A3": "What are the key challenges you are currently facing?\nPlease provide as much detail as possible",
        "A4": "What challenges do you expect to face in the next 6/12 months? (Please include timeframes)",
        "A5": "Please provide an update on your local evaluation activities",
        "A6": (
            "Please provide any key milestones which you would like to make us aware of for "
            "publicity purposes during the next quarter\n"
            "(e.g. first spade in the ground, designs complete, building fit out)"
        ),
        "A7": "If any support is required from the DLUHC TF team, please comment",
    }
    df_programme_progress.columns = [questions[column[-2:]] for column in df_programme_progress.columns]
    df_programme_progress = join_to_programme(df_data, df_programme_progress)
    df_programme_progress = df_programme_progress.dropna(
        subset=["How is your programme progressing against your original profile / forecast? "]
    )

    # un-pivot the data to match data model
    df_programme_progress = pd.melt(
        df_programme_progress, id_vars=["Submission ID", "Programme ID"], var_name="Question", value_name="Answer"
    )
    df_programme_progress.sort_values(["Submission ID", "Question"], inplace=True)

    df_programme_progress.reset_index(drop=True, inplace=True)
    return df_programme_progress


def extract_project_progress(df_data: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Project progress rows from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    Round 2, Project Progress data does not contain:
    - "Most Important Upcoming Comms Milestone" columns
    - "Project Adjustment Request Status" column

    :param df_data: Input DataFrame containing consolidated data.
    :return: A new DataFrame containing the extracted project progress rows.
    """
    index_1 = "Tab 3 - Programme Progress - Project Progress  Start Date"
    index_2 = "Tab 3 - Programme Progress - Project Progress Commentary"
    df_project_progress = df_data.loc[:, index_1:index_2]
    df_project_progress = join_to_project(df_data, df_project_progress)

    df_project_progress.columns = [
        "Submission ID",
        "Project ID",
        "Start Date",
        "Completion Date",
        "Project Delivery Status",
        "Delivery (RAG)",
        "Spend (RAG)",
        "Risk (RAG)",
        "Commentary on Status and RAG Ratings",
    ]

    # clean 2 x edge-case occurrences of date in string format
    df_project_progress["Start Date"] = df_project_progress["Start Date"].replace("01.07.2022", 44743)

    # convert Excel datetime to Python
    df_project_progress["Start Date"] = datetime_excel_to_pandas(df_project_progress["Start Date"])
    df_project_progress["Completion Date"] = datetime_excel_to_pandas(df_project_progress["Completion Date"])

    # some columns contain non-viable options for mandatory fields, clean these.
    cols_to_clean = [
        "Project Delivery Status",
        "Delivery (RAG)",
        "Spend (RAG)",
        "Risk (RAG)",
        "Commentary on Status and RAG Ratings",
    ]
    df_project_progress[cols_to_clean] = df_project_progress[cols_to_clean].replace(
        {
            0: np.nan,
            "0": np.nan,
            "< Select >": np.nan,
        }
    )

    # drop rows where all values ar empty
    df_project_progress = df_project_progress.dropna(
        subset=[
            "Start Date",
            "Completion Date",
            "Project Delivery Status",
            "Delivery (RAG)",
            "Spend (RAG)",
            "Risk (RAG)",
            "Commentary on Status and RAG Ratings",
        ],
        how="all",
    )
    # TODO: getting a lot of null values in non-nullable rows still. Check what TF want to do with these:
    #  1) Throw away (loss of partial data rows)
    #  2) Keep (need to change database, make sure validation is tight for R3)
    #  3) Get TF to fix spreadsheet

    # TODO: Update - TF to provide list of non-reportable projects to drop (this might cover these non-nulls)

    df_project_progress.reset_index(drop=True, inplace=True)
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
    # only Q1 and Q5 have guidance notes (but not consistently).
    df_funding_questions["Guidance Notes 1"] = df_funding_questions[
        "Tab 4 - Funding Profiles B - B1 Q1 - Guidance Notes"
    ]
    df_funding_questions["Guidance Notes 5"] = df_funding_questions[
        "Tab 4 - Funding Profiles B - B1 Q5 - Guidance Notes"
    ]

    # un-pivot the data
    df_funding_questions = pd.melt(
        df_funding_questions,
        id_vars=["Submission ID", "Programme ID", "Guidance Notes 1", "Guidance Notes 5"],
        var_name="question_col",
        value_name="Response",
    )

    # map of questions from the R3 ingest form, assumed these match Q1-6 in R2 data
    question_map = {
        "1": "Beyond these three funding types, have you received any payments for specific projects?",
        "2": "Please indicate how much of your allocation has been utilised (in £s)",
        "3": "Please confirm whether the amount utilised represents your entire allocation",
        "4": (
            "Please describe when funding was utilised and, "
            "if applicable, when any remaining funding will be utilised"
        ),
        "5": "Please select the option that best describes how the funding was, or will be, utilised",
        "6": "Please explain in detail how the funding has, or will be, utilised",
    }
    # map against Q no extracted from header string
    df_funding_questions["Question"] = df_funding_questions["question_col"].str[33].map(question_map)

    # combine guidance Notes, but ONLY for the relevant question sections.
    df_funding_questions["Guidance Notes"] = [
        row["Guidance Notes 1"]
        if row["Question"] == question_map["1"]
        else row["Guidance Notes 5"]
        if row["Question"] == question_map["5"]
        else np.nan
        for _, row in df_funding_questions.iterrows()
    ]

    # Strip "indicator" value from end of un-pivoted column headers
    df_funding_questions["Indicator"] = df_funding_questions["question_col"].str.extract(r".*- (.*)")

    # tidy-up, drop unwanted cols, replace non-entry values with nan.
    df_funding_questions = df_funding_questions.drop(["question_col", "Guidance Notes 1", "Guidance Notes 5"], axis=1)
    df_funding_questions["Response"] = df_funding_questions["Response"].replace(
        {
            0: np.nan,
            "0": np.nan,
            "< Select >": np.nan,
        }
    )
    # drop rows with "Guidance Notes" as value in indicator column (hang-over from melt)
    df_funding_questions.drop(
        df_funding_questions[df_funding_questions["Indicator"] == "Guidance Notes"].index, inplace=True
    )

    df_funding_questions.sort_values(["Submission ID", "Question", "Indicator"], inplace=True)
    df_funding_questions.reset_index(drop=True, inplace=True)
    return df_funding_questions


def extract_funding_data(df_input: pd.DataFrame) -> pd.DataFrame:
    """
    Extract funding data from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    :param df_input: Input DataFrame containing consolidated data.
    :return: A new DataFrame containing the extracted funding data.
    """
    index_1 = "Tab 4 - Funding Profiles C 1st Row - Pre-20/21 H1 - CDEL Utilised"
    index_2 = "Tab 4 - Funding Profiles C 8th Row - Grand Total - TF Funding Total"
    df_funding = df_input.loc[:, index_1:index_2]
    index_1 = "Tab 4 - Funding Profiles Other Funding Sources 1 -  Funding Source - OFS 1"
    index_2 = "Tab 4 - Funding Profiles Other Funding Sources 28 - Grand Total - OFS 5"
    df_funding = pd.concat([df_funding, df_input.loc[:, index_1:index_2]], axis=1)

    df_funding_data = pd.DataFrame()

    # Mandatory Funding source section
    # 21 cols per row for first 6 rows. drop rows 4.
    for idx in range(0, (21 * 6), 21):
        # idx 63 (4th funding source in spreadsheet) is a Total (we drop aggregations)
        if idx == 63:
            continue
        temp_df = df_funding.iloc[:, idx : idx + 21]
        # drop unwanted "totals" columns
        columns_to_drop = temp_df.columns[[3, 6, 9, 12, 15, 18, 20]]
        temp_df = temp_df.drop(columns_to_drop, axis=1)
        # add project/submission to each section
        temp_df = join_to_project(df_input, temp_df)
        # add funding source based on spreadsheet position
        temp_df["Funding Source Name"] = {
            0: (
                "Towns Fund CDEL which is being utilised on TF project related "
                "activity (For Town Deals, this excludes the 5% CDEL Pre-Payment)"
            ),
            21: "Town Deals 5% CDEL Pre-Payment",
            42: "How much of your CDEL forecast is contractually committed?",
            84: "Towns Fund RDEL Payment which is being utilised on TF project related activity",
            105: "How much of your RDEL forecast is contractually committed?",
        }[idx]

        # mandatory funding sources have hard-coded values in data model
        temp_df["Funding Source Type"] = "Towns Fund"
        temp_df["Secured"] = np.nan

        # these columns need consistently naming for melt (currently different per section).
        cols_to_rename = temp_df.columns[2:16]
        replacement_col_names = [
            "Before 20/21",
            "H1 20/21",
            "H2 20/21",
            "H1 21/22",
            "H2 21/22",
            "H1 22/23",
            "H2 22/23",
            "H1 23/24",
            "H2 23/24",
            "H1 24/25",
            "H2 24/25",
            "H1 25/26",
            "H2 25/26",
            "Beyond 25/26",
        ]
        financial_period_col_map = dict(zip(cols_to_rename, replacement_col_names))
        temp_df.rename(columns=financial_period_col_map, inplace=True)
        temp_df.rename(columns={"Tab 2 - Project Admin - Index Codes": "Project ID"}, inplace=True)

        df_funding_data = df_funding_data.append(temp_df)

    # Custom Funding source section
    # 24 cols per row for 5 rows. start index is 168. Error in spreadsheet col headers here (OFS2 starts at 2)
    for idx in range(168, 168 + (24 * 5), 24):
        temp_df = df_funding.iloc[:, idx : idx + 24]
        temp_df = join_to_project(df_input, temp_df)

        # drop unwanted "totals" columns
        columns_to_drop = temp_df.columns[[8, 11, 14, 17, 20, 23, 25]]
        temp_df = temp_df.drop(columns_to_drop, axis=1)

        # drop empty custom rows (ie all rows contain 0 or 0.0)
        temp_df = temp_df[(temp_df.iloc[:, 2:] != 0).any(axis=1)]

        temp_df = temp_df.loc[(temp_df != 0).any(axis=1)]

        # TODO: Secured column is labelled "unsecured" in R2 data sheet - queried with TF, do we need to switch?
        # all columns need consistently naming for melt (currently different per section).
        temp_df.columns = [
            "Submission ID",
            "Project ID",
            "Funding Source Name",
            "Funding Source Type",
            "Secured",
            "Before 20/21",
            "H1 20/21",
            "H2 20/21",
            "H1 21/22",
            "H2 21/22",
            "H1 22/23",
            "H2 22/23",
            "H1 23/24",
            "H2 23/24",
            "H1 24/25",
            "H2 24/25",
            "H1 25/26",
            "H2 25/26",
            "Beyond 25/26",
        ]

        df_funding_data = df_funding_data.append(temp_df)

    # un-pivot the data into financial period rows
    df_funding_data = pd.melt(
        df_funding_data,
        id_vars=[
            "Submission ID",
            "Project ID",
            "Funding Source Name",
            "Funding Source Type",
            "Secured",
        ],
        var_name="Reporting Period",
        value_name="Spend for Reporting Period",
    )
    df_funding_data.sort_values(["Project ID", "Funding Source Name"], inplace=True)

    df_funding_data = convert_financial_halves(df_funding_data, "Reporting Period")

    # not currently provided with Round 2 data
    df_funding_data["Actual/Forecast"] = df_funding_data.apply(get_actual_forecast, axis=1)

    df_funding_data.reset_index(drop=True, inplace=True)
    return df_funding_data


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

    # Method for relevant data per financial half
    def get_financial_halves(columns):
        pattern = r"\d{4}/\d{2}"
        exclusion_word = "Total"

        matching_values = [
            value
            for value in columns
            if (re.search(pattern, value) and exclusion_word not in value) or "Beyond" in value
        ]

        return matching_values

    # These are Submission ID and Project ID
    identifiers = df_outputs.iloc[:, 0:2]

    # This dict is all 28 outputs for each project
    df_dict = {
        "man 1": df_outputs.iloc[:, 3:25],
        "man 2": df_outputs.iloc[:, 25:47],
        "man 3": df_outputs.iloc[:, 47:69],
        "spe 1": df_outputs.iloc[:, 69:92],
        "spe 2": df_outputs.iloc[:, 92:115],
        "spe 3": df_outputs.iloc[:, 115:138],
        "spe 4": df_outputs.iloc[:, 138:161],
        "spe 5": df_outputs.iloc[:, 161:184],
        "spe 6": df_outputs.iloc[:, 184:207],
        "spe 7": df_outputs.iloc[:, 207:230],
        "spe 8": df_outputs.iloc[:, 230:253],
        "spe 9": df_outputs.iloc[:, 253:276],
        "spe 10": df_outputs.iloc[:, 276:299],
        "spe 11": df_outputs.iloc[:, 299:322],
        "spe 12": df_outputs.iloc[:, 322:345],
        "spe 13": df_outputs.iloc[:, 345:368],
        "spe 14": df_outputs.iloc[:, 368:391],
        "spe 15": df_outputs.iloc[:, 391:414],
        "cus 1": df_outputs.iloc[:, 414:436],
        "cus 2": df_outputs.iloc[:, 436:458],
        "cus 3": df_outputs.iloc[:, 458:480],
        "cus 4": df_outputs.iloc[:, 480:502],
        "cus 5": df_outputs.iloc[:, 502:524],
        "cus 6": df_outputs.iloc[:, 524:546],
        "cus 7": df_outputs.iloc[:, 546:568],
        "cus 8": df_outputs.iloc[:, 568:590],
        "cus 9": df_outputs.iloc[:, 590:612],
        "cus 10": df_outputs.iloc[:, 612:],
    }

    # Standardise all outputs to have the PKs + add extra col where needed
    for key, value in df_dict.items():
        df_dict[key] = pd.concat([identifiers, df_dict[key]], axis=1)
        if "spe" not in key:
            df_dict[key]["Additional Information"] = "0"

    # Pick output dataframe slice's columns to use for standardisation
    standardised_columns = df_dict["spe 1"].columns
    unpivoted_df = pd.DataFrame(columns=standardised_columns)

    # Rename all columns, so they will be standardised, then concat
    for key, value in df_dict.items():
        df_dict[key].columns = [
            standardised_columns[i] for i, c in enumerate(df_dict[key].columns) if i < len(standardised_columns)
        ]
        unpivoted_df = pd.concat([unpivoted_df, df_dict[key]], axis=0)

    financial_halves = get_financial_halves(unpivoted_df.columns)

    # Don't want to lose any data in the melt, so get all non-melting cols
    id_vars = unpivoted_df.columns.difference(financial_halves)

    # Get data for each financial half as its own row
    df_unpivoted_financial_halves = pd.melt(
        unpivoted_df,
        id_vars=id_vars,
        value_vars=financial_halves,
        value_name="Amount",
        var_name="financial_period",
    )

    df_unpivoted_financial_halves["financial_year"] = df_unpivoted_financial_halves["financial_period"].str.extract(
        r"(\d{4}/\d{2})"
    )

    # Define the UK financial year start and end dates
    financial_year_start = pd.to_datetime(
        df_unpivoted_financial_halves["financial_year"].str[:4] + "-04-01", format="%Y-%m-%d"
    )
    financial_year_end = financial_year_start + pd.DateOffset(years=1) - pd.DateOffset(days=1)

    # Create an empty list to store the new rows
    new_rows = []

    # Iterate over each row in the original dataframe
    for index, row in df_unpivoted_financial_halves.iterrows():
        if "Beyond" in row["financial_period"]:
            start_date = pd.Timestamp(year=2026, month=4, day=1)
            end_date = np.datetime64("NaT")
        elif "H1" in row["financial_period"]:
            start_date = financial_year_start[index]
            end_date = financial_year_start[index] + pd.DateOffset(months=6) - pd.DateOffset(days=1)
            # Halfway through the financial year
        else:
            start_date = financial_year_start[index] + pd.DateOffset(months=6)  # Start of the next half
            end_date = financial_year_end[index]

        new_rows.append(
            {
                "start_date": start_date,
                "end_date": end_date,
            }
        )

    temp_df = pd.DataFrame(new_rows)

    df_unpivoted_financial_halves["Start_Date"] = temp_df["start_date"]
    df_unpivoted_financial_halves["End_Date"] = temp_df["end_date"]

    # Now rename according to mapping, and remove unneeded cols
    final_cols = [
        "Submission ID",
        "Project ID",
        "Start_Date",
        "End_Date",
        "Output",
        "Unit of Measurement",
        "Actual/Forecast",
        "Amount",
        "Additional Information",
    ]

    df_outputs = df_unpivoted_financial_halves.rename(
        columns={
            "Tab 2 - Project Admin - Index Codes": "Project ID",
            "Tab 5 - Project Outputs - Project Specific Output 1 ": "Output",
            "Tab 5 - Project Outputs - Project Specific Output 1 Unit of Measurement": "Unit of Measurement",
            "Tab 5 - Project Outputs - Project Specific Output 1 Additional Information": "Additional Information",
        }
    )

    df_outputs["Actual/Forecast"] = df_outputs.apply(get_actual_forecast, axis=1)

    df_outputs = df_outputs[final_cols]

    # Where there is no Output, has not been selected on form, therefore drop
    df_outputs = df_outputs[(df_outputs["Output"] != "< Select >") & (df_outputs["Output"] != 0)]
    # both string "0" and int 0 populating additional info col
    df_outputs["Additional Information"] = df_outputs["Additional Information"].replace(0, np.nan).replace("0", np.nan)

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


def extract_footfall_outcomes(df_input: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Project Outcome rows from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    Un-flattens project data from 1 row per programme, to 1 row per project.
    Then, un-pivots project rows to 1 row per date-period/project combo (instead of 1 project row containing
    all the date cols).

    :param df_input: Input DataFrame containing consolidated data.
    :return: A new DataFrame containing the extracted footfall outcome data.
    """
    index_1 = "Tab 6 - Outcomes: Section C - Footfall Indicator 1 - Name"
    index_2 = "Tab 6 - Outcomes: Section C - Footfall Indicator 15 - March 2026"
    df_footfall = df_input.loc[:, index_1:index_2]

    # joined to programme, as all outcomes returned on first line for each ingest
    df_footfall = join_to_programme(df_input, df_footfall)

    # drop irrelevant rows - these contain no actual data
    df_footfall = df_footfall.dropna(subset=["Tab 6 - Outcomes: Section C - Footfall Indicator 1 - Name"])

    # new index with ref to footfall indicator No. stripped out
    new_index = df_footfall.iloc[:, :3].columns.str.split("- ", expand=True).get_level_values(-1)
    new_index = new_index.append(df_footfall.iloc[:, 3:79].columns.str.split("- ", expand=True).get_level_values(-1))

    df_unpivot = pd.DataFrame()
    # 76 cols per section, 15 sections. 3 prefix columns.
    for idx in range(3, (15 * 76) + 3, 76):
        temp_cols = df_footfall.iloc[:, idx : idx + 76]
        # re-join each of the 15 sections to the "programme" level info
        df_prog_id = df_footfall.loc[
            :, "Tab 2 - Project Admin - TD / FHSF":"Tab 2 - Project Admin - Grant Recipient Organisation"
        ]
        temp_cols = pd.concat([df_prog_id, temp_cols], axis=1)
        temp_cols.columns = new_index

        # unpivot table, split month cols into var column, corresponding values into val col.
        temp_cols = pd.melt(temp_cols, id_vars=list(new_index[:7]), var_name="Month", value_name="Amount")
        temp_cols.sort_values(["Relevant Project", "Geography"], inplace=True)
        df_unpivot = df_unpivot.append(temp_cols)

        # TODO: Some project fields are empty, some are 0, and some of these have values in. Map to programme

    df_unpivot.reset_index(drop=True, inplace=True)
    # Convert "Date" column values into datetime objects start and end dates (for the given month)
    df_unpivot[["Start_Date", "End_Date"]] = df_unpivot["Month"].apply(lambda x: pd.Series(convert_date(x)))
    return df_unpivot


def extract_programme_risks(df_input: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Programme level risks from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".
    Un-flattens project data from 1 row per programme, to 1 row per project.

    :param df_input: Input DataFrame containing consolidated data.
    :return: A new DataFrame containing the extracted programme risks.
    """
    index_1 = "Tab 7 - Risks: Section A - Programme Risk 1 - Name"
    index_2 = "Tab 7 - Risks: Section A - Programme Risk 3 - Risk Owner/Role"
    df_risks = df_input.loc[:, index_1:index_2]
    df_risks = join_to_programme(df_input, df_risks)

    headers = df_risks.iloc[:, :3].columns.str.split("- ", expand=True).get_level_values(-1)
    headers = headers.append(df_risks.iloc[:, 3:17].columns.str.split("- ", expand=True).get_level_values(-1))

    # drop irrelevant rows - these contain no actual data. 3 cols in subset, due to edge-cases in dataset
    df_risks = df_risks.dropna(
        subset=[
            "Tab 7 - Risks: Section A - Programme Risk 1 - Name",
            "Tab 7 - Risks: Section A - Programme Risk 1 - Category",
            "Tab 7 - Risks: Section A - Programme Risk 1 - Pre-mitigated Impact",
        ],
        how="all",
    )

    df_risks_out = pd.DataFrame()
    # 14 cols per section, 3 sections. 3 prefix columns.
    for idx in range(3, (3 * 14) + 3, 14):
        temp_cols = df_risks.iloc[:, idx : idx + 14]
        df_prog_id = df_risks.loc[
            :, "Tab 2 - Project Admin - TD / FHSF":"Tab 2 - Project Admin - Grant Recipient Organisation"
        ]
        temp_cols = pd.concat([df_prog_id, temp_cols], axis=1)
        temp_cols.columns = headers
        df_risks_out = df_risks_out.append(temp_cols)

    # remove all rows with 0's for data EXCEPT particular edge case in data
    df_risks_out = df_risks_out[(df_risks_out["Name"] != 0) & (df_risks_out["Pre-mitigated Impact"] != 0)]
    df_risks_out = df_risks_out.dropna(subset=["Name", "Pre-mitigated Impact"], how="all")

    df_risks_out.sort_values(["Grant Recipient Organisation", "Name"], inplace=True)
    df_risks_out.reset_index(drop=True, inplace=True)
    return df_risks_out


def extract_project_risks(df_input: pd.DataFrame) -> pd.DataFrame:
    """
    Extract Project level risks from DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 2 Reporting - Consolidation".

    :param df_input: Input DataFrame containing consolidated data.
    :return: A new DataFrame containing the extracted project risks.
    """
    index_1 = "Tab 7 - Risks: Section B - Project Risk 1 - Name"
    index_2 = "Tab 7 - Risks: Section B - Project Risk 3 - Risk Owner/Role"
    df_risks = df_input.loc[:, index_1:index_2]
    headers = pd.Index(["Project ID", "Project Name", "Risk Name", "Risk Category"]).append(
        df_risks.iloc[:, 2:14].columns.str.split("- ", expand=True).get_level_values(-1)
    )
    df_risks_out = pd.DataFrame()
    # 14 cols per section, 3 sections.
    for idx in range(0, (3 * 14), 14):
        temp_cols = df_risks.iloc[:, idx : idx + 14]
        temp_cols = join_to_project(df_input, temp_cols)
        temp_cols.columns = headers
        df_risks_out = df_risks_out.append(temp_cols)

    # clean out empty rows - combination of vectorized logical conditions to catch edge cases (partial rows) to keep
    df_risks_out = df_risks_out[
        ((df_risks_out["Risk Name"] != 0) | (df_risks_out["Risk Category"] != 0))
        & (df_risks_out["Pre-mitigated Raw Total Score"] != np.nan)
    ]
    df_risks_out = df_risks_out.dropna(subset=["Risk Name", "Pre-mitigated Raw Total Score"], how="all")

    df_risks_out.sort_values(["Project Name"], inplace=True)
    df_risks_out.reset_index(drop=True, inplace=True)
    return df_risks_out


# assuming this slice of 3 cols is the most suitable to identify programme by
def join_to_programme(df_data: pd.DataFrame, df_to_join: pd.DataFrame) -> pd.DataFrame:
    """
    Extract just the columns that identify a programme instance and join these to given subset of columns.

    Also adds the submission id.
    Tables (input params) must have the same number/order of rows.

    :param df_data: Input DataFrame containing consolidated data.
    :param df_to_join: DataFrame containing only columns to join with Programme identifiers.
    :return: DataFrame joined with the 3 identifier rows for a Programme.
    """

    df_joined = pd.concat([df_data[["Submission ID", "Programme ID"]], df_to_join], axis=1)
    return df_joined


# assuming this slice of 3 cols is the most suitable to identify programme by
def join_to_project(df_data: pd.DataFrame, df_to_join: pd.DataFrame) -> pd.DataFrame:
    """
    Extract just the columns that identify a project instance and join these to given subset of columns.

    Also adds the submission id.
    Tables (input params) must have the same number/order of rows.

    :param df_data: Input DataFrame containing consolidated data.
    :param df_to_join: DataFrame containing only columns to join with Project identifiers.
    :return: DataFrame joined with the 2 identifier rows for a Programme.
    """

    df_proj_id = df_data[["Submission ID", "Tab 2 - Project Admin - Index Codes"]]
    df_joined = pd.concat([df_proj_id, df_to_join], axis=1)
    return df_joined


def convert_date(date_str: str) -> tuple[datetime, datetime]:
    """Convert a string in the format 'May 2020' into datetime objects for first and last day of the given month."""
    date_obj = datetime.strptime(date_str, "%B %Y")
    start_date = date_obj.replace(day=1)
    next_month = start_date.replace(day=28) + timedelta(days=4)
    end_date = next_month - timedelta(days=next_month.day)
    return start_date, end_date


def get_actual_forecast(row: pd.Series) -> str:
    """Check if a row's dates indicate actual or forecast, based on the last day of R2 reporting."""
    last_day_r2 = pd.Timestamp(year=2022, month=9, day=30)
    if pd.notnull(row["End_Date"]):
        if row["End_Date"] > last_day_r2:
            return "Forecast"
        else:
            return "Actual"
    elif pd.notnull(row["Start_Date"]):
        if row["Start_Date"] > last_day_r2:
            return "Forecast"
    return np.nan
