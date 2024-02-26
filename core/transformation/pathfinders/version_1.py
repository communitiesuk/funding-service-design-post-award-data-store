from datetime import datetime

import pandas as pd

from core.const import PF_REPORTING_ROUND_TO_DATES, FundTypeIdEnum
from core.transformation.utils import extract_postcodes


def pathfinders_transform_v1(
    df_dict: dict[str, pd.DataFrame],
    reporting_round: int,
    programme_name_to_id_mapping: dict[str, str],
    project_name_to_id_mapping: dict[str, str],
    programme_project_mapping: dict[str, list[str]],
) -> dict[str, pd.DataFrame]:
    """
    Transform the data extracted from the Excel file into a format that can be loaded into the database.

    :param df_dict: Dictionary of DataFrames representing tables extracted from the original Excel file
    :return: Dictionary of DataFrames representing transformed data
    """
    transformed = {}
    transformed["Submission_Ref"] = _submission_ref(reporting_round)
    transformed["Place Details"] = _place_details(df_dict)
    transformed["Programme_Ref"] = _programme_ref(df_dict, programme_name_to_id_mapping)
    transformed["Organisation_Ref"] = _organisation_ref(df_dict)
    transformed["Project Details"] = _project_details(df_dict, programme_name_to_id_mapping, project_name_to_id_mapping)
    transformed["Programme Progress"] = _programme_progress(df_dict)
    transformed["Project Progress"] = _project_progress(df_dict)
    transformed["Funding Questions"] = _funding_questions(df_dict)
    transformed["Funding Comments"] = _funding_comments(df_dict)
    transformed["Funding"] = _funding_data(df_dict)
    transformed["Output_Data"] = _output_data(df_dict)
    transformed["Outputs_Ref"] = _outputs_ref(df_dict)
    transformed["Outcome_Data"] = _outcome_data(df_dict)
    transformed["Outcome_Ref"] = _outcome_ref(df_dict)
    transformed["RiskRegister"] = _risk_register(df_dict)
    transformed["Project Location"] = _project_location(df_dict)
    transformed["Project Finance Changes"] = _project_finance_changes(df_dict)
    return transformed


def _submission_ref(reporting_round: int) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Submission Date": [datetime.now()],
            "Reporting Period Start": [PF_REPORTING_ROUND_TO_DATES[reporting_round]["start"]],
            "Reporting Period End": [PF_REPORTING_ROUND_TO_DATES[reporting_round]["end"]],
            "Reporting Round": [reporting_round],
        }
    )


def _place_details(df_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    questions = [
        "Financial Completion Date",
        "Practical Completion Date",
        "Organisation Name",
        "Contact Name",
        "Contact Email Address",
        "Contact Telephone",
    ]
    answers = [df_dict[q].iloc[0, 0] for q in questions]
    indicators = [pd.NA] * len(questions)
    return pd.DataFrame(
        {
            "Question": questions,
            "Indicator": indicators,
            "Answer": answers,
        }
    )


def _programme_ref(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    programme_name = df_dict["Organisation Name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[programme_name]
    fund_type_id = FundTypeIdEnum.PATHFINDERS.value
    organisation_name = programme_name
    return pd.DataFrame(
        {
            "Programme ID": [programme_id],
            "Programme Name": [programme_name],
            "FundType_ID": [fund_type_id],
            "Organisation": [organisation_name],
        }
    )


def _organisation_ref(df_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Organisation Name": [df_dict["Organisation Name"].iloc[0, 0]],
            "Geography": [pd.NA],
        }
    )


def _project_details(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
    project_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    programme_id = programme_name_to_id_mapping[df_dict["Organisation Name"].iloc[0, 0]]
    project_ids = df_dict["Project Location"]["Project name"].map(project_name_to_id_mapping)
    location_multiplicities = df_dict["Project Location"]["Location"].map(
        lambda x: "Multiple" if "," in x else "Single"
    )
    locations = df_dict["Project Location"]["Location"].map(lambda x: x.split(","))
    postcodes = df_dict["Project Location"]["Location"].map(extract_postcodes)
    return pd.DataFrame(
        {
            "Project Name": df_dict["Project Location"]["Project Name"],
            "Primary Intervention Theme": [pd.NA] * len(project_ids),
            "Single or Multiple Locations": location_multiplicities,
            "GIS Provided": [pd.NA] * len(project_ids),
            "Locations": locations,
            "Postcodes": postcodes,
            "Lat/Long": [pd.NA] * len(project_ids),
            "Project ID": project_ids,
            "Programme ID": [programme_id] * len(project_ids),
        }
    )


def _programme_progress(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    programme_id = programme_name_to_id_mapping[df_dict["Organisation Name"].iloc[0, 0]]
    portfolio_progress = df_dict["Portfolio Progress"].iloc[0, 0]
    big_issues = df_dict["Portfolio Big Issues"].iloc[0, 0]
    significant_milestones = df_dict["Significant Milestones"].iloc[0, 0]
    return pd.DataFrame(
        {
            "Programme ID": [programme_id],
            "Question": ["Portfolio Progress", "Big Issues", "Significant Milestones"],
            "Answer": [portfolio_progress, big_issues, significant_milestones],
        }
    )


def _project_progress(
    df_dict: dict[str, pd.DataFrame],
    project_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    """
    "Start Date",
    "Completion Date",
    "Current Project Delivery Stage",
    "Project Delivery Status",
    "Leading Factor of Delay",
    "Project Adjustment Request Status",
    "Delivery (RAG)",
    "Spend (RAG)",
    "Risk (RAG)",
    "Commentary on Status and RAG Ratings",
    "Most Important Upcoming Comms Milestone",
    "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
    "Project ID"
    """
    project_ids = df_dict["Project Location"]["Project name"].map(project_name_to_id_mapping)
    delivery_rags = df_dict["Project Progress"]["Delivery RAG rating"]
    spend_rags = df_dict["Project Progress"]["Spend RAG rating"]
    commentaries = df_dict["Project Progress"]["Why have you given these ratings?"]
    return pd.DataFrame(
        {
            "Start Date": [pd.NA] * len(project_ids),
            "Completion Date": [pd.NA] * len(project_ids),
            "Current Project Delivery Stage": [pd.NA] * len(project_ids),
            "Project Delivery Status": [pd.NA] * len(project_ids),
            "Leading Factor of Delay": [pd.NA] * len(project_ids),
            "Project Adjustment Request Status": [pd.NA] * len(project_ids),
            "Delivery (RAG)": delivery_rags,
            "Spend (RAG)": spend_rags,
            "Risk (RAG)": [pd.NA] * len(project_ids),
            "Commentary on Status and RAG Ratings": commentaries,
            "Most Important Upcoming Comms Milestone": [pd.NA] * len(project_ids),
            "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": [pd.NA] * len(project_ids),
            "Project ID": project_ids,
        }
    )


def _funding_questions(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    pass


def _funding_comments(df_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    pass


def _funding_data(df_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    pass


def _output_data(df_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    pass


def _outputs_ref(df_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    pass


def _outcome_data(df_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    pass


def _outcome_ref(df_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    pass


def _risk_register(df_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    pass


def _project_location(df_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    pass


def _project_finance_changes(df_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    pass
