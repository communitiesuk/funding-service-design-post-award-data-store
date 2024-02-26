from datetime import datetime

import pandas as pd

from core.const import (
    OUTCOME_CATEGORIES,
    OUTPUT_CATEGORIES,
    PF_REPORTING_PERIOD_TO_DATES,
    PF_REPORTING_ROUND_TO_DATES,
    FundTypeIdEnum,
)
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
    transformed["Programme Progress"] = _programme_progress(df_dict, programme_name_to_id_mapping)
    transformed["Project Progress"] = _project_progress(df_dict, project_name_to_id_mapping)
    transformed["Funding Questions"] = _funding_questions(df_dict, programme_name_to_id_mapping)
    transformed["Funding"] = _funding_data(df_dict, programme_name_to_id_mapping)
    transformed.update(_outputs(df_dict, programme_name_to_id_mapping))
    transformed.update(_outcomes(df_dict, programme_name_to_id_mapping))
    transformed["RiskRegister"] = _risk_register(df_dict, programme_name_to_id_mapping)
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
    organisation_name = df_dict["Organisation Name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    project_ids = df_dict["Project Location"]["Project name"].map(project_name_to_id_mapping)
    location_multiplicities = df_dict["Project Location"]["Location"].map(
        lambda x: "Multiple" if "," in x else "Single"
    )
    locations = df_dict["Project Location"]["Location"].map(lambda x: x.split(","))
    postcodes = df_dict["Project Location"]["Location"].map(extract_postcodes)
    return pd.DataFrame(
        {
            "Project Name": df_dict["Project Location"]["Project name"],
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
    organisation_name = df_dict["Organisation Name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    portfolio_progress = df_dict["Portfolio Progress"].iloc[0, 0]
    big_issues = df_dict["Portfolio Big Issues"].iloc[0, 0]
    significant_milestones = df_dict["Significant Milestones"].iloc[0, 0]
    return pd.DataFrame(
        {
            "Programme ID": [programme_id] * 3,
            "Question": ["Portfolio Progress", "Big Issues", "Significant Milestones"],
            "Answer": [portfolio_progress, big_issues, significant_milestones],
        }
    )


def _project_progress(
    df_dict: dict[str, pd.DataFrame],
    project_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
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


def _funding_questions(df_dict: dict[str, pd.DataFrame], programme_name_to_id_mapping: dict[str, str]) -> pd.DataFrame:
    questions = [
        "Underspend",
        "Current Underspend",
        "Underspend Requested",
        "Spending Plan",
        "Forecast Spend",
        "Uncommitted Funding Plan",
        "Change Request Threshold",
    ]
    answers = [df_dict[q].iloc[0, 0] for q in questions]
    organisation_name = df_dict["Organisation Name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    return pd.DataFrame(
        {
            "Question": questions,
            "Guidance Notes": [pd.NA] * len(questions),
            "Indicator": [pd.NA] * len(questions),
            "Response": answers,
            "Programme ID": [programme_id] * len(questions),
        }
    )


def _funding_data(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    """
    Will need to add programme_junction_id to funding database table and implement XOR logic in mappings
    """
    organisation_name = df_dict["Organisation Name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    melted_df = pd.melt(
        df_dict["Forecast and Actual Spend"],
        id_vars=["Type of spend"],
        var_name="Reporting Period",
        value_name="Spend for Reporting Period",
    )
    start_dates = melted_df["Reporting Period"].map(
        lambda x: PF_REPORTING_PERIOD_TO_DATES[", ".join(x.split(", ")[:-1])]["start"]
    )
    end_dates = melted_df["Reporting Period"].map(
        lambda x: PF_REPORTING_PERIOD_TO_DATES[", ".join(x.split(", ")[:-1])]["end"]
    )
    actual_forecast = melted_df["Reporting Period"].map(lambda x: "Actual" if "Actual" in x else "Forecast")
    return pd.DataFrame(
        {
            "Project ID": [pd.NA] * len(melted_df),
            "Funding Source Name": [pd.NA] * len(melted_df),
            "Funding Source Type": melted_df["Type of spend"],
            "Secured": [pd.NA] * len(melted_df),
            "Spend for Reporting Period": melted_df["Spend for Reporting Period"],
            "Actual/Forecast": actual_forecast,
            "Start Date": start_dates,
            "End Date": end_dates,
            "Programme ID": [programme_id] * len(melted_df),
        }
    )


def _outputs(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> dict[str, pd.DataFrame]:
    """
    Will need to add programme_junction_id to output_data database table and implement XOR logic in mappings

        "Additional Information",
        "Project ID",
        "Output",
        "Unit of Measurement",
        "Amount",
        "Actual/Forecast",
        "Start_Date",
        "End_Date"
    """
    organisation_name = df_dict["Organisation Name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    outputs = df_dict["Outputs"]["Output"]
    output_categories = outputs.map(OUTPUT_CATEGORIES)
    melted_df = pd.melt(
        df_dict["Outputs"],
        id_vars=["Intervention theme", "Output", "Unit of measurement"],
        var_name="Reporting Period",
        value_name="Amount",
    )
    start_dates = melted_df["Reporting Period"].map(
        lambda x: PF_REPORTING_PERIOD_TO_DATES[", ".join(x.split(", ")[:-1])]["start"]
    )
    end_dates = melted_df["Reporting Period"].map(
        lambda x: PF_REPORTING_PERIOD_TO_DATES[", ".join(x.split(", ")[:-1])]["end"]
    )
    actual_forecast = melted_df["Reporting Period"].map(lambda x: "Actual" if "Actual" in x else "Forecast")
    return {
        "Outputs_Ref": pd.DataFrame(
            {
                "Output Name": outputs,
                "Output Category": output_categories,
            }
        ),
        "Output_Data": pd.DataFrame(
            {
                "Additional Information": pd.NA * len(melted_df),
                "Project ID": [pd.NA] * len(melted_df),
                "Output": melted_df["Output"],
                "Unit of Measurement": melted_df["Unit of measurement"],
                "Amount": melted_df["Amount"],
                "Actual/Forecast": actual_forecast,
                "Start_Date": start_dates,
                "End_Date": end_dates,
                "Programme ID": [programme_id] * len(melted_df),
            }
        ),
    }


def _outcomes(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> dict[str, pd.DataFrame]:
    organisation_name = df_dict["Organisation Name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    outcomes = df_dict["Outcomes"]["Outcome"]
    outcome_categories = df_dict["Outcomes"]["Intervention theme"].map(OUTCOME_CATEGORIES)
    melted_df = pd.melt(
        df_dict["Outcomes"],
        id_vars=["Intervention theme", "Outcome", "Unit of measurement"],
        var_name="Reporting Period",
        value_name="Amount",
    )
    start_dates = melted_df["Reporting Period"].map(
        lambda x: PF_REPORTING_PERIOD_TO_DATES[", ".join(x.split(", ")[:-1])]["start"]
    )
    end_dates = melted_df["Reporting Period"].map(
        lambda x: PF_REPORTING_PERIOD_TO_DATES[", ".join(x.split(", ")[:-1])]["end"]
    )
    actual_forecast = melted_df["Reporting Period"].map(lambda x: "Actual" if "Actual" in x else "Forecast")
    return {
        "Outcome_Ref": pd.DataFrame(
            {
                "Outcome Name": outcomes,
                "Outcome Category": outcome_categories,
            }
        ),
        "Outcome_Data": pd.DataFrame(
            {
                "Higher Frequency": [pd.NA] * len(melted_df),
                "Project ID": [pd.NA] * len(melted_df),
                "Programme ID": [programme_id] * len(melted_df),
                "Outcome": melted_df["Outcome"],
                "UnitofMeasurement": melted_df["Unit of measurement"],
                "GeographyIndicator": [pd.NA] * len(melted_df),
                "Amount": melted_df["Amount"],
                "Actual/Forecast": actual_forecast,
                "Start_Date": start_dates,
                "End_Date": end_dates,
            }
        ),
    }


def _risk_register(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    organisation_name = df_dict["Organisation Name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    risks = df_dict["Risks"]
    return pd.DataFrame(
        {
            "Programme ID": [programme_id] * len(risks),
            "Project ID": [pd.NA] * len(risks),
            "RiskName": risks["Risk name"],
            "RiskCategory": risks["Category"],
            "Short Description": risks["Description"],
            "Full Description": [pd.NA] * len(risks),
            "Consequences": [pd.NA] * len(risks),
            "Pre-mitigatedImpact": risks["Impact score"],
            "Pre-mitigatedLikelihood": risks["Likelihood score"],
            "Mitigations": risks["Mitigations"],
            "PostMitigatedImpact": [pd.NA] * len(risks),
            "PostMitigatedLikelihood": [pd.NA] * len(risks),
            "Proximity": [pd.NA] * len(risks),
            "RiskOwnerRole": [pd.NA] * len(risks),
        }
    )


def _project_finance_changes(df_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    return df_dict["Project Finance Changes"]
