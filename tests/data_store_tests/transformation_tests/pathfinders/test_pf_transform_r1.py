import pandas as pd
from pandas._testing import assert_frame_equal

import data_store.transformation.pathfinders.pf_transform_r1 as pf


def test_transform(mock_pf_r1_df_dict: dict[str, pd.DataFrame]):
    pf.transform(df_dict=mock_pf_r1_df_dict, reporting_round=1)


def test__submission_ref(mock_pf_r1_df_dict: dict[str, pd.DataFrame]):
    transformed_df = pf._submission_ref(df_dict=mock_pf_r1_df_dict)
    row = transformed_df.iloc[0]
    assert isinstance(row["submission_date"], pd.Timestamp)
    assert row["sign_off_name"] == "Graham Bell"
    assert row["sign_off_role"] == "Project Manager"
    assert row["sign_off_date"] == pd.Timestamp("2024-03-05").isoformat()


def test__place_details(
    mock_pf_r1_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._place_details(
        df_dict=mock_pf_r1_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "programme_id": ["PF-BOL"] * 5,
            "question": [
                "Financial completion date",
                "Practical completion date",
                "Organisation name",
                "Contact name",
                "Contact email",
            ],
            "answer": [
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
    mock_pf_r1_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._programme_ref(
        df_dict=mock_pf_r1_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "programme_id": ["PF-BOL"],
            "programme_name": ["Bolton Council"],
            "fund_type_id": ["PF"],
            "organisation": ["Bolton Council"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__organisation_ref(
    mock_pf_r1_df_dict: dict[str, pd.DataFrame],
):
    transformed_df = pf._organisation_ref(df_dict=mock_pf_r1_df_dict)
    expected_df = pd.DataFrame(
        {
            "organisation_name": ["Bolton Council"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__project_details(
    mock_pf_r1_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
    mock_project_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._project_details(
        df_dict=mock_pf_r1_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
        project_name_to_id_mapping=mock_project_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "project_id": ["PF-BOL-001", "PF-BOL-002"],
            "programme_id": ["PF-BOL", "PF-BOL"],
            "project_name": ["PF-BOL-001: Wellsprings Innovation Hub", "PF-BOL-002: Bolton Market Upgrades"],
            "locations": ["BL1 1SE", "BL1 1TJ, BL1 1TQ"],
            "postcodes": [["BL1 1SE"], ["BL1 1TJ", "BL1 1TQ"]],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__programme_progress(
    mock_pf_r1_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._programme_progress(
        df_dict=mock_pf_r1_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "programme_id": ["PF-BOL"] * 3,
            "question": [
                "Portfolio progress",
                "Big issues across portfolio",
                "Upcoming significant milestones",
            ],
            "answer": [
                "word word word word word",
                "some big issues",
                "some milestones",
            ],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__project_progress(
    mock_pf_r1_df_dict: dict[str, pd.DataFrame],
    mock_project_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._project_progress(
        df_dict=mock_pf_r1_df_dict,
        project_name_to_id_mapping=mock_project_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "project_id": ["PF-BOL-001", "PF-BOL-002"],
            "delivery_rag": [1, 3],
            "spend_rag": [2, 1],
            "commentary": ["No comment", "Wouldn't you like to know"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__funding_questions(
    mock_pf_r1_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._funding_questions(
        df_dict=mock_pf_r1_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    questions = [
        "Credible plan",
        "Total underspend",
        "Proposed underspend use",
        "Credible plan summary",
        "Current underspend",
        "Uncommitted funding plan",
        "Summary of changes below change request threshold",
    ]
    expected_df = pd.DataFrame(
        {
            "programme_id": ["PF-BOL"] * len(questions),
            "question": questions,
            "response": ["Yes", 0.0, 0.0, "This is a summary", 0.0, pd.NA, pd.NA],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__funding_data(
    mock_pf_r1_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._funding_data(
        df_dict=mock_pf_r1_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    funding_source_types = [
        "How much of your forecast is contractually committed?",
        "How much of your forecast is not contractually committed?",
        "Freedom and flexibilities spend",
        "Secured match funding spend",
        "Unsecured match funding",
    ]
    reporting_periods = [
        "Financial year 2023 to 2024, (Jan to Mar), Actual",
        "Financial year 2024 to 2025, (Apr to Jun), Forecast",
        "Financial year 2024 to 2025, (Jul to Sep), Forecast",
        "Financial year 2024 to 2025, (Oct to Dec), Forecast",
        "Financial year 2024 to 2025, (Jan to Mar), Forecast",
        "Financial year 2025 to 2026, (Apr to Jun), Forecast",
        "Financial year 2025 to 2026, (Jul to Sep), Forecast",
        "Financial year 2025 to 2026, (Oct to Dec), Forecast",
        "Financial year 2025 to 2026, (Jan to Mar), Forecast",
    ]
    first_start_date = "2024-01-01"
    last_start_date = "2026-01-01"
    start_dates = list(pd.date_range(start=first_start_date, end=last_start_date, freq="QS"))
    end_dates = [
        ((start_dates[i] - pd.Timedelta(days=1)).replace(hour=23, minute=59, second=59))
        for i in range(1, len(start_dates))
    ]
    end_dates.append(pd.Timestamp("2026-03-31 23:59:59"))
    expected_df = pd.DataFrame(
        {
            "programme_id": ["PF-BOL"] * len(funding_source_types) * len(reporting_periods),
            "funding_source": ["Pathfinders"] * len(funding_source_types) * len(reporting_periods),
            "spend_type": funding_source_types * len(reporting_periods),
            "start_date": [date for date in start_dates for _ in range(5)],
            "end_date": [date for date in end_dates for _ in range(5)],
            "spend_for_reporting_period": ([1.0, 0.0, 0.0, 0.0, 0.0] * len(reporting_periods)),
            "state": (["Actual"] * len(funding_source_types))
            + (["Forecast"] * len(funding_source_types) * (len(reporting_periods) - 1)),
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__outputs(
    mock_pf_r1_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    mock_pf_r1_df_dict["Bespoke outputs"] = pd.concat(
        (
            mock_pf_r1_df_dict["Bespoke outputs"],
            pd.DataFrame(
                {
                    "Intervention theme": ["Bespoke"],
                    "Output": ["Amount of Floor Space Ratinalised (Sqm)"],
                    "Unit of measurement": ["sqm"],
                    "Financial year 2023 to 2024, (Jan to Mar), Actual": [5.0],
                    "Financial year 2024 to 2025, (Apr to Jun), Forecast": [5.0],
                    "Financial year 2024 to 2025, (Jul to Sep), Forecast": [5.0],
                    "Financial year 2024 to 2025, (Oct to Dec), Forecast": [5.0],
                    "Financial year 2024 to 2025, (Jan to Mar), Forecast": [5.0],
                    "Financial year 2025 to 2026, (Apr to Jun), Forecast": [5.0],
                    "Financial year 2025 to 2026, (Jul to Sep), Forecast": [5.0],
                    "Financial year 2025 to 2026, (Oct to Dec), Forecast": [5.0],
                    "Financial year 2025 to 2026, (Jan to Mar), Forecast": [5.0],
                    "April 2026 and after, Total": [5.0],
                }
            ),
        )
    )
    transformed_df_dict = pf._outputs(
        df_dict=mock_pf_r1_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    first_start_date = "2024-01-01"
    last_start_date = "2026-04-01"
    start_dates = list(pd.date_range(start=first_start_date, end=last_start_date, freq="QS"))
    end_dates = [
        ((start_dates[i] - pd.Timedelta(days=1)).replace(hour=23, minute=59, second=59))
        for i in range(1, len(start_dates))
    ]
    end_dates.append(pd.NaT)
    expected_df_dict = {
        "Outputs_Ref": pd.DataFrame(
            {
                "output_name": [
                    "Total length of pedestrian paths improved",
                    "Potential entrepreneurs assisted",
                    "Amount of Floor Space Rationalised (Sqm)",
                ],
                "output_category": [
                    "Enhancing subregional and regional connectivity",
                    "Bespoke",
                    "Bespoke",
                ],
            }
        ),
        "Output_Data": pd.DataFrame(
            {
                "programme_id": ["PF-BOL"] * len(start_dates) * 3,
                "output": (["Total length of pedestrian paths improved"] * len(start_dates))
                + (["Potential entrepreneurs assisted", "Amount of Floor Space Rationalised (Sqm)"] * len(start_dates)),
                "start_date": start_dates + [i for p in zip(start_dates, start_dates, strict=False) for i in p],
                "end_date": end_dates + [i for p in zip(end_dates, end_dates, strict=False) for i in p],
                "unit_of_measurement": (["km"] * len(start_dates)) + (["n of", "sqm"] * len(start_dates)),
                "state": (["Actual"] + (["Forecast"] * (len(start_dates) - 1)))
                + (["Actual", "Actual"] + (["Forecast"] * (len(start_dates) * 2 - 2))),
                "amount": ([1.0] * len(start_dates)) + ([5.0] * len(start_dates)) * 2,
            }
        ),
    }
    assert_frame_equal(transformed_df_dict["Outputs_Ref"], expected_df_dict["Outputs_Ref"])
    assert_frame_equal(transformed_df_dict["Output_Data"], expected_df_dict["Output_Data"])


def test__outcomes(
    mock_pf_r1_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df_dict = pf._outcomes(
        df_dict=mock_pf_r1_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    first_start_date = "2024-01-01"
    last_start_date = "2026-04-01"
    start_dates = list(pd.date_range(start=first_start_date, end=last_start_date, freq="QS"))
    end_dates = [
        ((start_dates[i] - pd.Timedelta(days=1)).replace(hour=23, minute=59, second=59))
        for i in range(1, len(start_dates))
    ]
    end_dates.append(pd.NaT)
    expected_df_dict = {
        "Outcome_Ref": pd.DataFrame(
            {
                "outcome_name": ["Vehicle flow"],
                "outcome_category": ["Enhancing subregional and regional connectivity"],
            }
        ),
        "Outcome_Data": pd.DataFrame(
            {
                "programme_id": ["PF-BOL"] * len(start_dates),
                "outcome": ["Vehicle flow"] * len(start_dates),
                "start_date": start_dates,
                "end_date": end_dates,
                "unit_of_measurement": ["n of"] * len(start_dates),
                "amount": [1.0] * len(start_dates),
                "state": ["Actual"] + (["Forecast"] * (len(start_dates) - 1)),
            }
        ),
    }
    assert_frame_equal(transformed_df_dict["Outcome_Ref"], expected_df_dict["Outcome_Ref"])
    assert_frame_equal(transformed_df_dict["Outcome_Data"], expected_df_dict["Outcome_Data"])


def test__risk_register(
    mock_pf_r1_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._risk_register(
        df_dict=mock_pf_r1_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "programme_id": ["PF-BOL"],
            "risk_name": ["A risk"],
            "risk_category": ["Strategy risks"],
            "short_desc": ["a description"],
            "pre_mitigated_impact": ["1 - very low"],
            "pre_mitigated_likelihood": ["3 - medium"],
            "mitigations": ["some mitigations"],
            "post_mitigated_impact": ["1 - very low"],
            "post_mitigated_likelihood": ["1 - very low"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__project_finance_changes(
    mock_pf_r1_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = pf._project_finance_changes(
        df_dict=mock_pf_r1_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "programme_id": ["PF-BOL"],
            "change_number": [1],
            "project_funding_moved_from": ["PF-BOL-001: Wellsprings Innovation Hub"],
            "intervention_theme_moved_from": ["Enhancing subregional and regional connectivity"],
            "project_funding_moved_to": ["PF-BOL-001: Wellsprings Innovation Hub"],
            "intervention_theme_moved_to": ["Strengthening the visitor and local service economy"],
            "amount_moved": [100.32],
            "changes_made": ["change"],
            "reasons_for_change": ["reason"],
            "state": ["Actual"],
            "reporting_period_change_takes_place": ["Q4 2023/24: Jan 2024 - Mar 2024"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)
