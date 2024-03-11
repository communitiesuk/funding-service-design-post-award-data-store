import datetime

import pandas as pd
from pandas._testing import assert_frame_equal

import core.transformation.pathfinders.round_1.transform as pf


def test_pathfinders_transform(mock_df_dict: dict[str, pd.DataFrame]):
    pf.pathfinders_transform(df_dict=mock_df_dict, reporting_round=1)


def test__submission_ref(mock_df_dict: dict[str, pd.DataFrame]):
    transformed_df = pf._submission_ref(df_dict=mock_df_dict, reporting_round=1)
    row = transformed_df.iloc[0]
    assert isinstance(row["Submission Date"], pd.Timestamp)
    assert row["Reporting Period Start"] == datetime.datetime(2024, 4, 1)
    assert row["Reporting Period End"] == datetime.datetime(2024, 6, 30)
    assert row["Reporting Round"] == 1
    assert row["Sign Off Name"] == "Graham Bell"
    assert row["Sign Off Role"] == "Project Manager"
    assert row["Sign Off Date"] == pd.Timestamp("2024-03-05")


def test__place_details(
    mock_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._place_details(
        df_dict=mock_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Programme ID": ["PF-BOL"] * 6,
            "Question": [
                "Financial completion date",
                "Practical completion date",
                "Organisation name",
                "Contact name",
                "Contact email address",
                "Contact telephone",
            ],
            "Answer": [
                pd.Timestamp("2001-01-01 00:00:00"),
                pd.Timestamp("2001-01-01 00:00:00"),
                "Bolton Metropolitan Borough Council",
                "Steve Jobs",
                "testing@test.gov.uk",
                pd.NA,
            ],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__programme_ref(
    mock_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._programme_ref(
        df_dict=mock_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Programme ID": ["PF-BOL"],
            "Programme Name": ["Bolton Metropolitan Borough Council"],
            "FundType_ID": ["PF"],
            "Organisation": ["Bolton Metropolitan Borough Council"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__organisation_ref(
    mock_df_dict: dict[str, pd.DataFrame],
):
    transformed_df = pf._organisation_ref(df_dict=mock_df_dict)
    expected_df = pd.DataFrame(
        {
            "Organisation": ["Bolton Metropolitan Borough Council"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__project_details(
    mock_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
    mock_project_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._project_details(
        df_dict=mock_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
        project_name_to_id_mapping=mock_project_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Project ID": ["PF-BOL-001", "PF-BOL-002"],
            "Programme ID": ["PF-BOL", "PF-BOL"],
            "Project Name": ["Wellsprings Innovation Hub", "Bolton Market Upgrades"],
            "Single or Multiple Locations": ["Single", "Multiple"],
            "Locations": [["BL1 1SE"], ["BL1 1TJ", "BL1 1TQ"]],
            "Postcodes": [["BL1 1SE"], ["BL1 1TJ", "BL1 1TQ"]],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__programme_progress(
    mock_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._programme_progress(
        df_dict=mock_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Programme ID": ["PF-BOL"] * 3,
            "Question": [
                "Portfolio progress",
                "Portfolio big issues",
                "Significant milestones",
            ],
            "Answer": [
                "word word word word word",
                "some big issues",
                "some milestones",
            ],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__project_progress(
    mock_df_dict: dict[str, pd.DataFrame],
    mock_project_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._project_progress(
        df_dict=mock_df_dict,
        project_name_to_id_mapping=mock_project_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Project ID": ["PF-BOL-001", "PF-BOL-002"],
            "Delivery (RAG)": [1, 3],
            "Spend (RAG)": [2, 1],
            "Commentary on Status and RAG Ratings": ["No comment", "Wouldn't you like to know"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__funding_questions(
    mock_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._funding_questions(
        df_dict=mock_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    questions = [
        "Credible plan",
        "Total underspend",
        "Underspend use proposal",
        "Credible plan summary",
        "Current underspend",
        "Uncommitted funding plan",
        "Changes below threshold summary",
    ]
    expected_df = pd.DataFrame(
        {
            "Programme ID": ["PF-BOL"] * len(questions),
            "Question": questions,
            "Response": ["Yes", 0.0, 0.0, pd.NA, 0.0, pd.NA, pd.NA],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__funding_data(
    mock_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._funding_data(
        df_dict=mock_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    funding_source_types = [
        "How much of your forecast is contractually committed?",
        "How much of your forecast is not contractually committed?",
        "Freedom and flexibilities spend",
        "Total DLUHC spend (inc. F&F)",
        "Secured match funding spend",
        "Unsecured match funding",
        "Total match",
    ]
    reporting_periods = [
        f"Financial year {year} to {year + 1}, ({quarter}), {'Actual' if year < 2024 else 'Forecast'}"
        for year in range(2024, 2026)
        for quarter in ["Apr to Jun", "Jul to Sep", "Oct to Dec", "Jan to Mar"]
    ]
    reporting_periods.append("April 2026 and after, Total")
    start_date = "2024-04-01"
    end_date = "2026-04-01"
    start_dates = list(pd.date_range(start=start_date, end=end_date, freq="QS"))
    end_dates = [(start_dates[i + 1] - pd.Timedelta(days=1)) for i in range(len(start_dates) - 1)]
    end_dates.append(pd.NaT)
    expected_df = pd.DataFrame(
        {
            "Programme ID": ["PF-BOL"] * len(funding_source_types) * len(reporting_periods),
            "Funding Source Type": funding_source_types * len(reporting_periods),
            "Start_Date": [date for date in start_dates for _ in range(7)],
            "End_Date": [date for date in end_dates for _ in range(7)],
            "Spend for Reporting Period": ([1.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0] * (len(reporting_periods) - 1))
            + [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
            "Actual/Forecast": (["Actual"] * len(funding_source_types))
            + (["Forecast"] * len(funding_source_types) * (len(reporting_periods) - 1)),
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__outputs(
    mock_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df_dict = pf._outputs(
        df_dict=mock_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    start_date = "2024-04-01"
    end_date = "2026-04-01"
    start_dates = list(pd.date_range(start=start_date, end=end_date, freq="QS"))
    end_dates = [(start_dates[i + 1] - pd.Timedelta(days=1)) for i in range(len(start_dates) - 1)]
    end_dates.append(pd.NaT)
    expected_df_dict = {
        "Outputs_Ref": pd.DataFrame(
            {
                "Output Name": ["Total length of new pedestrian paths", "Potential entrepreneurs assisted"],
                "Output Category": [
                    "Enhancing sub-regional and regional connectivity",
                    "Strengthening the visitor and local service economy",
                ],
            }
        ),
        "Output_Data": pd.DataFrame(
            {
                "Programme ID": ["PF-BOL"] * len(start_dates) * 2,
                "Output": (["Total length of new pedestrian paths"] * len(start_dates))
                + (["Potential entrepreneurs assisted"] * len(start_dates)),
                "Start_Date": start_dates * 2,
                "End_Date": end_dates * 2,
                "Unit of Measurement": (["km"] * len(start_dates)) + (["n of"] * len(start_dates)),
                "Actual/Forecast": (["Actual"] + (["Forecast"] * (len(start_dates) - 1))) * 2,
                "Amount": ([1.0] * len(start_dates)) + ([5.0] * len(start_dates)),
            }
        ),
    }
    assert_frame_equal(transformed_df_dict["Outputs_Ref"], expected_df_dict["Outputs_Ref"])
    assert_frame_equal(transformed_df_dict["Output_Data"], expected_df_dict["Output_Data"])


def test__outcomes(
    mock_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df_dict = pf._outcomes(
        df_dict=mock_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    start_date = "2024-04-01"
    end_date = "2026-04-01"
    start_dates = list(pd.date_range(start=start_date, end=end_date, freq="QS"))
    end_dates = [(start_dates[i + 1] - pd.Timedelta(days=1)) for i in range(len(start_dates) - 1)]
    end_dates.append(pd.NaT)
    expected_df_dict = {
        "Outcome_Ref": pd.DataFrame(
            {
                "Outcome Name": ["Vehicle flow"],
                "Outcome Category": ["Unlocking and enabling industrial, commercial, and residential development"],
            }
        ),
        "Outcome_Data": pd.DataFrame(
            {
                "Programme ID": ["PF-BOL"] * len(start_dates),
                "Outcome": ["Vehicle flow"] * len(start_dates),
                "Start_Date": start_dates,
                "End_Date": end_dates,
                "UnitofMeasurement": ["km"] * len(start_dates),
                "Amount": [1.0] * len(start_dates),
                "Actual/Forecast": ["Actual"] + (["Forecast"] * (len(start_dates) - 1)),
            }
        ),
    }
    assert_frame_equal(transformed_df_dict["Outcome_Ref"], expected_df_dict["Outcome_Ref"])
    assert_frame_equal(transformed_df_dict["Outcome_Data"], expected_df_dict["Outcome_Data"])


def test__risk_register(
    mock_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._risk_register(
        df_dict=mock_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Programme ID": ["PF-BOL"],
            "RiskName": ["A risk"],
            "RiskCategory": ["Strategy risks"],
            "Short Description": ["a description"],
            "Pre-mitigatedImpact": ["1 - very low"],
            "Pre-mitigatedLikelihood": ["3 - medium"],
            "Mitigatons": ["some mitigations"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__project_finance_changes(
    mock_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._project_finance_changes(
        df_dict=mock_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Programme ID": ["PF-BOL"],
            "Change Number": [1],
            "Project Funding Moved From": ["Wellsprings Innovation Hub"],
            "Intervention Theme Moved From": ["Enhancing sub-regional and regional connectivity"],
            "Project Funding Moved To": ["Wellsprings Innovation Hub"],
            "Intervention Theme Moved To": ["Strengthening the visitor and local service economy"],
            "Amount Moved": [100.32],
            "Change Made": ["change"],
            "Reason for Change": ["reason"],
            "Actual or Forecast": ["Actual"],
            "Reporting Period Change Takes Place": ["Q1 Apr - Jun 23/24"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)
