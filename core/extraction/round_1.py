import pandas as pd


def ingest_round_1_data(df_map: pd.DataFrame) -> dict[pd.DataFrame]:
    """
    Extract data from Round 1 Reporting Template into column headed Pandas DataFrames.

    :param df_ingest: DataFrame of parsed Excel data.
    :return: Dictionary of extracted "tables" as DataFrames.
    """
    df_dictionary = dict()

    df_dictionary["programme_outcomes"] = extract_programme_outcomes(df_map["programme_outcomes"])
    df_dictionary["programme_risks"] = extract_programme_risks(df_map["programme_risks"])
    df_dictionary["programme_summary"] = extract_programme_summary(df_map["programme_summary"])
    df_dictionary["project_funding_comments"] = extract_project_funding_comments(df_map["project_funding_comments"])
    df_dictionary["project_funding_profiles"] = extract_project_funding_profiles(
        df_map["project_funding_profiles_MASTER"]
    )
    # df_dictionary["project_location"] = extract_project_details(df_map["project_location"])
    df_dictionary["project_progress"] = extract_project_progress(df_map["project_progress"])
    df_dictionary["project_risks"] = extract_project_risks(df_map["project_risks"])
    df_dictionary["postcode_region"] = extract_postcode_region(df_map["lookup_postcode_region"])
    df_dictionary["programme_project"] = extract_programme_project(df_map["lookup_programme_project"])
    df_dictionary["td_fundingcdel_rdel_accelerated"] = extract_accelerated(df_map["td_fundingcdel_rdel_accelerated"])
    df_dictionary["programme_management"] = extract_programme_management(df_map["td_funding_programme_management"])

    return df_dictionary


def extract_programme_outcomes(df_programme: pd.DataFrame) -> pd.DataFrame:
    """
    Extract programme outcomes information from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 1 Reporting - TF_aggregated_data_23.09.2022.xlsx".
    Specifically Project work sheet, parsed as dataframe.

    :param df: Input DataFrame containing data.
    :return: Extracted DataFrame containing programme data.
    """

    return df_programme


def extract_programme_risks(df_risks: pd.DataFrame) -> pd.DataFrame:
    """
    Extract programme risks information from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 1 Reporting - TF_aggregated_data_23.09.2022.xlsx".
    Specifically Project work sheet, parsed as dataframe.

    :param df: Input DataFrame containing data.
    :return: Extracted DataFrame containing programme data.
    """

    return df_risks


def extract_programme_summary(df_summary: pd.DataFrame) -> pd.DataFrame:
    """
    Extract programme summary information from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 1 Reporting - TF_aggregated_data_23.09.2022.xlsx".
    Specifically Project work sheet, parsed as dataframe.

    :param df: Input DataFrame containing data.
    :return: Extracted DataFrame containing programme data.
    """

    return df_summary


def extract_project_funding_comments(df_comments: pd.DataFrame) -> pd.DataFrame:
    """
    Extract project funding comments from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 1 Reporting - TF_aggregated_data_23.09.2022.xlsx".
    Specifically Project work sheet, parsed as dataframe.

    :param df: Input DataFrame containing data.
    :return: Extracted DataFrame containing programme data.
    """

    return df_comments


def extract_project_funding_profiles(df_funding_profiles: pd.DataFrame) -> pd.DataFrame:
    # must flip values as data model column called 'secured' and looks for opposite
    df_funding_profiles["unsecured_funding"] = df_funding_profiles["unsecured_funding"].replace(
        {"No": "Yes", "Yes": "No"}
    )

    # create a subset with only the relevant columns
    df_funding_profiles = df_funding_profiles[
        ["Project ID", "funding_source_name", "funding_source", "unsecured_funding", "time_period"]
    ]

    # rename columns to correspond to data model names for easier merge
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
    project_details: pd.DataFrame, project_funding_profiles: pd.DataFrame, project_identifiers: pd.DataFrame
) -> pd.DataFrame:
    with_project_id = get_project_id_hard(project_funding_profiles, project_identifiers)

    project_funding_profiles_subset = extract_project_funding_profiles(with_project_id)

    merged_df = pd.merge(
        project_details,
        project_funding_profiles_subset,
        on=["Project ID", "Funding Source Name", "Funding Source Type", "Secured", "Reporting Period"],
        how="outer",
    )

    merged_df.to_csv("Funding.csv", index=False)

    return merged_df


def extract_project_location(project_location: pd.DataFrame) -> pd.DataFrame:
    # create a subset with only the relevant columns
    project_location = project_location[
        ["Project ID", "place_name", "primary_intervention_theme", "site_location_type"]
    ]

    # rename columns to correspond to data model names for easier merge
    project_location = project_location.rename(
        columns={
            "primary_intervention_theme": "Primary Intervention Theme",
            "place_name": "Locations",
            "site_location_type": "Single or Multiple Locations",
        }
    )

    return project_location


def transform_project_location(
    project_details: pd.DataFrame, project_location: pd.DataFrame, project_identifiers: pd.DataFrame
) -> pd.DataFrame:
    with_project_id = get_project_id_easy(project_location, project_identifiers)
    project_location_subset = extract_project_location(with_project_id)

    merged_df = pd.merge(
        project_details,
        project_location_subset,
        on=["Project ID", "Primary Intervention Theme", "Single or Multiple Locations", "Locations"],
        how="outer",
    )

    merged_df.to_csv("Project Details.csv", index=False)

    return merged_df


def extract_project_progress(df_progress: pd.DataFrame) -> pd.DataFrame:
    # create a subset with only the relevant columns
    df_progress = df_progress[
        ["Project ID", "start_date", "completion_date", "status", "delivery_rag", "spend_rag", "risk_rag", "commentary"]
    ]

    # rename columns to correspond to data model names for easier merge
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
    project_details: pd.DataFrame, project_progress: pd.DataFrame, project_identifiers: pd.DataFrame
) -> pd.DataFrame:
    with_project_id = get_project_id_easy(project_progress, project_identifiers)
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

    merged_df.to_csv("Project Progress.csv", index=False)

    return merged_df


def extract_project_risks(df_project_risks: pd.DataFrame) -> pd.DataFrame:
    # create a subset with only the relevant columns
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

    # rename columns to correspond to data model names for easier merge
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
    project_details: pd.DataFrame, project_risks: pd.DataFrame, project_identifiers: pd.DataFrame
) -> pd.DataFrame:
    with_project_id = get_project_id_hard(project_risks, project_identifiers)

    project_risks_subset = extract_project_risks(with_project_id)

    # named incorrectly in data model sheet
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

    merged_df.to_csv("Project Risks.csv", index=False)

    return merged_df


def extract_postcode_region(df_postcode: pd.DataFrame) -> pd.DataFrame:
    """
    Extract postcode region from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 1 Reporting - TF_aggregated_data_23.09.2022.xlsx".
    Specifically Project work sheet, parsed as dataframe.

    :param df: Input DataFrame containing data.
    :return: Extracted DataFrame containing programme data.
    """

    return df_postcode


def extract_programme_project(df_programme_project: pd.DataFrame) -> pd.DataFrame:
    """
    Extract programme project information from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 1 Reporting - TF_aggregated_data_23.09.2022.xlsx".
    Specifically Project work sheet, parsed as dataframe.

    :param df: Input DataFrame containing data.
    :return: Extracted DataFrame containing programme data.
    """

    return df_programme_project


def extract_accelerated(df_accelerated: pd.DataFrame) -> pd.DataFrame:
    """
    Extract td funding accelerated information from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 1 Reporting - TF_aggregated_data_23.09.2022.xlsx".
    Specifically Project work sheet, parsed as dataframe.

    :param df: Input DataFrame containing data.
    :return: Extracted DataFrame containing programme data.
    """

    return df_accelerated


def extract_programme_management(df_programme_management: pd.DataFrame) -> pd.DataFrame:
    """
    Extract programme management information from a DataFrame.

    Input dataframe is parsed from Excel spreadsheet: "Round 1 Reporting - TF_aggregated_data_23.09.2022.xlsx".
    Specifically Project work sheet, parsed as dataframe.

    :param df: Input DataFrame containing data.
    :return: Extracted DataFrame containing programme data.
    """

    return df_programme_management


def extract_project_identifiers(df_project_identifiers: pd.DataFrame) -> pd.DataFrame:
    df_project_identifiers = df_project_identifiers.iloc[2:760, 1:4]
    df_project_identifiers = df_project_identifiers.rename(
        columns={"Unnamed: 1": "Project ID", "Unnamed: 2": "place_name", "Unnamed: 3": "project_name"}
    )

    return df_project_identifiers


# if the round_1_category contains both proj_name & place_name can lookup Project ID directly in project_indentifiers
def get_project_id_easy(round_1_category: pd.DataFrame, project_identifiers: pd.DataFrame) -> pd.DataFrame:
    round_1_category = round_1_category.rename(columns={"proj_name": "project_name"})
    merged_df = pd.merge(round_1_category, project_identifiers, on=["project_name", "place_name"], how="left")

    # Filter rows where Project ID is missing
    missing_data = merged_df[merged_df["Project ID"].isnull()]

    # Get the project names and place names with missing Project ID
    missing_project_ids = missing_data[["project_name", "place_name"]].values.tolist()
    print(missing_project_ids)

    return merged_df


def get_project_id_hard(round_1_category: pd.DataFrame, project_identifiers: pd.DataFrame) -> pd.DataFrame:
    round_1_category_with_name_and_place = get_project_name(round_1_category, round_1_data["lookup_programme_project"])

    merged_df = pd.merge(
        round_1_category_with_name_and_place, project_identifiers, on=["project_name", "place_name"], how="left"
    )

    # Filter rows where Project ID is missing
    missing_data = merged_df[merged_df["Project ID"].isnull()]

    # Get the project names and place names with missing Project ID
    missing_project_ids = missing_data[["project_name", "place_name"]].values.tolist()
    print(missing_project_ids)

    return merged_df


# if round_1_category contains no proj_name get here via the lookup table
def get_project_name(round_1_category: pd.DataFrame, lookup_table: pd.DataFrame) -> pd.DataFrame:
    lookup_table = lookup_table[["project_name", "return_num", "proj_num"]]
    merged_df = pd.merge(round_1_category, lookup_table, on=["return_num", "proj_num"], how="left")

    merged_df.to_csv("test.csv", index=False)

    return merged_df


def extract_data_model_fields(df_data_model: pd.DataFrame) -> pd.DataFrame:
    data_model = {sheet_name: pd.DataFrame(columns=sheet.columns) for sheet_name, sheet in df_data_model.items()}

    return data_model


round_1_data = pd.read_excel("Round 1 Reporting - TF_aggregated_data_23.09.2022.xlsx", sheet_name=None)

data_model = pd.read_excel("Data Model v3.7.xlsx", sheet_name=None)
data_model = extract_data_model_fields(data_model)

project_identifiers = pd.read_excel(
    "EXAMPLE_TF_Reporting_Template_-_TD_-_Newhaven_-_DDMMYY.xlsx", sheet_name="Project Identifiers"
)
project_identifiers = extract_project_identifiers(project_identifiers)

transform_project_location(data_model["Project Details"], round_1_data["project_location"], project_identifiers)
transform_project_progress(data_model["Project Progress"], round_1_data["project_progress"], project_identifiers)
transform_project_funding_profiles(
    data_model["Funding"], round_1_data["project_funding_profiles_MASTER"], project_identifiers
)
transform_project_risks(data_model["RiskRegister"], round_1_data["project_risks"], project_identifiers)
