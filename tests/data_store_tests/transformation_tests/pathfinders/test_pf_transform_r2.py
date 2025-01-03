import pandas as pd
from pandas._testing import assert_frame_equal

import data_store.transformation.pathfinders.pf_transform_r2 as pf


def test_transform(mock_pf_r2_df_dict: dict[str, pd.DataFrame]):
    pf.transform(df_dict=mock_pf_r2_df_dict, reporting_round=1)


def test__submission_ref(mock_pf_r2_df_dict: dict[str, pd.DataFrame]):
    transformed_df = pf._submission_ref(df_dict=mock_pf_r2_df_dict)
    row = transformed_df.iloc[0]
    assert isinstance(row["Submission Date"], pd.Timestamp)
    assert row["Sign Off Name"] == "Graham Bell"
    assert row["Sign Off Role"] == "Project Manager"
    assert row["Sign Off Date"] == pd.Timestamp("2024-03-05").isoformat()


def test__place_details(
    mock_pf_r2_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._place_details(
        df_dict=mock_pf_r2_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Programme ID": ["PF-BOL"] * 6,
            "Question": [
                "Financial completion date",
                "Activity end date",
                "Practical completion date",
                "Organisation name",
                "Contact name",
                "Contact email",
            ],
            "Answer": [
                pd.Timestamp("2001-01-01 00:00:00").isoformat(),
                pd.Timestamp("2001-01-01 00:00:00").isoformat(),
                pd.Timestamp("2001-01-01 00:00:00").isoformat(),
                "Bolton Council",
                "Steve Jobs",
                "testing@test.gov.uk",
            ],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__programme_ref(
    mock_pf_r2_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._programme_ref(
        df_dict=mock_pf_r2_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Programme ID": ["PF-BOL"],
            "Programme Name": ["Bolton Council"],
            "FundType_ID": ["PF"],
            "Organisation": ["Bolton Council"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__organisation_ref(
    mock_pf_r2_df_dict: dict[str, pd.DataFrame],
):
    transformed_df = pf._organisation_ref(df_dict=mock_pf_r2_df_dict)
    expected_df = pd.DataFrame(
        {
            "Organisation": ["Bolton Council"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__project_details(
    mock_pf_r2_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
    mock_project_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._project_details(
        df_dict=mock_pf_r2_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
        project_name_to_id_mapping=mock_project_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Project ID": ["PF-BOL-001", "PF-BOL-002"],
            "Programme ID": ["PF-BOL", "PF-BOL"],
            "Project Name": ["PF-BOL-001: Wellsprings Innovation Hub", "PF-BOL-002: Bolton Market Upgrades"],
            "Locations": ["BL1 1SE", "BL1 1TJ, BL1 1TQ"],
            "Postcodes": [["BL1 1SE"], ["BL1 1TJ", "BL1 1TQ"]],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__programme_progress(
    mock_pf_r2_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._programme_progress(
        df_dict=mock_pf_r2_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Programme ID": ["PF-BOL"] * 5,
            "Question": [
                "Portfolio progress",
                "Ability to spend current spending profile (RAG)",
                "Current portfolio-level delivery progress (RAG)",
                "Big issues across portfolio",
                "Upcoming significant milestones",
            ],
            "Answer": [
                "word word word word word",
                "Green",
                "Amber",
                "some big issues",
                "some milestones",
            ],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__project_progress(
    mock_pf_r2_df_dict: dict[str, pd.DataFrame],
    mock_project_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._project_progress(
        df_dict=mock_pf_r2_df_dict,
        project_name_to_id_mapping=mock_project_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Project ID": ["PF-BOL-001", "PF-BOL-002"],
            "Project Status": ["In progress", "In progress"],
            "Delivery (RAG)": [1, 3],
            "Spend (RAG)": [2, 1],
            "Commentary on Status and RAG Ratings": ["No comment", "Wouldn't you like to know"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__funding_questions(
    mock_pf_r2_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._funding_questions(
        df_dict=mock_pf_r2_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    questions = [
        "Current underspend",
        "Uncommitted funding plan",
        "Summary of changes below change request threshold",
    ]
    expected_df = pd.DataFrame(
        {
            "Programme ID": ["PF-BOL"] * len(questions),
            "Question": questions,
            "Response": [0.0, pd.NA, pd.NA],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__funding_data(
    mock_pf_r2_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._funding_data(
        df_dict=mock_pf_r2_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    funding_source_types = [
        "How much of your forecast is contractually committed (this includes actual expenditure)?",
        "How much of your forecast is not contractually committed?",
        "Freedom and flexibilities spend",
        "Secured match funding spend (this includes actual match funding)",
        "Unsecured match funding",
    ]
    reporting_periods = [
        "Total cumulative actuals to date, (Up to and including Mar 2024), Actual",
        "Financial year 2024 to 2025, (Apr to Jun), Actual",
        "Financial year 2024 to 2025, (Jul to Sep), Actual",
        "Financial year 2024 to 2025, (Oct to Dec), Forecast",
        "Financial year 2024 to 2025, (Jan to Mar), Forecast",
        "Financial year 2025 to 2026, (Apr to Jun), Forecast",
        "Financial year 2025 to 2026, (Jul to Sep), Forecast",
        "Financial year 2025 to 2026, (Oct to Dec), Forecast",
        "Financial year 2025 to 2026, (Jan to Mar), Forecast",
        "Financial year 2026 to 2027, (Apr to Jun), Forecast",
        "Financial year 2026 to 2027, (Jul to Sep), Forecast",
        "Financial year 2026 to 2027, (Oct to Dec), Forecast",
        "Financial year 2026 to 2027, (Jan to Mar), Forecast",
    ]
    first_start_date = "2024-01-01"
    last_start_date = "2027-01-01"
    start_dates = list(pd.date_range(start=first_start_date, end=last_start_date, freq="QS"))

    # The actual start date for "Total cumulative actuals to date, (Up to and including Mar 2024)" is 2019-01-01,
    # as per agreement with PF team.
    start_dates[0] = start_dates[0].replace(year=2019)

    end_dates = [
        ((start_dates[i] - pd.Timedelta(days=1)).replace(hour=23, minute=59, second=59))
        for i in range(1, len(start_dates))
    ]
    end_dates.append(pd.Timestamp("2027-03-31 23:59:59"))
    expected_df = pd.DataFrame(
        {
            "Programme ID": ["PF-BOL"] * len(funding_source_types) * len(reporting_periods) * 2,
            "Funding Source Name": ["Pathfinders"] * len(funding_source_types) * len(reporting_periods) * 2,
            "Funding Category": [
                item
                for _ in reporting_periods
                for item in (["Capital"] * len(funding_source_types) + ["Revenue"] * len(funding_source_types))
            ],
            "Funding Source Type": funding_source_types * len(reporting_periods) * 2,
            "Start_Date": [date for date in start_dates for _ in range(len(funding_source_types) * 2)],
            "End_Date": [date for date in end_dates for _ in range(len(funding_source_types) * 2)],
            "Spend for Reporting Period": ([1.0, 0.0, 0.0, 0.0, 0.0] * len(reporting_periods)) * 2,
            "Actual/Forecast": (["Actual"] * len(funding_source_types) * 3) * 2
            + (["Forecast"] * len(funding_source_types) * (len(reporting_periods) - 3)) * 2,
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__outputs(
    mock_pf_r2_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df_dict = pf._outputs(
        df_dict=mock_pf_r2_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    first_start_date = "2024-01-01"
    last_start_date = "2027-04-01"
    start_dates = list(pd.date_range(start=first_start_date, end=last_start_date, freq="QS"))

    # The actual start date for "Total cumulative actuals to date, (Up to and including Mar 2024)" is 2019-01-01,
    # as per agreement with PF team.
    start_dates[0] = start_dates[0].replace(year=2019)

    end_dates = [
        ((start_dates[i] - pd.Timedelta(days=1)).replace(hour=23, minute=59, second=59))
        for i in range(1, len(start_dates))
    ]
    end_dates.append(pd.NaT)
    expected_df_dict = {
        "Outputs_Ref": pd.DataFrame(
            {
                "Output Name": ["Total length of pedestrian paths improved", "Potential entrepreneurs assisted"],
                "Output Category": [
                    "Enhancing subregional and regional connectivity",
                    "Bespoke",
                ],
            }
        ),
        "Output_Data": pd.DataFrame(
            {
                "Programme ID": ["PF-BOL"] * len(start_dates) * 2,
                "Output": (["Total length of pedestrian paths improved"] * len(start_dates))
                + (["Potential entrepreneurs assisted"] * len(start_dates)),
                "Start_Date": start_dates * 2,
                "End_Date": end_dates * 2,
                "Unit of Measurement": (["km"] * len(start_dates)) + (["n of"] * len(start_dates)),
                "Actual/Forecast": (["Actual"] * 3 + (["Forecast"] * (len(start_dates) - 3))) * 2,
                "Amount": ([1.0] * len(start_dates)) + ([5.0] * len(start_dates)),
            }
        ),
    }
    assert_frame_equal(transformed_df_dict["Outputs_Ref"], expected_df_dict["Outputs_Ref"])
    assert_frame_equal(transformed_df_dict["Output_Data"], expected_df_dict["Output_Data"])


def test__outcomes(
    mock_pf_r2_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df_dict = pf._outcomes(
        df_dict=mock_pf_r2_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    first_start_date = "2024-01-01"
    last_start_date = "2027-04-01"
    start_dates = list(pd.date_range(start=first_start_date, end=last_start_date, freq="QS"))

    # The actual start date for "Total cumulative actuals to date, (Up to and including Mar 2024)" is 2019-01-01,
    # as per agreement with PF team.
    start_dates[0] = start_dates[0].replace(year=2019)

    end_dates = [
        ((start_dates[i] - pd.Timedelta(days=1)).replace(hour=23, minute=59, second=59))
        for i in range(1, len(start_dates))
    ]
    end_dates.append(pd.NaT)
    expected_df_dict = {
        "Outcome_Ref": pd.DataFrame(
            {
                "Outcome_Name": ["Vehicle flow"],
                "Outcome_Category": ["Enhancing subregional and regional connectivity"],
            }
        ),
        "Outcome_Data": pd.DataFrame(
            {
                "Programme ID": ["PF-BOL"] * len(start_dates),
                "Outcome": ["Vehicle flow"] * len(start_dates),
                "Start_Date": start_dates,
                "End_Date": end_dates,
                "UnitofMeasurement": ["n of"] * len(start_dates),
                "Amount": [1.0] * len(start_dates),
                "Actual/Forecast": ["Actual"] * 3 + (["Forecast"] * (len(start_dates) - 3)),
            }
        ),
    }
    assert_frame_equal(transformed_df_dict["Outcome_Ref"], expected_df_dict["Outcome_Ref"])
    assert_frame_equal(transformed_df_dict["Outcome_Data"], expected_df_dict["Outcome_Data"])


def test__risk_register(
    mock_pf_r2_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._risk_register(
        df_dict=mock_pf_r2_df_dict,
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
            "PostMitigatedImpact": ["1 - very low"],
            "PostMitigatedLikelihood": ["1 - very low"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__project_finance_changes(
    mock_pf_r2_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._project_finance_changes(
        df_dict=mock_pf_r2_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Programme ID": ["PF-BOL"],
            "Change Number": [1],
            "Project Funding Moved From": ["PF-BOL-001: Wellsprings Innovation Hub"],
            "Intervention Theme Moved From": ["Enhancing subregional and regional connectivity"],
            "Project Funding Moved To": ["PF-BOL-001: Wellsprings Innovation Hub"],
            "Intervention Theme Moved To": ["Strengthening the visitor and local service economy"],
            "Amount Moved": [100.32],
            "Change Made": ["change"],
            "Reason for Change": ["reason"],
            "Actual or Forecast": ["Actual"],
            "Reporting Period Change Takes Place": ["Q4 2023/24: Jan 2024 - Mar 2024"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)
