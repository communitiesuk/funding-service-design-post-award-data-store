import typing
from datetime import datetime

import pandas as pd

from data_store.const import (
    FundTypeIdEnum,
)
from data_store.transformation.utils import create_dataframe, extract_postcodes

FAS_REPORTING_PERIOD_HEADERS_TO_DATES = {
    "Total cumulative actuals to date, (Up to and including Mar 2024)": {
        "start": datetime(2019, 1, 1),
        "end": datetime(2024, 3, 31, 23, 59, 59),
    },
    "Financial year 2024 to 2025, (Apr to Jun)": {
        "start": datetime(2024, 4, 1),
        "end": datetime(2024, 6, 30, 23, 59, 59),
    },
    "Financial year 2024 to 2025, (Jul to Sep)": {
        "start": datetime(2024, 7, 1),
        "end": datetime(2024, 9, 30, 23, 59, 59),
    },
    "Financial year 2024 to 2025, (Oct to Dec)": {
        "start": datetime(2024, 10, 1),
        "end": datetime(2024, 12, 31, 23, 59, 59),
    },
    "Financial year 2024 to 2025, (Jan to Mar)": {
        "start": datetime(2025, 1, 1),
        "end": datetime(2025, 3, 31, 23, 59, 59),
    },
    "Financial year 2025 to 2026, (Apr to Jun)": {
        "start": datetime(2025, 4, 1),
        "end": datetime(2025, 6, 30, 23, 59, 59),
    },
    "Financial year 2025 to 2026, (Jul to Sep)": {
        "start": datetime(2025, 7, 1),
        "end": datetime(2025, 9, 30, 23, 59, 59),
    },
    "Financial year 2025 to 2026, (Oct to Dec)": {
        "start": datetime(2025, 10, 1),
        "end": datetime(2025, 12, 31, 23, 59, 59),
    },
    "Financial year 2025 to 2026, (Jan to Mar)": {
        "start": datetime(2026, 1, 1),
        "end": datetime(2026, 3, 31, 23, 59, 59),
    },
    "Financial year 2026 to 2027, (Apr to Jun)": {
        "start": datetime(2026, 4, 1),
        "end": datetime(2026, 6, 30, 23, 59, 59),
    },
    "Financial year 2026 to 2027, (Jul to Sep)": {
        "start": datetime(2026, 7, 1),
        "end": datetime(2026, 9, 30, 23, 59, 59),
    },
    "Financial year 2026 to 2027, (Oct to Dec)": {
        "start": datetime(2026, 10, 1),
        "end": datetime(2026, 12, 31, 23, 59, 59),
    },
    "Financial year 2026 to 2027, (Jan to Mar)": {
        "start": datetime(2027, 1, 1),
        "end": datetime(2027, 3, 31, 23, 59, 59),
    },
}


OUTPUT_REPORTING_PERIOD_HEADERS_TO_DATES = {
    "Total cumulative outputs to date, (Up to and including Mar 2024)": {
        "start": datetime(2019, 1, 1),
        "end": datetime(2024, 3, 31, 23, 59, 59),
    },
    "Financial year 2024 to 2025, (Apr to Jun)": {
        "start": datetime(2024, 4, 1),
        "end": datetime(2024, 6, 30, 23, 59, 59),
    },
    "Financial year 2024 to 2025, (Jul to Sep)": {
        "start": datetime(2024, 7, 1),
        "end": datetime(2024, 9, 30, 23, 59, 59),
    },
    "Financial year 2024 to 2025, (Oct to Dec)": {
        "start": datetime(2024, 10, 1),
        "end": datetime(2024, 12, 31, 23, 59, 59),
    },
    "Financial year 2024 to 2025, (Jan to Mar)": {
        "start": datetime(2025, 1, 1),
        "end": datetime(2025, 3, 31, 23, 59, 59),
    },
    "Financial year 2025 to 2026, (Apr to Jun)": {
        "start": datetime(2025, 4, 1),
        "end": datetime(2025, 6, 30, 23, 59, 59),
    },
    "Financial year 2025 to 2026, (Jul to Sep)": {
        "start": datetime(2025, 7, 1),
        "end": datetime(2025, 9, 30, 23, 59, 59),
    },
    "Financial year 2025 to 2026, (Oct to Dec)": {
        "start": datetime(2025, 10, 1),
        "end": datetime(2025, 12, 31, 23, 59, 59),
    },
    "Financial year 2025 to 2026, (Jan to Mar)": {
        "start": datetime(2026, 1, 1),
        "end": datetime(2026, 3, 31, 23, 59, 59),
    },
    "Financial year 2026 to 2027, (Apr to Jun)": {
        "start": datetime(2026, 4, 1),
        "end": datetime(2026, 6, 30, 23, 59, 59),
    },
    "Financial year 2026 to 2027, (Jul to Sep)": {
        "start": datetime(2026, 7, 1),
        "end": datetime(2026, 9, 30, 23, 59, 59),
    },
    "Financial year 2026 to 2027, (Oct to Dec)": {
        "start": datetime(2026, 10, 1),
        "end": datetime(2026, 12, 31, 23, 59, 59),
    },
    "Financial year 2026 to 2027, (Jan to Mar)": {
        "start": datetime(2027, 1, 1),
        "end": datetime(2027, 3, 31, 23, 59, 59),
    },
    "April 2027 and after": {"start": datetime(2027, 4, 1), "end": None},
}

OUTCOME_REPORTING_PERIOD_HEADERS_TO_DATES = {
    "Total cumulative outcomes to date, (Up to and including Mar 2024)": {
        "start": datetime(2019, 1, 1),
        "end": datetime(2024, 3, 31, 23, 59, 59),
    },
    "Financial year 2024 to 2025, (Apr to Jun)": {
        "start": datetime(2024, 4, 1),
        "end": datetime(2024, 6, 30, 23, 59, 59),
    },
    "Financial year 2024 to 2025, (Jul to Sep)": {
        "start": datetime(2024, 7, 1),
        "end": datetime(2024, 9, 30, 23, 59, 59),
    },
    "Financial year 2024 to 2025, (Oct to Dec)": {
        "start": datetime(2024, 10, 1),
        "end": datetime(2024, 12, 31, 23, 59, 59),
    },
    "Financial year 2024 to 2025, (Jan to Mar)": {
        "start": datetime(2025, 1, 1),
        "end": datetime(2025, 3, 31, 23, 59, 59),
    },
    "Financial year 2025 to 2026, (Apr to Jun)": {
        "start": datetime(2025, 4, 1),
        "end": datetime(2025, 6, 30, 23, 59, 59),
    },
    "Financial year 2025 to 2026, (Jul to Sep)": {
        "start": datetime(2025, 7, 1),
        "end": datetime(2025, 9, 30, 23, 59, 59),
    },
    "Financial year 2025 to 2026, (Oct to Dec)": {
        "start": datetime(2025, 10, 1),
        "end": datetime(2025, 12, 31, 23, 59, 59),
    },
    "Financial year 2025 to 2026, (Jan to Mar)": {
        "start": datetime(2026, 1, 1),
        "end": datetime(2026, 3, 31, 23, 59, 59),
    },
    "Financial year 2026 to 2027, (Apr to Jun)": {
        "start": datetime(2026, 4, 1),
        "end": datetime(2026, 6, 30, 23, 59, 59),
    },
    "Financial year 2026 to 2027, (Jul to Sep)": {
        "start": datetime(2026, 7, 1),
        "end": datetime(2026, 9, 30, 23, 59, 59),
    },
    "Financial year 2026 to 2027, (Oct to Dec)": {
        "start": datetime(2026, 10, 1),
        "end": datetime(2026, 12, 31, 23, 59, 59),
    },
    "Financial year 2026 to 2027, (Jan to Mar)": {
        "start": datetime(2027, 1, 1),
        "end": datetime(2027, 3, 31, 23, 59, 59),
    },
    "April 2027 and after": {"start": datetime(2027, 4, 1), "end": None},
}


def transform(df_dict: dict[str, pd.DataFrame], reporting_round: int) -> dict[str, pd.DataFrame]:
    """
    Transform the data extracted from the Excel file into a format that can be loaded into the database.

    :param df_dict: Dictionary of DataFrames representing tables extracted from the original Excel file
    :param reporting_round: The reporting round of the data
    :return: Dictionary of DataFrames representing transformed data
    """
    project_details_df = df_dict["Project details control"]
    programme_name_to_id_mapping = {
        row["Local Authority"]: row["Reference"][:6] for _, row in project_details_df.iterrows()
    }
    project_name_to_id_mapping = {row["Full name"]: row["Reference"] for _, row in project_details_df.iterrows()}
    transformed: dict[str, pd.DataFrame] = {}
    transformed["Submission_Ref"] = _submission_ref(df_dict)
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
    transformed["ProjectFinanceChange"] = _project_finance_changes(df_dict, programme_name_to_id_mapping)
    return transformed


def _submission_ref(df_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Populates `submission_dim` table:
        submission_id           - assigned during load_data
        submission_date         - from "Submission Date" in the transformed DF
        submission_filename     - assigned during load_data
        data_blob               - includes "Sign Off Name", "Sign Off Role" and "Sign Off Date" from the transformed DF
    """
    signatory_name = df_dict["Signatory name"].iloc[0, 0]
    signatory_role = df_dict["Signatory role"].iloc[0, 0]
    signature_date = typing.cast(pd.Timestamp, df_dict["Signature date"].iloc[0, 0]).isoformat()
    return create_dataframe(
        {
            "Submission Date": [datetime.now()],
            "Sign Off Name": [signatory_name],
            "Sign Off Role": [signatory_role],
            "Sign Off Date": [signature_date],
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
        "Activity end date",
        "Practical completion date",
        "Organisation name",
        "Contact name",
        "Contact email",
        "Contact telephone",
    ]
    answers = [df_dict[q].iloc[0, 0] for q in questions]
    answers = [(answer.isoformat() if isinstance(answer, pd.Timestamp) else answer) for answer in answers]
    # Filter out nan values from answers and corresponding questions
    questions, answers = zip(*[(q, a) for q, a in zip(questions, answers, strict=False) if pd.notna(a)], strict=False)  # type: ignore[assignment]
    return create_dataframe(
        {
            "Programme ID": [programme_id] * len(questions),
            "Question": questions,
            "Answer": answers,
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
    return create_dataframe(
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
    """
    # TODO: Investigate removal of NA-filled fields from transformation output, from this and other functions
    # https://dluhcdigital.atlassian.net/browse/SMD-664
    return create_dataframe(
        {
            "Organisation": [df_dict["Organisation name"].iloc[0, 0]],
        }
    )


def _project_details(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
    project_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    """
    Populates `project_dim` table
        project_id                  - from "Project ID" in the transformed DF
        project_name                - from "Project Name" in the transformed DF
        postcodes                   - from "Postcodes" in the transformed DF
        programme_junction_id       - assigned during map_data_to_models based on "Programme ID" in the transformed DF
        data_blob                   - includes "Locations" from the transformed DF
    """
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    project_ids = df_dict["Project location"]["Project name"].map(project_name_to_id_mapping)
    postcodes: pd.Series = df_dict["Project location"]["Project full postcode/postcodes (for example, AB1D 2EF)"].map(
        extract_postcodes
    )
    return create_dataframe(
        {
            "Project ID": project_ids,
            "Programme ID": [programme_id] * len(project_ids),
            "Project Name": df_dict["Project location"]["Project name"],
            "Locations": df_dict["Project location"]["Project full postcode/postcodes (for example, AB1D 2EF)"],
            "Postcodes": postcodes,
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
    prr_df = df_dict["Portfolio RAG ratings"]
    spend_ability_rag = prr_df[prr_df.iloc[:, 0] == "Your ability to spend the current spending profile"].iloc[0, 1]
    portfolio_progress_rag = prr_df[prr_df.iloc[:, 0] == "Your current portfolio-level delivery progress"].iloc[0, 1]
    big_issues = df_dict["Big issues across portfolio"].iloc[0, 0]
    significant_milestones = df_dict["Upcoming significant milestones"].iloc[0, 0]
    return create_dataframe(
        {
            "Programme ID": [programme_id] * 5,
            "Question": [
                "Portfolio progress",
                "Ability to spend current spending profile (RAG)",
                "Current portfolio-level delivery progress (RAG)",
                "Big issues across portfolio",
                "Upcoming significant milestones",
            ],
            "Answer": [
                portfolio_progress,
                spend_ability_rag,
                portfolio_progress_rag,
                big_issues,
                significant_milestones,
            ],
        }
    )


def _project_progress(
    df_dict: dict[str, pd.DataFrame],
    project_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    """
    Populates `project_progress` table:
        project_id                  - from "Project ID" in the transformed DF
        start_date                  - nullable
        end_date                    - nullable
        date_of_important_milestone - nullable
        data_blob                   - includes "Project status", "Delivery (RAG)", "Spend (RAG)", "Commentary on Status
                                      and RAG Ratings" from the transformed DF
    """
    project_ids = df_dict["Project location"]["Project name"].map(project_name_to_id_mapping)
    project_statuses = df_dict["Project progress"]["Project status"]
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
    return create_dataframe(
        {
            "Project ID": project_ids,
            "Project Status": project_statuses,
            "Delivery (RAG)": delivery_rags,
            "Spend (RAG)": spend_rags,
            "Commentary on Status and RAG Ratings": commentaries,
        }
    )


def _funding_questions(df_dict: dict[str, pd.DataFrame], programme_name_to_id_mapping: dict[str, str]) -> pd.DataFrame:
    """
    Populates `funding_question` table:
        programme_junction_id   - assigned during map_data_to_models based on "Programme ID" in the transformed DF
        data_blob               - includes "Question" and "Response" from the transformed DF
    """
    questions = [
        "Current underspend",
        "Total payment value received from MHCLG",
        "Total LA spend to date",
        "Credible plan summary",
        "Uncommitted funding plan",
        "Summary of changes below change request threshold",
    ]
    answers = [df_dict[q].iloc[0, 0] for q in questions]
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    return create_dataframe(
        {
            "Programme ID": [programme_id] * len(questions),
            "Question": questions,
            "Response": answers,
        }
    )


def _funding_data(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    """
    Populates `funding` table:
        project_id              - nullable
        start_date              - from "Start_Date" in the transformed DF
        end_date                - from "End_Date" in the transformed DF
        data_blob               - includes "Funding Source Type", "Spend for Reporting Period" and "Actual/Forecast"
                                  from the transformed DF
        programme_junction_id   - assigned during map_data_to_models based on "Programme ID" in the transformed DF
    """
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]

    capital_df = df_dict["Forecast and actual spend (capital)"]
    capital_df["Funding category"] = "Capital"

    revenue_df = df_dict["Forecast and actual spend (revenue)"]
    revenue_df["Funding category"] = "Revenue"

    combined_df = pd.concat([capital_df, revenue_df], ignore_index=True)
    melted_df = pd.melt(
        combined_df,
        id_vars=["Funding category", "Type of spend"],
        var_name="Reporting Period",
        value_name="Spend for Reporting Period",
    )
    start_dates: pd.Series = melted_df["Reporting Period"].map(
        lambda x: FAS_REPORTING_PERIOD_HEADERS_TO_DATES[", ".join(x.split(", ")[:-1])]["start"]
    )
    end_dates: pd.Series = melted_df["Reporting Period"].map(
        lambda x: FAS_REPORTING_PERIOD_HEADERS_TO_DATES[", ".join(x.split(", ")[:-1])]["end"]
    )
    actual_forecast = melted_df["Reporting Period"].map(lambda x: "Actual" if "Actual" in x else "Forecast")
    return create_dataframe(
        {
            "Programme ID": [programme_id] * len(melted_df),
            "Funding Source Name": ["Pathfinders"] * len(melted_df),
            "Funding Category": melted_df["Funding category"],
            "Funding Source Type": melted_df["Type of spend"],
            "Start_Date": start_dates,
            "End_Date": end_dates,
            "Spend for Reporting Period": melted_df["Spend for Reporting Period"],
            "Actual/Forecast": actual_forecast,
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
            project_id              - nullable
            output_id               - assigned via FK relations in map_data_to_models based on "Output" in the
                                      transformed DF "Output_Data"
            start_date              - from "Start_Date" in the transformed DF "Output_Data"
            end_date                - from "End_Date" in the transformed DF "Output_Data"
            unit_of_measurement     - from "Unit of Measurement" in the transformed DF "Output_Data"
            state                   - from "Actual/Forecast" in the transformed DF "Output_Data"
            amount                  - from "Amount" in the transformed DF "Output_Data"
            additional_information  - nullable
            programme_junction_id   - assigned during map_data_to_models based on "Programme ID" in the transformed DF
                                      "Output_Data"  # Not currently implemented
    """
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    standard_outputs = df_dict["Outputs"]["Output"]
    bespoke_outputs = df_dict["Bespoke outputs"]["Output"]
    outputs = pd.concat([standard_outputs, bespoke_outputs], ignore_index=True)
    standard_output_categories = df_dict["Outputs"]["Intervention theme"]
    bespoke_output_categories = df_dict["Bespoke outputs"]["Intervention theme"]
    output_categories = pd.concat([standard_output_categories, bespoke_output_categories], ignore_index=True)
    standard_output_melted_df = pd.melt(
        df_dict["Outputs"],
        id_vars=["Intervention theme", "Output", "Unit of measurement"],
        var_name="Reporting Period",
        value_name="Amount",
    )
    bespoke_output_melted_df = pd.melt(
        df_dict["Bespoke outputs"],
        id_vars=["Intervention theme", "Output", "Unit of measurement"],
        var_name="Reporting Period",
        value_name="Amount",
    )
    melted_df = pd.concat([standard_output_melted_df, bespoke_output_melted_df], ignore_index=True)
    start_dates: pd.Series = melted_df["Reporting Period"].map(
        lambda x: OUTPUT_REPORTING_PERIOD_HEADERS_TO_DATES[", ".join(x.split(", ")[:-1])]["start"]
    )
    end_dates: pd.Series = melted_df["Reporting Period"].map(
        lambda x: OUTPUT_REPORTING_PERIOD_HEADERS_TO_DATES[", ".join(x.split(", ")[:-1])]["end"]
    )
    actual_forecast = melted_df["Reporting Period"].map(lambda x: "Actual" if "Actual" in x else "Forecast")
    return {
        "Outputs_Ref": create_dataframe(
            {
                "Output Name": outputs,
                "Output Category": output_categories,
            }
        ),
        "Output_Data": create_dataframe(
            {
                "Programme ID": [programme_id] * len(melted_df),
                "Output": melted_df["Output"],
                "Start_Date": start_dates,
                "End_Date": end_dates,
                "Unit of Measurement": melted_df["Unit of measurement"],
                "Actual/Forecast": actual_forecast,
                "Amount": melted_df["Amount"],
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
            project_id              - nullable
            outcome_id              - assigned via FK relations in map_data_to_models based on "Outcome" in the
                                      transformed DF "Outcome_Data"
            start_date              - from "Start_Date" in the transformed DF "Outcome_Data"
            end_date                - from "End_Date" in the transformed DF "Outcome_Data"
            unit_of_measurement     - from "Unit of Measurement" in the transformed DF "Outcome_Data"
            geography_indicator     - nullable
            amount                  - from "Amount" in the transformed DF "Outcome_Data"
            state                   - from "Actual/Forecast" in the transformed DF "Outcome_Data"
            higher_frequency        - nullable
            programme_junction_id   - assigned during map_data_to_models based on "Programme ID" in the transformed DF
                                      "Outcome_Data"
    """
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    standard_outcomes = df_dict["Outcomes"]["Outcome"]
    bespoke_outcomes = df_dict["Bespoke outcomes"]["Outcome"]
    outcomes = pd.concat([standard_outcomes, bespoke_outcomes], ignore_index=True)
    standard_outcome_categories = df_dict["Outcomes"]["Intervention theme"]
    bespoke_outcome_categories = df_dict["Bespoke outcomes"]["Intervention theme"]
    outcome_categories = pd.concat([standard_outcome_categories, bespoke_outcome_categories], ignore_index=True)
    standard_outcome_melted_df = pd.melt(
        df_dict["Outcomes"],
        id_vars=["Intervention theme", "Outcome", "Unit of measurement"],
        var_name="Reporting Period",
        value_name="Amount",
    )
    bespoke_outcome_melted_df = pd.melt(
        df_dict["Bespoke outcomes"],
        id_vars=["Intervention theme", "Outcome", "Unit of measurement"],
        var_name="Reporting Period",
        value_name="Amount",
    )
    melted_df = pd.concat([standard_outcome_melted_df, bespoke_outcome_melted_df], ignore_index=True)
    start_dates: pd.Series = melted_df["Reporting Period"].map(
        lambda x: OUTCOME_REPORTING_PERIOD_HEADERS_TO_DATES[", ".join(x.split(", ")[:-1])]["start"]
    )
    end_dates: pd.Series = melted_df["Reporting Period"].map(
        lambda x: OUTCOME_REPORTING_PERIOD_HEADERS_TO_DATES[", ".join(x.split(", ")[:-1])]["end"]
    )
    actual_forecast = melted_df["Reporting Period"].map(lambda x: "Actual" if "Actual" in x else "Forecast")
    return {
        "Outcome_Ref": create_dataframe(
            {
                "Outcome_Name": outcomes,
                "Outcome_Category": outcome_categories,
            }
        ),
        "Outcome_Data": create_dataframe(
            {
                "Programme ID": [programme_id] * len(melted_df),
                "Outcome": melted_df["Outcome"],
                "Start_Date": start_dates,
                "End_Date": end_dates,
                "UnitofMeasurement": melted_df["Unit of measurement"],
                "Amount": melted_df["Amount"],
                "Actual/Forecast": actual_forecast,
            }
        ),
    }


def _risk_register(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    """
    Populates `risk_register` table:
        project_id              - nullable
        programme_junction_id   - assigned during map_data_to_models based on "Programme ID" in the transformed DF
        data_blob               - includes "Risk Name", "Risk Category", "Short Description", "Pre-mitigatedImpact",
                                  "Pre-mitigatedLikelihood", "Mitigatons", "Post-mitigatedImpact" and
                                  "Post-mitigatedLikelihood" from the transformed DF
    """
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    risks = df_dict["Risks"]
    return create_dataframe(
        {
            "Programme ID": [programme_id] * len(risks),
            "RiskName": risks["Risk name"],
            "RiskCategory": risks["Category"],
            "Short Description": risks["Description"],
            "Pre-mitigatedImpact": risks["Pre-mitigated impact score"],
            "Pre-mitigatedLikelihood": risks["Pre-mitigated likelihood score"],
            "Mitigatons": risks["Mitigations"],  # NOTE: Typo in mappings.py needs to be fixed
            "PostMitigatedImpact": risks["Post-mitigated impact score"],
            "PostMitigatedLikelihood": risks["Post-mitigated likelihood score"],
        }
    )


def _project_finance_changes(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    """
    Populates `project_finance_change` table:
        programme_junction_id   - assigned during map_data_to_models based on "Programme ID" in the transformed DF
        data_blob               - includes "Change Number", "Project Funding Moved From", "Intervention Theme Moved
                                  From", "Project Funding Moved To", "Intervention Theme Moved To", "Amount Moved",
                                  "Change Made", "Reason for Change", "Actual or Forecast" and "Reporting Period
                                  Change Takes Place" from the transformed DF
    """
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    pfcs = df_dict["Project finance changes"]
    if pfcs.empty:
        return create_dataframe({})
    return create_dataframe(
        {
            "Programme ID": [programme_id] * len(pfcs),
            "Change Number": pfcs["Change number"],
            "Project Funding Moved From": pfcs["Project funding moved from"],
            "Intervention Theme Moved From": pfcs["Intervention theme moved from"],
            "Project Funding Moved To": pfcs["Project funding moved to"],
            "Intervention Theme Moved To": pfcs["Intervention theme moved to"],
            "Amount Moved": pfcs["Amount moved"],
            "Change Made": pfcs["What changes have you made / or are planning to make? (100 words max)"],
            "Reason for Change": pfcs["Reason for change (100 words max)"],
            "Actual or Forecast": pfcs["Actual, forecast or cancelled"],
            "Reporting Period Change Takes Place": pfcs["Reporting period change takes place"],
        }
    )
