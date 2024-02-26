import datetime

import pandas as pd
from pandas._testing import assert_frame_equal

import core.transformation.pathfinders.version_1 as v1


def test_pathfinders_transform(
    mock_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
    mock_project_name_to_id_mapping: dict[str, str],
):
    v1.pathfinders_transform(
        df_dict=mock_df_dict,
        reporting_round=1,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
        project_name_to_id_mapping=mock_project_name_to_id_mapping,
    )


def test__submission_ref():
    transformed_df = v1._submission_ref(reporting_round=1)
    row = transformed_df.iloc[0]
    assert isinstance(row["Submission Date"], pd.Timestamp)
    assert row["Reporting Period Start"] == datetime.datetime(2024, 4, 1)
    assert row["Reporting Period End"] == datetime.datetime(2024, 6, 30)
    assert row["Reporting Round"] == 1


def test__place_details(
    mock_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = v1._place_details(
        df_dict=mock_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Question": [
                "Financial Completion Date",
                "Practical Completion Date",
                "Organisation Name",
                "Contact Name",
                "Contact Email Address",
                "Contact Telephone",
            ],
            "Indicator": [pd.NA] * 6,
            "Answer": [
                pd.Timestamp("2001-01-01 00:00:00"),
                pd.Timestamp("2001-01-01 00:00:00"),
                "Bolton Metropolitan Borough Council",
                "Steve Jobs",
                "testing@test.gov.uk",
                pd.NA,
            ],
            "Programme ID": ["PF-BOL"] * 6,
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__programme_ref(
    mock_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = v1._programme_ref(
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
    transformed_df = v1._organisation_ref(df_dict=mock_df_dict)
    expected_df = pd.DataFrame(
        {
            "Organisation Name": ["Bolton Metropolitan Borough Council"],
            "Geography": [pd.NA],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test__project_details(
    mock_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
    mock_project_name_to_id_mapping: dict[str, str],
):
    transformed_df = v1._project_details(
        df_dict=mock_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
        project_name_to_id_mapping=mock_project_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Project Name": ["Wellsprings Innovation Hub"],
            "Primary Intervention Theme": [pd.NA],
            "Single or Multiple Locations": ["Single"],
            "GIS Provided": [pd.NA],
            "Locations": ["M1 1AG"],
            "Postcodes": ["M1 1AG"],
            "Lat/Long": [pd.NA],
            "Project ID": ["PF-BOL-001"],
            "Programme ID": ["PF-BOL"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)


def test_programme_progress(
    mock_df_dict: dict[str, pd.DataFrame],
    mock_programme_name_to_id_mapping: dict[str, str],
):
    transformed_df = v1._programme_progress(
        df_dict=mock_df_dict,
        programme_name_to_id_mapping=mock_programme_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Programme ID": ["PF-BOL"] * 3,
            "Question": [
                "Portfolio Progress",
                "Big Issues",
                "Significant Milestones",
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
    transformed_df = v1._project_progress(
        df_dict=mock_df_dict,
        project_name_to_id_mapping=mock_project_name_to_id_mapping,
    )
    expected_df = pd.DataFrame(
        {
            "Start Date": [pd.NaT],
            "Completion Date": [pd.NaT],
            "Current Project Delivery Stage": [pd.NA],
            "Project Delivery Status": [pd.NA],
            "Leading Factor of Delay": [pd.NA],
            "Project Adjustment Request Status": [pd.NA],
            "Delivery (RAG)": ["Amber/Green"],
            "Spend (RAG)": ["Amber/Green"],
            "Risk (RAG)": [pd.NA],
            "Commentary on Status and RAG Ratings": ["an explanation"],
            "Most Important Upcoming Comms Milestone": [pd.NA],
            "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": [pd.NA],
            "Project ID": ["PF-BOL-001"],
        }
    )
    assert_frame_equal(transformed_df, expected_df)
