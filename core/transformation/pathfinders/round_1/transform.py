from datetime import datetime

import pandas as pd

from core.const import FundTypeIdEnum
from core.transformation.pathfinders.consts import (
    PF_REPORTING_PERIOD_TO_DATES,
    PF_REPORTING_ROUND_TO_DATES,
)
from core.transformation.pathfinders.round_1.control_mappings import (
    create_control_mappings,
)
from core.transformation.utils import extract_postcodes


def pathfinders_transform(
    df_dict: dict[str, pd.DataFrame],
    reporting_round: int,
) -> dict[str, pd.DataFrame]:
    """
    Transform the data extracted from the Excel file into a format that can be loaded into the database.

    :param df_dict: Dictionary of DataFrames representing tables extracted from the original Excel file
    :param reporting_round: The reporting round of the data
    :return: Dictionary of DataFrames representing transformed data
    """
    control_mappings = create_control_mappings(df_dict)
    programme_name_to_id_mapping = control_mappings["programme_name_to_id"]
    project_name_to_id_mapping = control_mappings["project_name_to_id"]
    transformed = {}
    transformed["Submission_Ref"] = _submission_ref(df_dict, reporting_round)
    transformed["Place Details"] = _place_details(df_dict, programme_name_to_id_mapping)
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
    transformed["Project Finance Changes"] = _project_finance_changes(df_dict, programme_name_to_id_mapping)
    return transformed


def _submission_ref(
    df_dict: dict[str, pd.DataFrame],
    reporting_round: int,
) -> pd.DataFrame:
    """
    Populates `submission_dim` table:
        submission_date         - from "Submission Date" in the transformed DF
        ingest_date             - assigned on DB insert as current date
        reporting_period_start  - from "Reporting Period Start" in the transformed DF
        reporting_period_end    - from "Reporting Period End" in the transformed DF
        reporting_round         - from "Reporting Round" in the transformed DF
        submission_filename     - assigned during load_data
        data_blob               - includes "Sign Off Name", "Sign Off Role" and "Sign Off Date" from the transformed DF
    """
    sign_off_name = df_dict["Sign off name"].iloc[0, 0]
    sign_off_role = df_dict["Sign off role"].iloc[0, 0]
    sign_off_date = df_dict["Sign off date"].iloc[0, 0]
    return pd.DataFrame(
        {
            "Submission Date": [datetime.now()],
            "Reporting Period Start": [PF_REPORTING_ROUND_TO_DATES[reporting_round]["start"]],
            "Reporting Period End": [PF_REPORTING_ROUND_TO_DATES[reporting_round]["end"]],
            "Reporting Round": [reporting_round],
            "Sign Off Name": [sign_off_name],
            "Sign Off Role": [sign_off_role],
            "Sign Off Date": [sign_off_date],
        }
    )


def _place_details(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    """
    Populates `place_detail` table:
        programme_junction_id   - assigned during map_data_to_models based on "Programme ID" in the transformed DF
        data_blob               - includes "Question" and "Answer" from the transformed DF
    """
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    questions = [
        "Financial completion date",
        "Practical completion date",
        "Organisation name",
        "Contact name",
        "Contact email address",
        "Contact telephone",
    ]
    answers = [df_dict[q].iloc[0, 0] for q in questions]
    return pd.DataFrame(
        {
            "Question": questions,
            "Answer": answers,
            "Programme ID": [programme_id] * len(questions),
        }
    )


def _programme_ref(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    """
    Populates `programme_dim` table:
        programme_id    - from "Programme ID" in the transformed DF
        programme_name  - from "Programme Name" in the transformed DF
        fund_type_id    - from "FundType_ID" in the transformed DF
        organisation_id - assigned via FK relations in map_data_to_models based on "Organisation" in the transformed DF
    """
    programme_name = df_dict["Organisation name"].iloc[0, 0]
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
    """
    Populates `organisation_dim` table:
        organisation_name   - from "Organisation Name" in the transformed DF
        geography           - from "Geography" in the transformed DF
    """
    # TODO: Investigate removal of NA-filled fields from transformation output, from this and other functions
    # https://dluhcdigital.atlassian.net/browse/SMD-664
    return pd.DataFrame(
        {
            "Organisation Name": [df_dict["Organisation name"].iloc[0, 0]],
            "Geography": [pd.NA],
        }
    )


def _project_details(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
    project_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    """
    Populates `project_dim` table
        programme_junction_id       - assigned during map_data_to_models based on "Programme ID" in the transformed DF
        project_id                  - from "Project ID" in the transformed DF
        project_name                - from "Project Name" in the transformed DF
        primary_intervention_theme  - from "Primary Intervention Theme" in the transformed DF
        location_multiplicity       - from "Single or Multiple Locations" in the transformed DF
        locations                   - from "Locations" in the transformed DF
        postcodes                   - from "Postcodes" in the transformed DF
        gis_provided                - from "GIS Provided" in the transformed DF
        lat_long                    - from "Lat/Long" in the transformed DF
    """
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    project_ids = df_dict["Project location"]["Project name"].map(project_name_to_id_mapping)
    location_multiplicities = df_dict["Project location"]['Project full postcode/postcodes (e.g., "AB1D 2EF")'].map(
        lambda x: "Multiple" if "," in x else "Single"
    )
    locations = df_dict["Project location"]['Project full postcode/postcodes (e.g., "AB1D 2EF")'].map(
        lambda x: list(map(str.strip, x.split(",")))
    )
    postcodes = df_dict["Project location"]['Project full postcode/postcodes (e.g., "AB1D 2EF")'].map(extract_postcodes)
    return pd.DataFrame(
        {
            "Project Name": df_dict["Project location"]["Project name"],
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
    """
    Populates `programme_progress` table:
        programme_junction_id   - assigned during map_data_to_models based on "Programme ID" in the transformed DF
        data_blob               - includes "Question" and "Answer" from the transformed DF
    """
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    portfolio_progress = df_dict["Portfolio progress"].iloc[0, 0]
    big_issues = df_dict["Portfolio big issues"].iloc[0, 0]
    significant_milestones = df_dict["Significant milestones"].iloc[0, 0]
    return pd.DataFrame(
        {
            "Programme ID": [programme_id] * 3,
            "Question": ["Portfolio progress", "Portfolio big issues", "Significant milestones"],
            "Answer": [portfolio_progress, big_issues, significant_milestones],
        }
    )


def _project_progress(
    df_dict: dict[str, pd.DataFrame],
    project_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    """
    Populates `project_progress` table:
        project_id                  - from "Project ID" in the transformed DF
        start_date                  - from "Start Date" in the transformed DF
        end_date                    - from "Completion Date" in the transformed DF
        data_blob                   - includes "Delivery (RAG)", "Spend (RAG)", "Commentary on Status and RAG Ratings"
                                      from the transformed DF
        date_of_important_milestone - from "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)" in the
                                      transformed DF
    """
    project_ids = df_dict["Project location"]["Project name"].map(project_name_to_id_mapping)
    rag_to_integer_mapping = {
        "Green": 1,
        "Amber/Green": 2,
        "Amber": 3,
        "Amber/Red": 4,
        "Red": 5,
    }
    delivery_rags = df_dict["Project progress"]["Delivery RAG rating"].map(rag_to_integer_mapping)
    spend_rags = df_dict["Project progress"]["Spend RAG rating"].map(rag_to_integer_mapping)
    commentaries = df_dict["Project progress"]["Why have you given these ratings? Enter an explanation (100 words max)"]
    return pd.DataFrame(
        {
            "Start Date": [pd.NA] * len(project_ids),
            "Completion Date": [pd.NA] * len(project_ids),
            "Delivery (RAG)": delivery_rags,
            "Spend (RAG)": spend_rags,
            "Commentary on Status and RAG Ratings": commentaries,
            "Project ID": project_ids,
        }
    )


def _funding_questions(df_dict: dict[str, pd.DataFrame], programme_name_to_id_mapping: dict[str, str]) -> pd.DataFrame:
    """
    Populates `funding_question` table:
        programme_junction_id   - assigned during map_data_to_models based on "Programme ID" in the transformed DF
        data_blob               - includes "Question" and "Response" from the transformed DF
    """
    questions = [
        "Credible plan",
        "Total underspend",
        "Underspend use proposal",
        "Credible plan summary",
        "Current underspend",
        "Uncommitted funding plan",
        "Changes below threshold summary",
    ]
    answers = [df_dict[q].iloc[0, 0] for q in questions]
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    return pd.DataFrame(
        {
            "Question": questions,
            "Response": answers,
            "Programme ID": [programme_id] * len(questions),
        }
    )


def _funding_data(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    """
    Populates `funding` table:
        project_id      - from "Project ID" in the transformed DF
        data_blob       - includes "Funding Source Type", "Spend for Reporting Period" and "Actual/Forecast" from the
                          transformed DF
        start_date      - from "Start_Date" in the transformed DF
        end_date        - from "End_Date" in the transformed DF
    """
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    melted_df = pd.melt(
        df_dict["Forecast and actual spend"],
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
            "Funding Source Type": melted_df["Type of spend"],
            "Spend for Reporting Period": melted_df["Spend for Reporting Period"],
            "Actual/Forecast": actual_forecast,
            "Start_Date": start_dates,
            "End_Date": end_dates,
            "Programme ID": [programme_id] * len(melted_df),
        }
    )


def _outputs(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> dict[str, pd.DataFrame]:
    """
    Populates `output_dim` and `output_data` tables:
        For `output_dim`:
            output_name     - from "Output" in the transformed DF "Outputs_Ref"
            output_category - from "Output Category" in the transformed DF "Outputs_Ref"

        For `output_data`:
            project_id              - from "Project ID" in the transformed DF "Output_Data"
            programme_junction_id   - assigned during map_data_to_models based on "Programme ID" in the transformed DF
                                      "Output_Data"
            output_id               - assigned via FK relations in map_data_to_models based on "Output" in the
                                      transformed DF "Output_Data"
            start_date              - from "Start_Date" in the transformed DF "Output_Data"
            end_date                - from "End_Date" in the transformed DF "Output_Data"
            unit_of_measurement     - from "Unit of Measurement" in the transformed DF "Output_Data"
            state                   - from "Actual/Forecast" in the transformed DF "Output_Data"
            amount                  - from "Amount" in the transformed DF "Output_Data"
            additional_information  - from "Additional Information" in the transformed DF "Output_Data"
    """
    # TODO: Handle bespoke outputs
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    outputs = df_dict["Outputs"]["Output"]
    output_categories = df_dict["Outputs"]["Intervention theme"]
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
    """
    Populates `outcome_dim` and `outcome_data` tables:
        For `outcome_dim`:
            outcome_name     - from "Outcome" in the transformed DF "Outcome_Ref"
            outcome_category - from "Outcome Category" in the transformed DF "Outcome_Ref"

        For `outcome_data`:
            project_id              - from "Project ID" in the transformed DF "Outcome_Data"
            programme_junction_id   - assigned during map_data_to_models based on "Programme ID" in the transformed DF
                                      "Outcome_Data"
            outcome_id              - assigned via FK relations in map_data_to_models based on "Outcome" in the
                                      transformed DF "Outcome_Data"
            start_date              - from "Start_Date" in the transformed DF "Outcome_Data"
            end_date                - from "End_Date" in the transformed DF "Outcome_Data"
            unit_of_measurement     - from "Unit of Measurement" in the transformed DF "Outcome_Data"
            geography_indicator     - from "Geography Indicator" in the transformed DF "Outcome_Data"
            amount                  - from "Amount" in the transformed DF "Outcome_Data"
            state                   - from "Actual/Forecast" in the transformed DF "Outcome_Data"
            higher_frequency        - from "Higher Frequency" in the transformed DF "Outcome_Data"
    """
    # TODO: Handle bespoke outcomes
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    outcomes = df_dict["Outcomes"]["Outcome"]
    outcome_categories = df_dict["Outcomes"]["Intervention theme"]
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
    """
    Populates `risk_register` table:
        project_id              - from "Project ID" in the transformed DF
        programme_junction_id   - assigned during map_data_to_models based on "Programme ID" in the transformed DF
        data_blob               - includes "Risk Name", "Risk Category", "Short Description", "Pre-mitigated Impact",
                                  "Pre-mitigated Likelihood" and "Mitigations" from the transformed DF
    """
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    risks = df_dict["Risks"]
    return pd.DataFrame(
        {
            "Programme ID": [programme_id] * len(risks),
            "Project ID": [pd.NA] * len(risks),
            "RiskName": risks["Risk name"],
            "RiskCategory": risks["Category"],
            "Short Description": risks["Description"],
            "Pre-mitigatedImpact": risks["Impact score"],
            "Pre-mitigatedLikelihood": risks["Likelihood score"],
            "Mitigations": risks["Mitigations"],
        }
    )


def _project_finance_changes(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    """
    Populates `project_finance_changes` table: # NOTE: This table does not exist in the current schema
        project_id              - from "Project ID" in the transformed DF
        data_blob               - includes "Change Number", "Project Funding Moved From", "Intervention Theme Moved
                                  From", "Project Funding Moved To", "Intervention Theme Moved To", "Amount Moved",
                                  "Changes Made", "Reason for Change", "Forecast or Actual Change" and "Reporting Period
                                  Change Took Place" from the transformed DF
    """
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    df = df_dict["Project finance changes"]
    df["Programme ID"] = programme_id
    return df
