import typing
from datetime import datetime

import pandas as pd

from data_store.const import (
    FundTypeIdEnum,
)
from data_store.transformation.utils import create_dataframe, extract_postcodes

FAS_REPORTING_PERIOD_HEADERS_TO_DATES = {
    "Financial year 2023 to 2024, (Jan to Mar)": {
        "start": datetime(2024, 1, 1),
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
}


OUTPUT_OUTCOME_REPORTING_PERIOD_HEADERS_TO_DATES = {
    "Financial year 2023 to 2024, (Jan to Mar)": {
        "start": datetime(2024, 1, 1),
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
    "April 2026 and after": {"start": datetime(2026, 4, 1), "end": None},
}


BESPOKE_OUTPUT_DISCREPANCY_MAPPING: dict[str, str] = {
    "Amount of Floor Space Ratinalised (Sqm)": "Amount of Floor Space Rationalised (Sqm)",
    "number of cleared sites": "Number of cleared sites",
    "m2 of heritage buildings renovated/restored": "m2 of Heritage buildings renovated/restored",
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
    signatory_name = df_dict["Signatory name"].iloc[0, 0]
    signatory_role = df_dict["Signatory role"].iloc[0, 0]
    signature_date = typing.cast(pd.Timestamp, df_dict["Signature date"].iloc[0, 0]).isoformat()
    return create_dataframe(
        {
            "submission_date": [datetime.now()],
            "sign_off_name": [signatory_name],
            "sign_off_role": [signatory_role],
            "sign_off_date": [signature_date],
        }
    )


def _place_details(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    questions = [
        "Financial completion date",
        "Practical completion date",
        "Organisation name",
        "Contact name",
        "Contact email",
        "Contact telephone",
    ]
    answers = [df_dict[q].iloc[0, 0] for q in questions]
    answers = [(answer.isoformat() if isinstance(answer, pd.Timestamp) else answer) for answer in answers]
    # Filter out nan values from answers and corresponding questions
    questions_zip, answers_zip = zip(
        *[(q, a) for q, a in zip(questions, answers, strict=False) if pd.notna(a)], strict=False
    )
    return create_dataframe(
        {
            "programme_id": [programme_id] * len(questions_zip),
            "question": questions_zip,
            "answer": answers_zip,
        }
    )


def _programme_ref(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    programme_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[programme_name]
    fund_type_id = FundTypeIdEnum.PATHFINDERS.value
    organisation_name = programme_name
    return create_dataframe(
        {
            "programme_id": [programme_id],
            "programme_name": [programme_name],
            "fund_type_id": [fund_type_id],
            "organisation": [organisation_name],
        }
    )


def _organisation_ref(df_dict: dict[str, pd.DataFrame]) -> pd.DataFrame:
    # TODO: Investigate removal of NA-filled fields from transformation output, from this and other functions
    # https://dluhcdigital.atlassian.net/browse/SMD-664
    return create_dataframe(
        {
            "organisation_name": [df_dict["Organisation name"].iloc[0, 0]],
        }
    )


def _project_details(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
    project_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    project_ids = df_dict["Project location"]["Project name"].map(project_name_to_id_mapping)
    postcodes: pd.Series = df_dict["Project location"]["Project full postcode/postcodes (for example, AB1D 2EF)"].map(
        extract_postcodes
    )
    return create_dataframe(
        {
            "project_id": project_ids,
            "programme_id": [programme_id] * len(project_ids),
            "project_name": df_dict["Project location"]["Project name"],
            "locations": df_dict["Project location"]["Project full postcode/postcodes (for example, AB1D 2EF)"],
            "postcodes": postcodes,
        }
    )


def _programme_progress(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    portfolio_progress = df_dict["Portfolio progress"].iloc[0, 0]
    big_issues = df_dict["Big issues across portfolio"].iloc[0, 0]
    significant_milestones = df_dict["Upcoming significant milestones"].iloc[0, 0]
    return create_dataframe(
        {
            "programme_id": [programme_id] * 3,
            "question": ["Portfolio progress", "Big issues across portfolio", "Upcoming significant milestones"],
            "answer": [portfolio_progress, big_issues, significant_milestones],
        }
    )


def _project_progress(
    df_dict: dict[str, pd.DataFrame],
    project_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
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
    return create_dataframe(
        {
            "project_id": project_ids,
            "delivery_rag": delivery_rags,
            "spend_rag": spend_rags,
            "commentary": commentaries,
        }
    )


def _funding_questions(df_dict: dict[str, pd.DataFrame], programme_name_to_id_mapping: dict[str, str]) -> pd.DataFrame:
    questions = [
        "Credible plan",
        "Total underspend",
        "Proposed underspend use",
        "Credible plan summary",
        "Current underspend",
        "Uncommitted funding plan",
        "Summary of changes below change request threshold",
    ]
    answers = [df_dict[q].iloc[0, 0] for q in questions]
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    return create_dataframe(
        {
            "programme_id": [programme_id] * len(questions),
            "question": questions,
            "response": answers,
        }
    )


def _funding_data(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    melted_df = pd.melt(
        df_dict["Forecast and actual spend"],
        id_vars=["Type of spend"],
        var_name="Reporting Period",
        value_name="spend_for_reporting_period",
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
            "programme_id": [programme_id] * len(melted_df),
            "funding_source": ["Pathfinders"] * len(melted_df),
            "spend_type": melted_df["Type of spend"],
            "start_date": start_dates,
            "end_date": end_dates,
            "spend_for_reporting_period": melted_df["spend_for_reporting_period"],
            "state": actual_forecast,
        }
    )


def _outputs(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> dict[str, pd.DataFrame]:
    # Certain bespoke outputs had small text changes after round 1, which were then applied manually to the database.
    # This mapping is used to ensure that the bespoke outputs are consistent with the database in case we re-ingest a
    # round 1 file.
    df_dict["Bespoke outputs"]["Output"].replace(BESPOKE_OUTPUT_DISCREPANCY_MAPPING, inplace=True)

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
        lambda x: OUTPUT_OUTCOME_REPORTING_PERIOD_HEADERS_TO_DATES[", ".join(x.split(", ")[:-1])]["start"]
    )
    end_dates: pd.Series = melted_df["Reporting Period"].map(
        lambda x: OUTPUT_OUTCOME_REPORTING_PERIOD_HEADERS_TO_DATES[", ".join(x.split(", ")[:-1])]["end"]
    )
    actual_forecast = melted_df["Reporting Period"].map(lambda x: "Actual" if "Actual" in x else "Forecast")
    return {
        "Outputs_Ref": create_dataframe(
            {
                "output_name": outputs,
                "output_category": output_categories,
            }
        ),
        "Output_Data": create_dataframe(
            {
                "programme_id": [programme_id] * len(melted_df),
                "output": melted_df["Output"],
                "start_date": start_dates,
                "end_date": end_dates,
                "unit_of_measurement": melted_df["Unit of measurement"],
                "state": actual_forecast,
                "amount": melted_df["Amount"],
            }
        ),
    }


def _outcomes(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> dict[str, pd.DataFrame]:
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
        lambda x: OUTPUT_OUTCOME_REPORTING_PERIOD_HEADERS_TO_DATES[", ".join(x.split(", ")[:-1])]["start"]
    )
    end_dates: pd.Series = melted_df["Reporting Period"].map(
        lambda x: OUTPUT_OUTCOME_REPORTING_PERIOD_HEADERS_TO_DATES[", ".join(x.split(", ")[:-1])]["end"]
    )
    actual_forecast = melted_df["Reporting Period"].map(lambda x: "Actual" if "Actual" in x else "Forecast")
    return {
        "Outcome_Ref": create_dataframe(
            {
                "outcome_name": outcomes,
                "outcome_category": outcome_categories,
            }
        ),
        "Outcome_Data": create_dataframe(
            {
                "programme_id": [programme_id] * len(melted_df),
                "outcome": melted_df["Outcome"],
                "start_date": start_dates,
                "end_date": end_dates,
                "unit_of_measurement": melted_df["Unit of measurement"],
                "amount": melted_df["Amount"],
                "state": actual_forecast,
            }
        ),
    }


def _risk_register(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    risks = df_dict["Risks"]
    return create_dataframe(
        {
            "programme_id": [programme_id] * len(risks),
            "risk_name": risks["Risk name"],
            "risk_category": risks["Category"],
            "short_desc": risks["Description"],
            "pre_mitigated_impact": risks["Pre-mitigated impact score"],
            "pre_mitigated_likelihood": risks["Pre-mitigated likelihood score"],
            "mitigations": risks["Mitigations"],
            "post_mitigated_impact": risks["Post-mitigated impact score"],
            "post_mitigated_likelihood": risks["Post-mitigated likelihood score"],
        }
    )


def _project_finance_changes(
    df_dict: dict[str, pd.DataFrame],
    programme_name_to_id_mapping: dict[str, str],
) -> pd.DataFrame:
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    programme_id = programme_name_to_id_mapping[organisation_name]
    pfcs = df_dict["Project finance changes"]
    return create_dataframe(
        {
            "programme_id": [programme_id] * len(pfcs),
            "change_number": pfcs["Change number"],
            "project_funding_moved_from": pfcs["Project funding moved from"],
            "intervention_theme_moved_from": pfcs["Intervention theme moved from"],
            "project_funding_moved_to": pfcs["Project funding moved to"],
            "intervention_theme_moved_to": pfcs["Intervention theme moved to"],
            "amount_moved": pfcs["Amount moved"],
            "changes_made": pfcs["What changes have you made / or are planning to make? (100 words max)"],
            "reasons_for_change": pfcs["Reason for change (100 words max)"],
            "state": pfcs["Actual, forecast or cancelled"],
            "reporting_period_change_takes_place": pfcs["Reporting period change takes place"],
        }
    )
