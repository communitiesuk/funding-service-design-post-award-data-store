"""
Methods specifically for extracting data from Round 1 (Excel Spreadsheet)
"""
import pandas as pd

# isort: off
from core.const import PLACE_NAME_ABBREVIATIONS, SUPPLEMENTARY_ABBREVIATION_MAPPINGS


def ingest_round_1_data(data_model: dict[pd.DataFrame], round_1_data: dict[pd.DataFrame]) -> dict[pd.DataFrame]:
    """
    Extract and transform data from Round 1 Reporting Template into column headed Pandas DataFrames.

    :param data_model: DataFrame of parsed Excel data.
            round_1_data: Dictionary of DataFrames of parsed Excel data.
    :return: Dictionary of transformed "tables" as DataFrames.
    """

    data_model_fields = extract_data_model_fields(data_model)

    df_dictionary = extract_data_model_fields(data_model)

    df_dictionary["Project Details"] = transform_project_location(
        data_model_fields["Project Details"], round_1_data["project_location"], round_1_data["lookup_programme_project"]
    )
    df_dictionary["Project Progress"] = transform_project_progress(
        data_model_fields["Project Progress"],
        round_1_data["project_progress"],
        round_1_data["lookup_programme_project"],
    )
    df_dictionary["Funding"] = transform_project_funding_profiles(
        data_model_fields["Funding"],
        round_1_data["project_funding_profiles_MASTER"],
        round_1_data["lookup_programme_project"],
    )
    df_dictionary["Funding Comments"] = transform_project_funding_comments(
        data_model_fields["Funding Comments"],
        round_1_data["project_funding_comments"],
        round_1_data["lookup_programme_project"],
    )

    project_risks = transform_project_risks(
        data_model_fields["RiskRegister"], round_1_data["project_risks"], round_1_data["lookup_programme_project"]
    )
    programme_risks = transform_programme_risks(data_model_fields["RiskRegister"], round_1_data["programme_risks"])
    df_dictionary["RiskRegister"] = pd.concat([project_risks, programme_risks], axis=0, ignore_index=True)

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


def transform_programme_risks(project_details: pd.DataFrame, programme_risks: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms programme risks data by merging with project details and applying null row filtering.

    :param project_details: DataFrame of project details.
    :param programme_risks: DataFrame of programme risks.
    :return: Transformed DataFrame after merging and null row filtering.
    """
    project_risks_subset = extract_programme_risks(programme_risks)

    project_details = project_details.rename(columns={"Project_ID": "Project ID"})

    merged_df = pd.merge(
        project_details,
        project_risks_subset,
        on=[
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

    merged_df.dropna(subset=merged_df.columns.difference(["Project ID"]), how="all", inplace=True)

    return merged_df


def extract_project_funding_comments(df_funding_comments: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts relevant columns from the project funding comments DataFrame.

    :param df_funding_comments: DataFrame of project funding comments.
    :return: Extracted DataFrame with columns 'Project ID' and 'Comment'.
    """
    # Create a subset with only the relevant columns
    df_funding_comments = df_funding_comments[["Project ID", "Value"]]

    # Rename columns to correspond to data model names for easier merge
    df_funding_comments = df_funding_comments.rename(columns={"Value": "Comment"})

    return df_funding_comments


def transform_project_funding_comments(
    project_details: pd.DataFrame, project_funding_comments: pd.DataFrame, lookup: pd.DataFrame
) -> pd.DataFrame:
    """
    Transforms project funding comments data by merging with project details and applying null row filtering.

    :param project_details: DataFrame of project details.
    :param project_funding_comments: DataFrame of project funding comments.
    :param lookup: DataFrame used for lookup operations.
    :return: Transformed DataFrame after merging and null row filtering.
    """
    with_project_id = get_project_id(
        project_funding_comments, lookup, PLACE_NAME_ABBREVIATIONS, SUPPLEMENTARY_ABBREVIATION_MAPPINGS
    )

    project_funding_comments_subset = extract_project_funding_comments(with_project_id)

    merged_df = pd.merge(project_details, project_funding_comments_subset, on=["Project ID", "Comment"], how="outer")

    merged_df.dropna(subset=merged_df.columns.difference(["Project ID"]), how="all", inplace=True)

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

    # Create a subset with only the relevant columns
    df_funding_profiles = df_funding_profiles[
        ["Project ID", "funding_source_name", "funding_source", "unsecured_funding", "time_period"]
    ]

    # Rename columns to correspond to data model names for easier merge
    df_funding_profiles = df_funding_profiles.rename(
        columns={
            "funding_source_name": "Funding Source Name",
            "funding_source": "Funding Source Type",
            "unsecured_funding": "Secured",
            "time_period": "Reporting Period",
        }
    )

    return df_funding_profiles


def transform_project_funding_profiles(
    project_details: pd.DataFrame, project_funding_profiles: pd.DataFrame, lookup: pd.DataFrame
) -> pd.DataFrame:
    """
    Transforms project funding profiles data by merging with project details and applying null row filtering.

    :param project_details: DataFrame of project details.
    :param project_funding_profiles: DataFrame of project funding profiles.
    :param lookup: DataFrame used for project ID mapping.
    :return: Transformed DataFrame after merging and null row filtering.
    """
    with_project_id = get_project_id(
        project_funding_profiles, lookup, PLACE_NAME_ABBREVIATIONS, SUPPLEMENTARY_ABBREVIATION_MAPPINGS
    )

    project_funding_profiles_subset = extract_project_funding_profiles(with_project_id)

    merged_df = pd.merge(
        project_details,
        project_funding_profiles_subset,
        on=["Project ID", "Funding Source Name", "Funding Source Type", "Secured", "Reporting Period"],
        how="outer",
    )

    merged_df.dropna(subset=merged_df.columns.difference(["Project ID"]), how="all", inplace=True)

    return merged_df


def extract_project_location(project_location: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts relevant columns from the project location DataFrame.

    :param project_location: DataFrame of project location data.
    :return: Extracted DataFrame with renamed columns.
    """
    # Create a subset with only the relevant columns
    project_location = project_location[
        ["Project ID", "place_name", "primary_intervention_theme", "site_location_type"]
    ]

    # Rename columns to correspond to data model names for easier merge
    project_location = project_location.rename(
        columns={
            "primary_intervention_theme": "Primary Intervention Theme",
            "place_name": "Locations",
            "site_location_type": "Single or Multiple Locations",
        }
    )

    return project_location


def transform_project_location(
    project_details: pd.DataFrame, project_location: pd.DataFrame, lookup: pd.DataFrame
) -> pd.DataFrame:
    """
    Transforms project location data by merging with project details and applying null row filtering.

    :param project_details: DataFrame of project details.
    :param project_location: DataFrame of project location data.
    :param lookup: DataFrame used for project ID mapping.
    :return: Transformed DataFrame after merging and null row filtering.
    """
    with_project_id = get_project_id(
        project_location, lookup, PLACE_NAME_ABBREVIATIONS, SUPPLEMENTARY_ABBREVIATION_MAPPINGS
    )

    project_location_subset = extract_project_location(with_project_id)

    merged_df = pd.merge(
        project_details,
        project_location_subset,
        on=["Project ID", "Primary Intervention Theme", "Single or Multiple Locations", "Locations"],
        how="outer",
    )

    merged_df.dropna(subset=merged_df.columns.difference(["Project ID"]), how="all", inplace=True)

    return merged_df


def extract_project_progress(df_progress: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts relevant columns from the project progress DataFrame.

    :param df_progress: DataFrame of project progress data.
    :return: Extracted DataFrame with renamed columns.
    """
    # Create a subset with only the relevant columns
    df_progress = df_progress[
        ["Project ID", "start_date", "completion_date", "status", "delivery_rag", "spend_rag", "risk_rag", "commentary"]
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
    project_details: pd.DataFrame, project_progress: pd.DataFrame, lookup: pd.DataFrame
) -> pd.DataFrame:
    """
    Transforms project progress data by merging with project details and applying null row filtering.

    :param project_details: DataFrame of project details.
    :param project_progress: DataFrame of project progress data.
    :param lookup: DataFrame used for project ID mapping.
    :return: Transformed DataFrame after merging and null row filtering.
    """
    with_project_id = get_project_id(
        project_progress, lookup, PLACE_NAME_ABBREVIATIONS, SUPPLEMENTARY_ABBREVIATION_MAPPINGS
    )

    project_progress_subset = extract_project_progress(with_project_id)

    merged_df = pd.merge(
        project_details,
        project_progress_subset,
        on=[
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

    merged_df.dropna(subset=merged_df.columns.difference(["Project ID"]), how="all", inplace=True)

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
    project_details: pd.DataFrame, project_risks: pd.DataFrame, lookup: pd.DataFrame
) -> pd.DataFrame:
    """
    Transforms project risks data by merging with project details and applying null row filtering.

    :param project_details: DataFrame of project details.
    :param project_risks: DataFrame of project risks data.
    :param lookup: DataFrame used for project ID mapping.
    :return: Transformed DataFrame after merging and null row filtering.
    """
    with_project_id = get_project_id(
        project_risks, lookup, PLACE_NAME_ABBREVIATIONS, SUPPLEMENTARY_ABBREVIATION_MAPPINGS
    )

    project_risks_subset = extract_project_risks(with_project_id)

    # Named incorrectly in data model sheet
    project_details = project_details.rename(columns={"Project_ID": "Project ID"})

    merged_df = pd.merge(
        project_details,
        project_risks_subset,
        on=[
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

    merged_df.dropna(subset=merged_df.columns.difference(["Project ID"]), how="all", inplace=True)

    return merged_df


def get_project_id(
    round_1_category: pd.DataFrame, lookup_table: pd.DataFrame, abbreviations: dict, supplementary_dict: dict
) -> pd.DataFrame:
    """
    Generates project IDs based on the round 1 category DataFrame by mapping place names, project numbers,
    and applying prefixes and abbreviations.

    :param round_1_category: DataFrame containing round 1 category data.
    :param lookup_table: DataFrame used for place name and project name mapping.
    :param abbreviations: Dictionary of abbreviations for place names.
    :param supplementary_dict: Dictionary of supplementary abbreviations for place names.
    :return: DataFrame with added 'Project ID' column.
    """
    if "proj_num" not in round_1_category.columns:
        round_1_category = get_project_number(round_1_category, lookup_table)

    prefix = "TD"

    def get_abbreviation(place_name):
        if place_name in abbreviations:
            return abbreviations[place_name]
        elif place_name in supplementary_dict:
            return supplementary_dict[place_name]
        else:
            return ""

    def get_actual_proj_num(proj_num):
        if len(proj_num) == 1:
            return "0" + proj_num
        else:
            return proj_num

    round_1_category["Project ID"] = (
        prefix
        + "-"
        + round_1_category["place_name"].map(get_abbreviation)
        + "-"
        + round_1_category["proj_num"].astype(str).map(get_actual_proj_num)
    )

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


def extract_data_model_fields(df_data_model: pd.DataFrame) -> pd.DataFrame:
    """
    Extracts data model fields from the provided DataFrame and creates an empty DataFrame for each sheet.

    :param df_data_model: DataFrame containing the data model.
    :return: Dictionary of empty DataFrames for each sheet in the data model.
    """
    data_model = {sheet_name: pd.DataFrame(columns=sheet.columns) for sheet_name, sheet in df_data_model.items()}

    return data_model
