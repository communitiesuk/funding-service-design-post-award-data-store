"""
Methods specifically for extracting data from Round 1 (Excel Spreadsheet)
"""
import datetime

import pandas as pd
from pandas.tseries.offsets import MonthEnd

# isort: off
from core.const import OUTCOME_CATEGORIES, TF_PLACE_NAMES_TO_ORGANISATIONS, ImpactEnum, LikelihoodEnum
from core.controllers.mappings import INGEST_MAPPINGS
from core.util import extract_postcodes


# flake8: noqa
def ingest_round_one_data_towns_fund(round_1_data: dict[pd.DataFrame]) -> dict[pd.DataFrame]:
    """
    Extract and transform data from Round 1 Reporting Template into column headed Pandas DataFrames.

    :param round_1_data: Dictionary of DataFrames of parsed Excel data.
    :return: Dictionary of transformed "tables" as DataFrames.
    """

    round_1_data = update_to_canonical_organisation_names_round_one(round_1_data)

    round_1_data = correct_place_name_spellings(round_1_data)

    round_1_data = get_submission_ids(round_1_data)

    data_model_fields = extract_data_model_fields()

    df_dictionary = extract_data_model_fields()

    df_dictionary["Project Details"] = transform_project_location(
        data_model_fields["Project Details"],
        round_1_data["project_location"],
        round_1_data["lookup_programme_project"],
        round_1_data["Place Identifiers"],
        round_1_data["programme_summary"],
    )
    df_dictionary["Project Progress"] = transform_project_progress(
        data_model_fields["Project Progress"],
        round_1_data["project_progress"],
        round_1_data["lookup_programme_project"],
        round_1_data["Place Identifiers"],
        round_1_data["programme_summary"],
    )
    df_dictionary["Funding"] = transform_project_funding_profiles(
        data_model_fields["Funding"],
        round_1_data["project_funding_profiles_MASTER"],
        round_1_data["lookup_programme_project"],
        round_1_data["Place Identifiers"],
        round_1_data["programme_summary"],
    )
    df_dictionary["Funding Comments"] = transform_project_funding_comments(
        data_model_fields["Funding Comments"],
        round_1_data["project_funding_comments"],
        round_1_data["lookup_programme_project"],
        round_1_data["Place Identifiers"],
        round_1_data["programme_summary"],
    )
    df_dictionary["Programme Progress"] = transform_programme_progress(
        data_model_fields["Programme Progress"],
        round_1_data["programme_summary"],
        round_1_data["Place Identifiers"],
        round_1_data["programme_summary"],
    )
    df_dictionary["Funding Questions"] = transform_funding_questions(
        data_model_fields["Funding Questions"],
        round_1_data["td_fundingcdel_rdel_accelerated"],
        round_1_data["Place Identifiers"],
        round_1_data["programme_summary"],
    )
    df_dictionary["Outcome_Data"] = transform_programme_outcomes(
        data_model_fields["Outcome_Data"],
        round_1_data["programme_outcomes"],
        round_1_data["Place Identifiers"],
        round_1_data["programme_summary"],
    )

    project_risks = transform_project_risks(
        data_model_fields["RiskRegister"],
        round_1_data["project_risks"],
        round_1_data["lookup_programme_project"],
        round_1_data["Place Identifiers"],
        round_1_data["programme_summary"],
    )
    programme_risks = transform_programme_risks(
        data_model_fields["RiskRegister"],
        round_1_data["programme_risks"],
        round_1_data["Place Identifiers"],
        round_1_data["programme_summary"],
    )
    df_dictionary["RiskRegister"] = pd.concat([project_risks, programme_risks], axis=0, ignore_index=True)

    df_dictionary["Outcome_Ref"] = extract_outcome_refs(df_dictionary["Outcome_Ref"], df_dictionary["Outcome_Data"])

    df_dictionary["Place Details"] = extract_place_details(
        data_model_fields["Place Details"],
        round_1_data["lookup_programme_project"],
        round_1_data["Place Identifiers"],
        round_1_data["programme_summary"],
    )

    df_dictionary = extract_submission_refs(df_dictionary)
    df_dictionary = extract_programme_refs(df_dictionary, round_1_data)
    df_dictionary = extract_organisation_refs(df_dictionary)
    df_dictionary = update_project_details(df_dictionary, round_1_data)
    df_dictionary = update_submission_id_type(df_dictionary)

    drop_unused_tables(df_dictionary)

    # there is a garbage value populating a lot of tables with no information other than "TD-" as programme id
    for df_name, df in df_dictionary.items():
        if "Programme ID" in df.columns:
            df_dictionary[df_name] = df[df["Programme ID"] != "TD-"]

    # hacky fix for mismatch in returns numbers for TD-MOR projects in Funding & Risks

    df_dictionary["Funding"].loc[
        df_dictionary["Funding"]["Project ID"].str.startswith("TD-MOR"), "Submission ID"
    ] = "S-R01-117"

    df_dictionary["RiskRegister"].loc[
        df_dictionary["RiskRegister"]["Project ID"].str.startswith("TD-MOR")
        & df_dictionary["RiskRegister"]["Project ID"].notnull(),
        "Submission ID",
    ] = "S-R01-117"

    # hacky fix for St Helens organisation being "None" in the data

    df_dictionary["Organisation_Ref"]["Organisation"][
        df_dictionary["Organisation_Ref"]["Organisation"] == "None"
    ] = "St Helens Borough Council"
    df_dictionary["Programme_Ref"]["Organisation"][
        df_dictionary["Programme_Ref"]["Programme ID"] == "TD-STH"
    ] = "St Helens Borough Council"

    return df_dictionary


def extract_programme_risks(df_programme_risks: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts relevant columns from the programme risks DataFrame.

    :param df_programme_risks: DataFrame of programme risks.
    :return: Extracted DataFrame with renamed columns.
    """
    # Create a subset with only the relevant columns
    df_programme_risks = df_programme_risks[
        [
            "Submission ID",
            "Programme ID",
            "risk_name",
            "risk_category",
            "short_description_of_the_risk",
            "full_description",
            "consequences",
            "pre-mitigated_impact",
            "pre-mitigated_likelihood",
            "mitigations",
            "post-mitigated_impact",
            "post-mitigated_likelihood",
            "proximity",
        ]
    ]

    # Rename columns to correspond to data model names for easier merge
    df_programme_risks = df_programme_risks.rename(
        columns={
            "risk_name": "RiskName",
            "risk_category": "RiskCategory",
            "short_description_of_the_risk": "Short Description",
            "full_description": "Full Description",
            "consequences": "Consequences",
            "pre-mitigated_impact": "Pre-mitigatedImpact",
            "pre-mitigated_likelihood": "Pre-mitigatedLikelihood",
            "mitigations": "Mitigatons",
            "post-mitigated_impact": "PostMitigatedImpact",
            "post-mitigated_likelihood": "PostMitigatedLikelihood",
            "proximity": "Proximity",
        }
    )

    return df_programme_risks


def transform_programme_risks(
    project_details: pd.DataFrame,
    programme_risks: pd.DataFrame,
    place_identifiers: pd.DataFrame,
    programme_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transforms programme risks data by merging with project details and applying null row filtering.

    :param project_details: DataFrame of project details.
    :param programme_risks: DataFrame of programme risks.
    :param place_identifers: DataFrame with information to identify place name abbreviations
    :param programme_summary: DataFrame to identify whether TD or HS
    :return: Transformed DataFrame after merging.
    """

    with_programme_id = get_programme_id(programme_risks, place_identifiers, programme_summary)

    programme_risks_subset = extract_programme_risks(with_programme_id)

    merged_df = pd.merge(
        project_details,
        programme_risks_subset,
        on=[
            "Submission ID",
            "Programme ID",
            "RiskName",
            "RiskCategory",
            "Short Description",
            "Full Description",
            "Consequences",
            "Pre-mitigatedImpact",
            "Pre-mitigatedLikelihood",
            "Mitigatons",
            "PostMitigatedImpact",
            "PostMitigatedLikelihood",
            "Proximity",
        ],
        how="outer",
    )

    likelihood_dict = {
        "1 - Very Low": LikelihoodEnum.LOW.value,
        "2 - Low": LikelihoodEnum.MEDIUM.value,
        "3 - Medium": LikelihoodEnum.HIGH.value,
        "4 - High": LikelihoodEnum.ALMOST_CERTAIN.value,
    }

    merged_df["PostMitigatedLikelihood"] = merged_df["PostMitigatedLikelihood"].map(likelihood_dict)
    merged_df["Pre-mitigatedLikelihood"] = merged_df["Pre-mitigatedLikelihood"].map(likelihood_dict)

    impact_dict = {
        "1- Marginal impact": ImpactEnum.MARGINAL.value,
        "2 - Low impact": ImpactEnum.LOW.value,
        "3 - Medium impact": ImpactEnum.MEDIUM.value,
        "4 - Significant impact": ImpactEnum.SIGNIFICANT.value,
        "4 - High Impact": ImpactEnum.SIGNIFICANT.value,
        "4 - High": ImpactEnum.SIGNIFICANT.value,
        "5 - Major impact": ImpactEnum.MAJOR.value,
    }

    merged_df["Pre-mitigatedImpact"] = (
        merged_df["Pre-mitigatedImpact"].map(impact_dict).fillna(merged_df["Pre-mitigatedImpact"])
    )
    merged_df["PostMitigatedImpact"] = (
        merged_df["PostMitigatedImpact"].map(impact_dict).fillna(merged_df["Pre-mitigatedImpact"])
    )

    promixity_dict = {"2 - Next 12 months": "2 - Distant: next 12 months"}

    merged_df["Proximity"] = merged_df["Proximity"].map(promixity_dict).fillna(merged_df["Proximity"])
    merged_df.dropna(subset=["Proximity"], inplace=True)
    merged_df.dropna(subset=["RiskName"], inplace=True)

    return merged_df


def extract_project_funding_comments(df_funding_comments: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts relevant columns from the project funding comments DataFrame.

    :param df_funding_comments: DataFrame of project funding comments.
    :return: Extracted DataFrame with columns 'Project ID' and 'Comment'.
    """
    # Create a subset with only the relevant columns
    df_funding_comments = df_funding_comments[["Submission ID", "Project ID", "Value"]]

    # Rename columns to correspond to data model names for easier merge
    df_funding_comments = df_funding_comments.rename(columns={"Value": "Comment"})

    return df_funding_comments


def transform_project_funding_comments(
    project_details: pd.DataFrame,
    project_funding_comments: pd.DataFrame,
    lookup: pd.DataFrame,
    place_identifiers: pd.DataFrame,
    programme_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transforms project funding comments data by merging with project details and applying null row filtering.

    :param project_details: DataFrame of project details.
    :param project_funding_comments: DataFrame of project funding comments.
    :param lookup: DataFrame used for lookup operations.
    :param place_identifers: DataFrame with information to identify place name abbreviations
    :param programme_summary: DataFrame to identify whether TD or HS
    :return: Transformed DataFrame after merging.
    """
    with_project_id = get_project_id(project_funding_comments, lookup, place_identifiers, programme_summary)

    project_funding_comments_subset = extract_project_funding_comments(with_project_id)

    merged_df = pd.merge(
        project_details, project_funding_comments_subset, on=["Submission ID", "Project ID", "Comment"], how="outer"
    )

    return merged_df


def extract_project_funding_profiles(df_funding_profiles: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts relevant columns from the project funding profiles DataFrame.

    :param df_funding_profiles: DataFrame of project funding profiles.
    :return: Extracted DataFrame with renamed columns.
    """
    # Flip values as the data model column called 'secured' expects the opposite values
    df_funding_profiles["unsecured_funding"] = df_funding_profiles["unsecured_funding"].replace(
        {"No": "Yes", "Yes": "No"}
    )

    df_funding_profiles = df_funding_profiles[df_funding_profiles["variable"] != "grand_total"]

    # Create a subset with only the relevant columns
    df_funding_profiles = df_funding_profiles[
        [
            "Submission ID",
            "Project ID",
            "funding_source_name",
            "funding_source",
            "unsecured_funding",
            "time_period",
            "value",
            "variable",
        ]
    ]

    # Rename columns to correspond to data model names for easier merge
    df_funding_profiles = df_funding_profiles.rename(
        columns={
            "funding_source_name": "Funding Source Name",
            "funding_source": "Funding Source Type",
            "unsecured_funding": "Secured",
            "time_period": "Reporting Period",
            "value": "Spend for Reporting Period",
        }
    )

    return df_funding_profiles


def transform_project_funding_profiles(
    project_details: pd.DataFrame,
    project_funding_profiles: pd.DataFrame,
    lookup: pd.DataFrame,
    place_identifiers: pd.DataFrame,
    programme_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transforms project funding profiles data by merging with project details and applying null row filtering.

    :param project_details: DataFrame of project details.
    :param project_funding_profiles: DataFrame of project funding profiles.
    :param lookup: DataFrame used for project ID mapping.
    :param place_identifers: DataFrame with information to identify place name abbreviations
    :param programme_summary: DataFrame to identify whether TD or HS
    :return: Transformed DataFrame after merging and null row filtering.
    """
    project_funding_profiles = project_funding_profiles[
        ~(
            (project_funding_profiles["time_period"] == "grand_total")
            | project_funding_profiles["time_period"].str.startswith("total-")
        )
    ]
    with_project_id = get_project_id(project_funding_profiles, lookup, place_identifiers, programme_summary)

    project_funding_profiles_subset = extract_project_funding_profiles(with_project_id)

    # there is no day, only month and year, and so for purposes of fitting into database all days set to 01
    project_funding_profiles_subset = split_date_column(
        project_funding_profiles_subset, "Reporting Period", "Start_Date", "End_Date"
    )

    merged_df = pd.merge(
        project_details,
        project_funding_profiles_subset,
        on=[
            "Submission ID",
            "Project ID",
            "Funding Source Name",
            "Funding Source Type",
            "Secured",
            "Start_Date",
            "End_Date",
            "Spend for Reporting Period",
        ],
        how="outer",
    )

    merged_df = merged_df.drop("Reporting Period", axis=1)
    # hidden cols in funding causing issues with get_project_id(); provisionally dropping these
    merged_df = merged_df.dropna(subset=["Project ID"])
    merged_df = merged_df[merged_df["Project ID"] != ""]

    FUNDING_NAME_DICT = {
        "cdel_tf_project_activity": (
            "Towns Fund CDEL which is being utilised on TF project related "
            "activity (For Town Deals, this excludes the 5% CDEL Pre-Payment)"
        ),
        "cdel": "Town Deals 5% CDEL Pre-Payment",
        "contractually_committed": "How much of your forecast is contractually committed?",
        "rdel": "Towns Fund RDEL Payment which is being utilised on TF project related activity",
    }

    merged_df = merged_df[merged_df["variable"] != "grand_total"]
    merged_df["Funding Source Type"] = merged_df["Funding Source Type"].fillna("Towns Fund")
    merged_df["Funding Source Name"] = merged_df["Funding Source Name"].fillna(
        merged_df["variable"].map(FUNDING_NAME_DICT)
    )
    merged_df.drop("variable", axis=1, inplace=True)

    merged_df = merged_df.drop_duplicates(
        subset=["Submission ID", "Project ID", "Funding Source Name", "Funding Source Type", "Start_Date", "End_Date"],
        keep="first",
    )

    # columns_to_drop = ["Start_Date", "End_Date"]
    # merged_df.dropna(subset=columns_to_drop, inplace=True)
    merged_df["End_Date"] = pd.to_datetime(merged_df["End_Date"], format="%d/%m/%Y") + MonthEnd(0)

    merged_df = merged_df[merged_df["Project ID"] != "TD-20"]
    merged_df.loc[merged_df["Secured"] == "None", "Secured"] = ""

    return merged_df


def extract_project_location(project_location: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts relevant columns from the project location DataFrame.

    :param project_location: DataFrame of project location data.
    :return: Extracted DataFrame with renamed columns.
    """
    # Create a subset with only the relevant columns
    project_location = project_location[
        [
            "Submission ID",
            "Project ID",
            "place_name",
            "primary_intervention_theme",
            "site_location_type",
            "all_postcodes",
            "gis_map_provided",
        ]
    ]

    # Rename columns to correspond to data model names for easier merge
    project_location = project_location.rename(
        columns={
            "primary_intervention_theme": "Primary Intervention Theme",
            "place_name": "Locations",
            "site_location_type": "Single or Multiple Locations",
            "all_postcodes": "Postcodes",
            "gis_map_provided": "GIS Provided",
        }
    )

    return project_location


def transform_project_location(
    project_details: pd.DataFrame,
    project_location: pd.DataFrame,
    lookup: pd.DataFrame,
    place_identifiers: pd.DataFrame,
    programme_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transforms project location data by merging with project details and applying null row filtering.

    :param project_details: DataFrame of project details.
    :param project_location: DataFrame of project location data.
    :param lookup: DataFrame used for project ID mapping.
    :param place_identifers: DataFrame with information to identify place name abbreviations
    :param programme_summary: DataFrame to identify whether TD or HS
    :return: Transformed DataFrame after merging.
    """
    with_project_id = get_project_id(project_location, lookup, place_identifiers, programme_summary)

    project_location_subset = extract_project_location(with_project_id)

    merged_df = pd.merge(
        project_details,
        project_location_subset,
        on=[
            "Submission ID",
            "Project ID",
            "Primary Intervention Theme",
            "Single or Multiple Locations",
            "Locations",
            "Postcodes",
            "GIS Provided",
        ],
        how="outer",
    )

    merged_df = merged_df.drop_duplicates(subset=["Project ID"], keep="first").reset_index(drop=True)
    merged_df["Programme ID"] = merged_df["Project ID"].str[:6]

    merged_df.loc[
        merged_df["GIS Provided"].isin(["< Select >", "None"]),
        "GIS Provided",
    ] = ""

    return merged_df


def extract_project_progress(df_progress: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts relevant columns from the project progress DataFrame.

    :param df_progress: DataFrame of project progress data.
    :return: Extracted DataFrame with renamed columns.
    """
    # Create a subset with only the relevant columns
    df_progress = df_progress[
        [
            "Submission ID",
            "Project ID",
            "start_date",
            "completion_date",
            "status",
            "delivery_rag",
            "spend_rag",
            "risk_rag",
            "commentary",
        ]
    ]

    # Rename columns to correspond to data model names for easier merge
    df_progress = df_progress.rename(
        columns={
            "start_date": "Start Date",
            "completion_date": "Completion Date",
            "status": "Project Delivery Status",
            "delivery_rag": "Delivery (RAG)",
            "spend_rag": "Spend (RAG)",
            "risk_rag": "Risk (RAG)",
            "commentary": "Commentary on Status and RAG Ratings",
        }
    )

    return df_progress


def transform_project_progress(
    project_details: pd.DataFrame,
    project_progress: pd.DataFrame,
    lookup: pd.DataFrame,
    place_identifiers: pd.DataFrame,
    programme_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transforms project progress data by merging with project details and applying null row filtering.

    :param project_details: DataFrame of project details.
    :param project_progress: DataFrame of project progress data.
    :param lookup: DataFrame used for project ID mapping.
    :param place_identifers: DataFrame with information to identify place name abbreviations
    :param programme_summary: DataFrame to identify whether TD or HS
    :return: Transformed DataFrame after merging.
    """
    with_project_id = get_project_id(project_progress, lookup, place_identifiers, programme_summary)

    project_progress_subset = extract_project_progress(with_project_id)

    merged_df = pd.merge(
        project_details,
        project_progress_subset,
        on=[
            "Submission ID",
            "Project ID",
            "Start Date",
            "Completion Date",
            "Project Delivery Status",
            "Delivery (RAG)",
            "Spend (RAG)",
            "Risk (RAG)",
            "Commentary on Status and RAG Ratings",
        ],
        how="outer",
    )

    merged_df = merged_df.drop_duplicates(subset=["Project ID"], keep="first").reset_index(drop=True)

    columns_to_drop = ["Delivery (RAG)", "Spend (RAG)", "Risk (RAG)"]
    merged_df.dropna(subset=columns_to_drop, inplace=True)

    delivery_status_dict = {
        "2. On track": "2. Ongoing - on track",
        "3. Delayed": "3. Ongoing - delayed",
    }

    merged_df["Project Delivery Status"] = (
        merged_df["Project Delivery Status"].map(delivery_status_dict).fillna(merged_df["Project Delivery Status"])
    )
    merged_df["Project Delivery Status"] = merged_df["Project Delivery Status"].replace("Unknown", "")

    merged_df["Delivery (RAG)"] = merged_df["Delivery (RAG)"].astype(int)
    merged_df["Spend (RAG)"] = merged_df["Spend (RAG)"].astype(int)
    merged_df["Risk (RAG)"] = merged_df["Risk (RAG)"].astype(int)

    return merged_df


def extract_project_risks(df_project_risks: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts relevant columns from the project risks DataFrame.

    :param df_project_risks: DataFrame of project risks data.
    :return: Extracted DataFrame with renamed columns.
    """
    # Create a subset with only the relevant columns
    df_project_risks = df_project_risks[
        [
            "Submission ID",
            "Project ID",
            "risk_name",
            "risk_category",
            "short_description_of_the_risk",
            "full_description",
            "consequences",
            "pre-mitigated_impact",
            "pre-mitigated_likelihood",
            "mitigations",
            "post-mitigated_impact",
            "post-mitigated_likelihood",
            "proximity",
        ]
    ]

    # Rename columns to correspond to data model names for easier merge
    df_project_risks = df_project_risks.rename(
        columns={
            "risk_name": "RiskName",
            "risk_category": "RiskCategory",
            "short_description_of_the_risk": "Short Description",
            "full_description": "Full Description",
            "consequences": "Consequences",
            "pre-mitigated_impact": "Pre-mitigatedImpact",
            "pre-mitigated_likelihood": "Pre-mitigatedLikelihood",
            "mitigations": "Mitigatons",
            "post-mitigated_impact": "PostMitigatedImpact",
            "post-mitigated_likelihood": "PostMitigatedLikelihood",
            "proximity": "Proximity",
        }
    )

    return df_project_risks


def transform_project_risks(
    project_details: pd.DataFrame,
    project_risks: pd.DataFrame,
    lookup: pd.DataFrame,
    place_identifiers: pd.DataFrame,
    programme_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transforms project risks data by merging with project details and applying null row filtering.

    :param project_details: DataFrame of project details.
    :param project_risks: DataFrame of project risks data.
    :param lookup: DataFrame used for project ID mapping.
    :param place_identifers: DataFrame with information to identify place name abbreviations
    :param programme_summary: DataFrame to identify whether TD or HS
    :return: Transformed DataFrame after merging.
    """
    with_project_id = get_project_id(project_risks, lookup, place_identifiers, programme_summary)

    project_risks_subset = extract_project_risks(with_project_id)

    # Named incorrectly in data model sheet
    project_details = project_details.rename(columns={"Project_ID": "Project ID"})

    merged_df = pd.merge(
        project_details,
        project_risks_subset,
        on=[
            "Submission ID",
            "Project ID",
            "RiskName",
            "RiskCategory",
            "Short Description",
            "Full Description",
            "Consequences",
            "Pre-mitigatedImpact",
            "Pre-mitigatedLikelihood",
            "Mitigatons",
            "PostMitigatedImpact",
            "PostMitigatedLikelihood",
            "Proximity",
        ],
        how="outer",
    )

    likelihood_dict = {
        "1 - Very Low": LikelihoodEnum.LOW.value,
        "2 - Low": LikelihoodEnum.MEDIUM.value,
        "3 - Medium": LikelihoodEnum.HIGH.value,
        "4 - High": LikelihoodEnum.ALMOST_CERTAIN.value,
    }

    merged_df["PostMitigatedLikelihood"] = merged_df["PostMitigatedLikelihood"].map(likelihood_dict)
    merged_df["Pre-mitigatedLikelihood"] = merged_df["Pre-mitigatedLikelihood"].map(likelihood_dict)

    impact_dict = {
        "1- Marginal impact": ImpactEnum.MARGINAL.value,
        "2 - Low impact": ImpactEnum.LOW.value,
        "3 - Medium impact": ImpactEnum.MEDIUM.value,
        "4 - Significant impact": ImpactEnum.SIGNIFICANT.value,
        "4 - High Impact": ImpactEnum.SIGNIFICANT.value,
        "4 - High": ImpactEnum.SIGNIFICANT.value,
        "5 - Major impact": ImpactEnum.MAJOR.value,
    }

    merged_df["Pre-mitigatedImpact"] = (
        merged_df["Pre-mitigatedImpact"].map(impact_dict).fillna(merged_df["Pre-mitigatedImpact"])
    )
    merged_df["PostMitigatedImpact"] = (
        merged_df["PostMitigatedImpact"].map(impact_dict).fillna(merged_df["Pre-mitigatedImpact"])
    )

    promixity_dict = {"2 - Next 12 months": "2 - Distant: next 12 months"}

    merged_df["Proximity"] = merged_df["Proximity"].map(promixity_dict).fillna(merged_df["Proximity"])
    merged_df = merged_df[merged_df["Proximity"] != "None"]

    merged_df.dropna(subset=["RiskName"], inplace=True)

    return merged_df


def extract_programme_progress(df_programme_progress: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts relevant columns from the project risks DataFrame.

    :param df_programme_progress: DataFrame of project risks data.
    :return: Extracted DataFrame with renamed columns.
    """
    question_dict = {
        "progress_against_forecast": "How is your programme progressing against your original profile / forecast? ",
        "six_month_update": "Please provide a progress update covering the 6 month reporting period",
        "current_challenges": "What are the key challenges you are currently facing?\nPlease provide as much detail as possible",
        "expected_challenges": "What challenges do you expect to face in the next 6/12 months? (Please include timeframes)",
        "local_evaluation_activities": "Please provide an update on your local evaluation activities",
        "key_milestones": (
            "Please provide any key milestones which you would like to make us aware of for "
            "publicity purposes during the next quarter\n"
            "(e.g. first spade in the ground, designs complete, building fit out)"
        ),
        "dluhc_support_required": "If any support is required from the DLUHC TF team, please comment",
    }

    q_and_a_subset = df_programme_progress[
        [
            "Submission ID",
            "Programme ID",
            "progress_against_forecast",
            "six_month_update",
            "current_challenges",
            "expected_challenges",
            "local_evaluation_activities",
            "key_milestones",
            "dluhc_support_required",
        ]
    ]

    q_and_as = pd.DataFrame(columns=["Submission ID", "Programme ID", "Question", "Answer"])

    for index, row in q_and_a_subset.iterrows():
        for col in q_and_a_subset.columns[2:]:
            question = question_dict[col]

            answer = row[col]

            programme_id = row["Programme ID"]

            submission_id = row["Submission ID"]

            q_and_as = q_and_as._append(
                {"Submission ID": submission_id, "Programme ID": programme_id, "Question": question, "Answer": answer},
                ignore_index=True,
            )

    return q_and_as


def transform_programme_progress(
    project_details: pd.DataFrame,
    programme_progress: pd.DataFrame,
    place_identifiers: pd.DataFrame,
    programme_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transforms project risks data by merging with project details and applying null row filtering.

    :param project_details: DataFrame of project details.
    :param project_progress: DataFrame of project risks data.
    :param place_identifers: DataFrame with information to identify place name abbreviations
    :param programme_summary: DataFrame to identify whether TD or HS
    :return: Transformed DataFrame after merging.
    """

    with_programme_id = get_programme_id(programme_progress, place_identifiers, programme_summary)

    programme_progress_subset = extract_programme_progress(with_programme_id)

    merged_df = pd.merge(
        project_details,
        programme_progress_subset,
        on=["Submission ID", "Programme ID", "Question", "Answer"],
        how="outer",
    )

    return merged_df


def extract_funding_questions(df_funding_questions: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts relevant columns from the funding questions DataFrame.

    :param df_funding_questions: DataFrame of funding questions data.
    :return: Extracted DataFrame with renamed columns.
    """
    column_mapping = {
        "received_other_payments": [
            "Beyond these three funding types, have you received any payments for specific projects?",
            "",
        ],
        "cdel_prepayment.gbp_utilised": [
            "Please indicate how much of your allocation has been utilised (in £s)",
            "TD 5% CDEL Pre-Payment",
        ],
        "cdel_prepayment.represents_entire_allocation": [
            "Please confirm whether the amount utilised represents your entire allocation",
            "TD 5% CDEL Pre-Payment",
        ],
        "cdel_prepayment.when_utilised": [
            "Please describe when funding was utilised and, if applicable, when any remaining funding will be utilised",
            "TD 5% CDEL Pre-Payment",
        ],
        "cdel_prepayment.how_utilised": [
            "Please select the option that best describes how the funding was, or will be, utilised",
            "TD 5% CDEL Pre-Payment",
        ],
        "cdel_prepayment.how_utilised_detail": [
            "Please explain in detail how the funding has, or will be, utilised",
            "TD 5% CDEL Pre-Payment",
        ],
        "rdel_capacity_funding.gbp_utilised": [
            "Please indicate how much of your allocation has been utilised (in £s)",
            "TD RDEL Capacity Funding",
        ],
        "rdel_capacity_funding.represents_entire_allocation": [
            "Please confirm whether the amount utilised represents your entire allocation",
            "TD RDEL Capacity Funding",
        ],
        "rdel_capacity_funding.when_utilised": [
            "Please describe when funding was utilised and, if applicable, when any remaining funding will be utilised",
            "TD RDEL Capacity Funding",
        ],
        "rdel_capacity_funding.how_utilised": [
            "Please select the option that best describes how the funding was, or will be, utilised",
            "TD RDEL Capacity Funding",
        ],
        "rdel_capacity_funding.how_utilised_detail": [
            "Please explain in detail how the funding has, or will be, utilised",
            "TD RDEL Capacity Funding",
        ],
        "td_accelerated.gbp_utilised": [
            "Please indicate how much of your allocation has been utilised (in £s)",
            "TD Accelerated Funding",
        ],
        "td_accelerated.represents_entire_allocation": [
            "Please confirm whether the amount utilised represents your entire allocation",
            "TD Accelerated Funding",
        ],
        "td_accelerated.when_utilised": [
            "Please describe when funding was utilised and, if applicable, when any remaining funding will be utilised",
            "TD Accelerated Funding",
        ],
        "td_accelerated.how_utilised": [
            "Please select the option that best describes how the funding was, or will be, utilised ",
            "TD Accelerated Funding",
        ],
        "td_accelerated.how_utilised_detail": [
            "Please explain in detail how the funding has, or will be, utilised",
            "TD Accelerated Funding",
        ],
    }

    q_and_a_subset = df_funding_questions[
        [
            "Submission ID",
            "Programme ID",
            "received_other_payments",
            "cdel_prepayment.gbp_utilised",
            "cdel_prepayment.represents_entire_allocation",
            "cdel_prepayment.when_utilised",
            "cdel_prepayment.how_utilised",
            "cdel_prepayment.how_utilised_detail",
            "rdel_capacity_funding.gbp_utilised",
            "rdel_capacity_funding.represents_entire_allocation",
            "rdel_capacity_funding.when_utilised",
            "rdel_capacity_funding.how_utilised",
            "rdel_capacity_funding.how_utilised_detail",
            "td_accelerated.gbp_utilised",
            "td_accelerated.represents_entire_allocation",
            "td_accelerated.when_utilised",
            "td_accelerated.how_utilised",
            "td_accelerated.how_utilised_detail",
        ]
    ]

    q_and_as = pd.DataFrame(columns=["Submission ID", "Programme ID", "Question", "Answer", "Indicator"])

    for index, row in q_and_a_subset.iterrows():
        for col in q_and_a_subset.columns[2:]:
            question = column_mapping[col][0]
            indicator = column_mapping[col][1]
            answer = row[col]
            programme_id = row["Programme ID"]
            submission_id = row["Submission ID"]

            q_and_as = q_and_as._append(
                {
                    "Submission ID": submission_id,
                    "Programme ID": programme_id,
                    "Question": question,
                    "Answer": answer,
                    "Indicator": indicator,
                },
                ignore_index=True,
            )

    q_and_as = q_and_as.rename(columns={"Answer": "Response"})

    return q_and_as


def transform_funding_questions(
    project_details: pd.DataFrame,
    funding_questions: pd.DataFrame,
    place_identifiers: pd.DataFrame,
    programme_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transforms project risks data by merging with project details and applying null row filtering.

    :param project_details: DataFrame of project details.
    :param funding_questions: DataFrame of funding questions.
    :param place_identifers: DataFrame with information to identify place name abbreviations
    :param programme_summary: DataFrame to identify whether TD or HS
    :return: Transformed DataFrame after merging and null row filtering.
    """

    with_programme_id = get_programme_id(funding_questions, place_identifiers, programme_summary)

    funding_questions_subset = extract_funding_questions(with_programme_id)

    merged_df = pd.merge(
        project_details,
        funding_questions_subset,
        on=[
            "Submission ID",
            "Programme ID",
            "Question",
            "Response",
            "Indicator",
        ],
        how="outer",
    )

    # merged_df.dropna(subset=merged_df.columns.difference(["Project ID"]), how="all", inplace=True)

    return merged_df


def extract_programme_outcomes(df_programme_outcomes: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts relevant columns from the programme risks DataFrame.

    :param df_programme_outcomes: DataFrame of programme risks.
    :return: Extracted DataFrame with renamed columns.
    """
    # Create a subset with only the relevant columns
    df_programme_outcomes = df_programme_outcomes[
        [
            "Submission ID",
            "Programme ID",
            "outcome",
            "value",
            "date",
        ]
    ]

    # Rename columns to correspond to data model names for easier merge
    df_programme_outcomes = df_programme_outcomes.rename(
        columns={"outcome": "Outcome", "value": "Amount", "date": "Start_Date"}
    )

    df_programme_outcomes["Amount"] = pd.to_numeric(df_programme_outcomes["Amount"], errors="coerce")

    return df_programme_outcomes


def transform_programme_outcomes(
    project_details: pd.DataFrame,
    programme_outcomes: pd.DataFrame,
    place_identifiers: pd.DataFrame,
    programme_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Transforms programme risks data by merging with project details and applying null row filtering.

    :param project_details: DataFrame of project details.
    :param programme_outcomes: DataFrame of programme outcomes.
    :param place_identifers: DataFrame with information to identify place name abbreviations
    :param programme_summary: DataFrame to identify whether TD or HS
    :return: Transformed DataFrame after merging.
    """

    with_programme_id = get_programme_id(programme_outcomes, place_identifiers, programme_summary)

    programme_outcomes_subset = extract_programme_outcomes(with_programme_id)

    merged_df = pd.merge(
        project_details,
        programme_outcomes_subset,
        on=[
            "Submission ID",
            "Programme ID",
            "Outcome",
            "Amount",
            "Start_Date",
        ],
        how="outer",
    )

    merged_df["Outcome"] = "Year on Year monthly % change in footfall"
    merged_df["UnitofMeasurement"] = "Year-on-year % change in monthly footfall"
    merged_df["GeographyIndicator"] = "Town"

    merged_df["End_Date"] = pd.to_datetime(merged_df["Start_Date"], format="%d/%m/%Y") + MonthEnd(0)

    return merged_df


def get_project_id(
    round_1_category: pd.DataFrame,
    lookup_table: pd.DataFrame,
    place_identifiers: pd.DataFrame,
    programme_summary: pd.DataFrame,
) -> pd.DataFrame:
    """
    Generates project IDs based on the round 1 category DataFrame by mapping place names, project numbers,
    and applying prefixes and abbreviations.

    :param round_1_category: DataFrame containing round 1 category data.
    :param lookup_table: DataFrame used for place name and project name mapping.
    :param place_identifers: DataFrame with information to identify place name abbreviations
    :param programme_summary: DataFrame to identify whether TD or HS
    :return: DataFrame with added 'Project ID' column.
    """
    if "proj_num" not in round_1_category.columns:
        round_1_category = get_project_number(round_1_category, lookup_table)

    round_1_category = get_prefix(round_1_category, programme_summary)

    TD_ABBREVIATIONS, FHSF_ABBREVIATIONS = extract_place_identifiers(place_identifiers)

    def get_abbreviation(place_name):
        if place_name in TD_ABBREVIATIONS:
            return str(TD_ABBREVIATIONS[place_name]) + "-"
        elif place_name in FHSF_ABBREVIATIONS:
            return str(FHSF_ABBREVIATIONS[place_name]) + "-"
        else:
            return ""

    def get_actual_proj_num(proj_num):
        if len(proj_num) == 1:
            return "0" + proj_num
        else:
            return proj_num

    round_1_category["Project ID"] = (
        round_1_category["form_type"]
        + "-"
        + round_1_category["place_name"].map(get_abbreviation)
        + round_1_category["proj_num"].astype(str).map(get_actual_proj_num)
    )

    return round_1_category


def get_programme_id(
    round_1_category: pd.DataFrame, place_identifiers: pd.DataFrame, programme_summary: pd.DataFrame
) -> pd.DataFrame:
    """
    Generates programme IDs based on the round 1 category DataFrame by mapping place names
    and applying prefixes and abbreviations.

    :param round_1_category: DataFrame containing round 1 category data.
    :param place_identifers: DataFrame with information to identify place name abbreviations.
    :param programme_summary: DataFrame to identify whether TD or HS
    :return: DataFrame with added 'Programme ID' column.
    """
    round_1_category = get_prefix(round_1_category, programme_summary)

    TD_ABBREVIATIONS, FHSF_ABBREVIATIONS = extract_place_identifiers(place_identifiers)

    def get_abbreviation(place_name):
        if place_name in TD_ABBREVIATIONS:
            return str(TD_ABBREVIATIONS[place_name])
        elif place_name in FHSF_ABBREVIATIONS:
            return str(FHSF_ABBREVIATIONS[place_name])
        else:
            return ""

    round_1_category["Programme ID"] = (
        round_1_category["form_type"] + "-" + round_1_category["place_name"].map(get_abbreviation)
    )
    return round_1_category


def get_prefix(round_1_category, programme_summary):
    """
    Updates the 'form_type' column in the round 1 category DataFrame by merging it with the programme_summary DataFrame
    and replacing values with abbreviations.

    :param round_1_category: DataFrame containing round 1 category data.
    :param programme_summary: DataFrame with information about place names, return numbers, and form types.
    :return: DataFrame with updated 'form_type' column.
    """
    programme_summary = programme_summary[["place_name", "return_num", "form_type"]]

    if "form_type" not in round_1_category.columns:
        merged_df = pd.merge(round_1_category, programme_summary, on=["place_name", "return_num"], how="left")
        merged_df["form_type"] = merged_df["form_type"].replace({"FHSF": "HS", "Town Deal": "TD"})
        return merged_df
    else:
        round_1_category["form_type"] = round_1_category["form_type"].replace({"FHSF": "HS", "Town Deal": "TD"})
        return round_1_category


def get_project_number(round_1_category: pd.DataFrame, lookup_table: pd.DataFrame) -> pd.DataFrame:
    """
    Retrieves missing project numbers from the lookup table based on place name and project name mapping.

    :param round_1_category: DataFrame containing round 1 category data.
    :param lookup_table: DataFrame used for place name and project name mapping.
    :return: DataFrame with added project numbers.
    """
    if "place_name" and "proj_name" in round_1_category.columns:
        round_1_category = round_1_category.rename(columns={"proj_name": "project_name"})
        lookup_table = lookup_table[["place_name", "project_name", "proj_num"]]

        merged_df = pd.merge(round_1_category, lookup_table, on=["place_name", "project_name"], how="left")
    else:
        merged_df = None

    return merged_df


def get_project_name(round_1_category: pd.DataFrame, lookup_table: pd.DataFrame) -> pd.DataFrame:
    round_1_category["proj_num"] = round_1_category["Project ID"].str[-2:].str.lstrip("0")

    lookup_table = lookup_table[["place_name", "project_name", "proj_num"]].astype({"proj_num": "string"})

    merged_df = pd.merge(
        round_1_category,
        lookup_table,
        left_on=["Locations", "proj_num"],
        right_on=["place_name", "proj_num"],
        how="left",
    )

    merged_df = merged_df.drop(columns=["proj_num", "place_name", "Project Name"])
    merged_df = merged_df.rename(columns={"project_name": "Project Name"})

    merged_df["Project Name"] = merged_df["Project Name"].fillna("Unknown")
    merged_df = merged_df.drop_duplicates(subset=["Project ID"], keep="first")

    return merged_df


def extract_data_model_fields() -> pd.DataFrame:
    """
    Extracts data model fields from the column mappings and returns a DataFrame mapping.

    :return: DataFrame mapping data model table names to their respective column names.
    """
    column_mapping = {mapping.worksheet_name: list(mapping.columns.keys()) for mapping in INGEST_MAPPINGS}

    dataframe_mapping = {table_name: pd.DataFrame(columns=columns) for table_name, columns in column_mapping.items()}

    return dataframe_mapping


def extract_place_identifiers(place_identifiers: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts TD and FHSF place identifiers from the place_identifiers DataFrame.

    :param place_identifiers: DataFrame containing place identifiers.
    :return: Tuple of dictionaries: (TD place dictionary, FHSF place dictionary).
    """
    cropped = place_identifiers.iloc[1:, 1:]
    cropped = cropped.rename(
        columns={
            "Unnamed: 1": "TD Place Names",
            "Unnamed: 2": "TD Abbreviations",
            "Unnamed: 4": "FHSF Place Names",
            "Unnamed: 5": "FHSF Abbreviations",
        }
    )

    place_names = cropped["TD Place Names"].tolist()
    abbreviations = cropped["TD Abbreviations"].tolist()

    td_dictionary = dict(zip(place_names, abbreviations))

    place_names = cropped["FHSF Place Names"].tolist()
    abbreviations = cropped["FHSF Abbreviations"].tolist()

    fhsf_dictionary = dict(zip(place_names, abbreviations))

    return td_dictionary, fhsf_dictionary


def extract_project_identifiers(project_identifiers: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts project identifiers from the given DataFrame and returns a concatenated DataFrame for TD and HS projects.

    :param project_identifiers: DataFrame containing project identifier information.
    :return: Concatenated DataFrame with project identifiers for TD and HS projects.
    """
    cropped = project_identifiers.iloc[2:, 1:]

    td = cropped[["Unnamed: 1", "Unnamed: 2", "Unnamed: 3"]]
    td = td.rename(
        columns={
            "Unnamed: 1": "Project ID",
            "Unnamed: 2": "place_name",
            "Unnamed: 3": "proj_name",
        }
    )

    hs = cropped[["Unnamed: 8", "Unnamed: 9", "Unnamed: 10"]]
    hs = hs.rename(
        columns={
            "Unnamed: 8": "Project ID",
            "Unnamed: 9": "place_name",
            "Unnamed: 10": "proj_name",
        }
    )
    hs = hs.dropna()

    return pd.concat([td, hs], ignore_index=True)


def split_date_column(
    dataframe: pd.DataFrame, column_name: str, start_date_column: str, end_date_column: str
) -> pd.DataFrame:
    """
    Splits the values in the specified column of the DataFrame into start and end dates
    and updates the corresponding start_date_column and end_date_column.

    :param dataframe: DataFrame containing the data.
    :param column_name: Name of the column to split.
    :param start_date_column: Name of the column to store the start dates.
    :param end_date_column: Name of the column to store the end dates.
    :return: Updated DataFrame with split dates.
    """
    dataframe[column_name] = dataframe[column_name].astype(str)  # Convert column to string

    split_values = dataframe[column_name].str.extract(r"(\w{3})-(\w{3})-(\d{4}/\d{2})")

    start_dates = split_values[0] + "-" + split_values[2].str[:2]
    end_dates = split_values[1] + "-" + split_values[2].str[5:]

    start_date_objects = pd.to_datetime(start_dates, format="%b-%y")
    end_date_objects = pd.to_datetime(end_dates, format="%b-%y")

    dataframe[start_date_column] = start_date_objects
    dataframe[end_date_column] = end_date_objects

    total_mask = dataframe[start_date_column].astype(str).str.startswith("total-") & dataframe[end_date_column].astype(
        str
    ).str.startswith("total-")
    dataframe.loc[total_mask, start_date_column] = pd.NaT
    dataframe.loc[total_mask, end_date_column] = pd.NaT

    grand_total_mask = dataframe[column_name] == "grand_total"
    dataframe.loc[grand_total_mask, start_date_column] = pd.NaT
    dataframe.loc[grand_total_mask, end_date_column] = pd.NaT

    # Apply additional changes
    dataframe.loc[dataframe[column_name] == "<2020/21", start_date_column] = pd.NaT
    dataframe.loc[dataframe[column_name] == "<2020/21", end_date_column] = pd.to_datetime(
        "31-03-2020", format="%d-%m-%Y"
    )
    dataframe.loc[dataframe[column_name] == ">2025/26", start_date_column] = pd.to_datetime(
        "01-04-2026", format="%d-%m-%Y"
    )
    dataframe.loc[dataframe[column_name] == ">2025/26", end_date_column] = pd.NaT

    return dataframe


def correct_place_name_spellings(df_dict: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Corrects the spellings of specific place names in the DataFrame dictionary.

    :param df_dict: Dictionary of DataFrames.
    :return: Updated DataFrame dictionary with corrected place name spellings.
    """
    for key, df in df_dict.items():
        if "place_name" in df.columns:
            df.loc[df["place_name"] == "Newcastle-under-Lyme", "place_name"] = "Newcastle-under-Lyme "
            df.loc[df["place_name"] == "Stavely", "place_name"] = "Staveley "
            df.loc[df["place_name"] == "Southport", "place_name"] = "Southport "
            df.loc[df["place_name"] == "Sutton Town Centre High Street", "place_name"] = "Sutton"

    return df_dict


def get_submission_ids(df_dict: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Generates submission IDs for each DataFrame in the dictionary based on the return_num column.

    :param df_dict: Dictionary of DataFrames.
    :return: Updated DataFrame dictionary with added 'Submission ID' column.
    """
    prefix = "S-R01-"

    for df_name, df in df_dict.items():
        if "return_num" in df.columns:
            return_nums = df["return_num"]
            df["Submission ID"] = prefix + return_nums.astype(str)

    return df_dict


def extract_submission_refs(df_dict: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Extracts submission IDs from the DataFrame dictionary and populates the 'Submission_Ref' table
    with the ordered submission IDs and other reporting period information.
    :param df_dict: Dictionary of DataFrames.
    :return: Updated DataFrame dictionary with populated 'Submission_Ref' table.
    """
    submission_ids = set()
    for df in df_dict.values():
        if "Submission ID" in df.columns:
            submission_ids.update(df["Submission ID"].unique())
    ordered_submission_ids = sorted(submission_ids, key=lambda x: int(x.split("-")[2]))

    df_dict["Submission_Ref"]["Submission ID"] = ordered_submission_ids
    df_dict["Submission_Ref"]["Submission Date"] = datetime.datetime.now()
    df_dict["Submission_Ref"]["Reporting Period Start"] = "1 April 2019"
    df_dict["Submission_Ref"]["Reporting Period End"] = "31 March 2022"
    df_dict["Submission_Ref"]["Reporting Round"] = "1"

    return df_dict


def extract_organisation_refs(df_dict: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Populates the 'Organisation_Ref' table.

    :param df_dict: Dictionary of DataFrames.
    :return: Updated DataFrame dictionary with Organisation_Ref filled in.
    """

    df_dict["Organisation_Ref"]["Organisation"] = pd.unique(df_dict["Programme_Ref"]["Organisation"])

    return df_dict


def extract_programme_refs(
    df_dict: dict[str, pd.DataFrame], round_1_data: dict[str, pd.DataFrame]
) -> dict[str, pd.DataFrame]:
    """
    Extracts programme references from the given data dictionaries and adds a 'Programme_Ref' dataframe.

    :param df_dict: Dictionary of dataframes.
    :param round_1_data: Dataframe containing round 1 data.
    :return: Updated dataframe dictionary with 'Programme_Ref' added.
    """
    programme_ids = set()
    for df in df_dict.values():
        if "Programme ID" in df.columns:
            programme_ids.update(df["Programme ID"].unique())

    programme_data = pd.DataFrame(
        {
            "Programme ID": list(programme_ids),
            "Programme Name": [f"programme_name_{i}" for i in range(1, len(programme_ids) + 1)],
            "FundType_ID": [str(pid)[:2] for pid in programme_ids],
        }
    )

    programme_data = programme_data.dropna()

    df_dict["Programme_Ref"] = programme_data

    df_dict["Programme_Ref"] = map_organisation_to_programme_id(
        df_dict["Programme_Ref"], round_1_data["programme_summary"], round_1_data["Place Identifiers"]
    )

    TD_ABBREVIATIONS, HS_ABBREVIATIONS = extract_place_identifiers(round_1_data["Place Identifiers"])

    reversed_TD = {value: key for key, value in TD_ABBREVIATIONS.items()}
    reversed_HS = {value: key for key, value in HS_ABBREVIATIONS.items()}

    place_names = list()

    for entry in programme_data["Programme ID"]:
        abbreviation = str(entry)[-3:]
        if abbreviation in reversed_TD:
            place_name = reversed_TD[abbreviation]
        elif abbreviation in reversed_HS:
            place_name = reversed_HS[abbreviation]
        else:
            place_name = None

        place_names.append(place_name)

    df_dict["Programme_Ref"]["Programme Name"] = place_names

    df_dict["Programme_Ref"] = df_dict["Programme_Ref"].dropna(subset=["Programme Name"])

    return df_dict


def map_organisation_to_programme_id(programme_refs, programme_summary, place_identifiers):
    """
    Maps organisation names to programme IDs based on the provided programme summary and place identifiers.

    :param programme_refs: Dataframe containing programme references.
    :param programme_summary: Dataframe containing programme summary.
    :param place_identifiers: Dataframe containing place identifiers.
    :return: Merged dataframe with mapped organisation names.
    """
    programme_summary = programme_summary[["place_name", "grant_recipient", "form_type"]]
    programme_summary["form_type"] = programme_summary["form_type"].replace({"FHSF": "HS", "Town Deal": "TD"})
    TD_ABBREVIATIONS, FHSF_ABBREVIATIONS = extract_place_identifiers(place_identifiers)

    def get_abbreviation(place_name):
        if place_name in TD_ABBREVIATIONS:
            return str(TD_ABBREVIATIONS[place_name])
        elif place_name in FHSF_ABBREVIATIONS:
            return str(FHSF_ABBREVIATIONS[place_name])
        else:
            return ""

    programme_summary["Programme ID"] = (
        programme_summary["form_type"] + "-" + programme_summary["place_name"].map(get_abbreviation)
    )

    programme_summary = programme_summary.drop_duplicates(subset=["Programme ID"])

    programme_summary = programme_summary[["Programme ID", "grant_recipient"]]

    merged_df = pd.merge(
        programme_refs,
        programme_summary,
        on=[
            "Programme ID",
        ],
        how="left",
    )

    merged_df = merged_df.rename(columns={"grant_recipient": "Organisation"})

    return merged_df


def extract_outcome_refs(outcome_refs: pd.DataFrame, outcomes: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts outcome references by adding unique outcome names to the outcome_refs dataframe.

    :param outcome_refs: Dataframe containing outcome references.
    :param outcomes: Dataframe containing outcome data.
    :return: Updated outcome_refs dataframe with added outcome names.
    """
    unique_outcomes = outcomes["Outcome"].unique()
    outcome_refs["Outcome_Name"] = unique_outcomes
    outcome_refs["Outcome_Category"] = outcome_refs["Outcome_Name"].map(OUTCOME_CATEGORIES).fillna("Custom")
    return outcome_refs


def update_project_details(df_dict, round_1_data):
    """
    Updates the 'Project Details' DataFrame in the given dictionary by adding missing projects
    from other DataFrames and setting desired values.

    :param df_dict: Dictionary of DataFrames.
    :param round_1_data: Dataframe containing round 1 data for reference.
    :return: Updated dictionary with the 'Project Details' DataFrame modified.
    """
    project_details = df_dict["Project Details"]

    existing_project_ids = set(project_details["Project ID"])

    for df_name, df in df_dict.items():
        if df_name != "Project Details" and "Project ID" in df.columns:
            missing_project_ids = set(df["Project ID"]) - existing_project_ids
            placenames = [
                reverse_placename_lookup(location, round_1_data["Place Identifiers"])
                for location in list(missing_project_ids)
            ]

            missing_projects = pd.DataFrame(
                {
                    "Project ID": list(missing_project_ids),
                    "Programme ID": [str(project_id)[:6] for project_id in missing_project_ids],
                    "Primary Intervention Theme": "Not Provided",
                    "Locations": placenames,
                    "Submission ID": [
                        reverse_submission_id_lookup(placename, round_1_data["lookup_programme_project"])
                        for placename in placenames
                    ],
                }
            )

            project_details = project_details._append(missing_projects, ignore_index=True)

    updated_project_details = project_details.dropna(subset=["Programme ID"])
    updated_project_details = updated_project_details[updated_project_details["Programme ID"] != "nan"]
    updated_project_details = updated_project_details.drop_duplicates(subset=["Project ID"], keep="first").reset_index(
        drop=True
    )

    updated_project_details = get_project_name(updated_project_details, round_1_data["lookup_programme_project"])
    updated_project_details = updated_project_details.dropna(subset=["Locations"])

    updated_project_details.loc[
        updated_project_details["Single or Multiple Locations"].isin(["< Select >", "None"]),
        "Single or Multiple Locations",
    ] = ""

    updated_project_details = updated_project_details.dropna(subset=["Submission ID"])

    updated_project_details["Locations"] = updated_project_details["Postcodes"].fillna("None")
    updated_project_details["Postcodes"] = updated_project_details.apply(
        lambda row: ",".join(extract_postcodes(str(row["Locations"]))), axis=1
    )
    df_dict["Project Details"] = updated_project_details

    return df_dict


def reverse_placename_lookup(location, place_identifiers):
    """
    Reverse lookup for the place name based on the location abbreviation.

    :param location: Location abbreviation.
    :param place_identifiers: DataFrame containing place identifiers.
    :return: Place name associated with the location abbreviation.
    """
    TD_ABBREVIATIONS, HS_ABBREVIATIONS = extract_place_identifiers(place_identifiers)

    reversed_TD = {value: key for key, value in TD_ABBREVIATIONS.items()}
    reversed_HS = {value: key for key, value in HS_ABBREVIATIONS.items()}

    if "-" in str(location):
        abbreviation = str(location).split("-")[1]
    else:
        abbreviation = None

    if abbreviation in reversed_TD:
        place_name = reversed_TD[abbreviation]
    elif abbreviation in reversed_HS:
        place_name = reversed_HS[abbreviation]
    else:
        place_name = None

    return place_name


def reverse_submission_id_lookup(place_name, lookup_table):
    """
    Reverse lookup for the submission ID based on the place name.

    :param place_name: Place name.
    :param lookup_table: DataFrame containing the lookup table.
    :return: Submission ID associated with the place name.
    """
    matching_rows = lookup_table.loc[lookup_table["place_name"] == place_name]

    if len(matching_rows) > 0:
        return_num = matching_rows["return_num"].values[0]

        submission_id = "S-R01-" + str(return_num)

        return submission_id
    else:
        return None


def extract_place_details(place_details, lookup_table, place_identifiers, programme_summary):
    """
    Extract place details from the lookup table and update the place_details dataframe.

    :param place_details: DataFrame containing the place details.
    :param lookup_table: DataFrame containing the lookup table.
    :param place_identifiers: DataFrame containing place identifiers.
    :param programme_summary: DataFrame containing programme summary information.
    :return: Updated place_details DataFrame.
    """
    converted_rows = []

    for _, row in lookup_table.iterrows():
        submission_id = "S-R01-" + str(row["return_num"])
        place_name = row["place_name"]
        return_num = row["return_num"]

        indicator = "Please select from the drop list provided"

        converted_rows.append(
            {
                "Submission ID": submission_id,
                "Question": "Are you filling this in for a Town Deal or Future High Street Fund?",
                "Answer": "",
                "Indicator": indicator,
                "place_name": place_name,
                "return_num": return_num,
            }
        )

        converted_rows.append(
            {
                "Submission ID": submission_id,
                "Question": "Please select your place name",
                "Answer": place_name,
                "Indicator": indicator,
                "place_name": place_name,
                "return_num": return_num,
            }
        )

        converted_rows.append(
            {
                "Submission ID": submission_id,
                "Question": "Grant Recipient:",
                "Answer": row["grant_recipient"],
                "Indicator": "Organisation Name",
                "place_name": place_name,
                "return_num": return_num,
            }
        )

    place_details = place_details._append(converted_rows, ignore_index=True)

    place_details = get_programme_id(place_details, place_identifiers, programme_summary)

    place_details.loc[
        place_details["Question"] == "Are you filling this in for a Town Deal or Future High Street Fund?", "Answer"
    ] = place_details["Programme ID"].apply(lambda x: "Town Deal" if str(x)[:2] == "TD" else "Future High Street Fund")

    place_details = place_details[["Submission ID", "Programme ID", "Question", "Answer", "Indicator"]]

    place_details = place_details.drop_duplicates(
        subset=["Submission ID", "Programme ID", "Question", "Answer", "Indicator"], keep="first"
    )

    return place_details


def drop_unused_tables(df_dict):
    """
    Drop unused tables from the DataFrame dictionary.

    :param df_dict: Dictionary of DataFrames.
    :return: Updated DataFrame dictionary with specified tables removed.
    """
    tables_to_drop = ["Private Investments", "Outputs_Ref", "Output_Data"]
    for table in tables_to_drop:
        df_dict.pop(table, None)

    return df_dict


def update_submission_id_type(df_dict):
    """
    Update the data type of the 'Submission ID' column in the DataFrame dictionary to string.

    :param df_dict: Dictionary of DataFrames.
    :return: Updated DataFrame dictionary with 'Submission ID' column data type changed to string.
    """
    column_name = "Submission ID"

    for key, df in df_dict.items():
        if column_name in df.columns:
            df[column_name] = df[column_name].astype(str)

    return df_dict


def update_to_canonical_organisation_names_round_one(df_dict: dict[str, pd.DataFrame]) -> dict[str, pd.DataFrame]:
    """
    Update the 'grant_recipient' field in each DataFrame of the DataFrame dictionary based on the 'place_name' column.

    :param df_dict: Dictionary of DataFrames.
    :return: Updated DataFrame dictionary with 'grant_recipient' field changed based on 'place_name' for programmes.
    """
    df = df_dict["programme_summary"]

    df["place_name_stripped"] = df["place_name"].str.strip()
    # Staveley is spelt wrong in R1, but is mapped to correct org name anyway
    # also the None value will map to nothing, therefore fillna to default to prevent key error
    df["grant_recipient"] = df["place_name_stripped"].map(TF_PLACE_NAMES_TO_ORGANISATIONS).fillna(df["grant_recipient"])
    df.drop("place_name_stripped", axis=1, inplace=True)
    df_dict["programme_summary"] = df

    return df_dict
