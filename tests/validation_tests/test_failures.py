import pandas as pd
import pytest

from core.const import TF_ROUND_4_TEMPLATE_VERSION
from core.validation.exceptions import UnimplementedErrorMessageException
from core.validation.failures import (
    GenericFailure,
    InvalidEnumValueFailure,
    NonNullableConstraintFailure,
    NonUniqueCompositeKeyFailure,
    UnauthorisedSubmissionFailure,
    WrongInputFailure,
    WrongTypeFailure,
    construct_cell_index,
    failures_to_messages,
    group_validation_messages,
    remove_errors_already_caught_by_null_failure,
)


def test_failures_to_messages_pre_transformation_failures():
    failure1 = WrongInputFailure(
        value_descriptor="Reporting Period",
        entered_value="wrong round",
        expected_values=set("correct round"),
    )
    failure2 = WrongInputFailure(
        value_descriptor="Fund Type",
        entered_value="wrong type",
        expected_values=set("wrong type"),
    )
    failure3 = WrongInputFailure(
        value_descriptor="Place Name", entered_value="wrong place", expected_values=set("correct place")
    )
    failure4 = WrongInputFailure(
        value_descriptor="Form Version",
        entered_value="wrong version",
        expected_values=set("correct version"),
    )
    failure5 = WrongInputFailure(
        value_descriptor="Place Name vs Fund Type",
        entered_value="Town_Deal",
        expected_values=set("Future High Street Fund"),
    )
    failures = [failure1, failure2, failure3, failure4, failure5]
    output = failures_to_messages(failures)

    assert output == {
        "pre_transformation_errors": [
            "Cell B6 in the “start here” tab must say “1 April 2023 to 30 September 2023”. Select this option from the "
            "dropdown list provided.",
            "Cell E7 in the “project admin” must contain a fund type from the dropdown list provided. Do not enter "
            "your own content.",
            "Cell E8 in the “project admin” must contain a place name from the dropdown list provided. Do not enter"
            " your own content.",
            f"The selected file must be the Town Deals and Future High Streets Fund Reporting Template"
            f" ({TF_ROUND_4_TEMPLATE_VERSION}).",
            "We do not recognise the combination of fund type and place name in cells E7 and E8 in "
            "“project admin”. Check the data is correct.",
        ]
    }


def test_invalid_enum_messages():
    InvalidEnumValueFailure(
        sheet="Project Details",
        column="Single or Multiple Locations",
        row_index=1,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
    ).to_message()
    InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Project Delivery Status",
        row_index=2,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
    ).to_message()
    InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Delivery (RAG)",
        row_index=2,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
    ).to_message()
    InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Spend (RAG)",
        row_index=2,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
    ).to_message()
    InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Risk (RAG)",
        row_index=2,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
    ).to_message()
    InvalidEnumValueFailure(
        sheet="Funding",
        column="Secured",
        row_index=50,
        row_values=("TD-ABC-1", "Value 2", "Value 3", "Value 4"),
    ).to_message()
    InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="Pre-mitigatedImpact",
        row_index=23,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
    ).to_message()
    InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="Pre-mitigatedLikelihood",
        row_index=24,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
    ).to_message()
    InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="PostMitigatedImpact",
        row_index=25,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
    ).to_message()
    InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="PostMitigatedLikelihood",
        row_index=23,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
    ).to_message()
    InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="Proximity",
        row_index=24,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
    ).to_message()
    InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Project Adjustment Request Status",
        row_index=2,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
    ).to_message()
    InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Current Project Delivery Stage",
        row_index=2,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
    ).to_message()
    InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Leading Factor of Delay",
        row_index=2,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
    ).to_message()
    InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="RiskCategory",
        row_index=25,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
    ).to_message()


def test_non_nullable_messages_project_details():
    failed_rows = pd.Series({"Start_Date": pd.to_datetime("2023-05-01 12:00:00")}, name=22)
    NonNullableConstraintFailure(
        sheet="Project Details", column="Locations", row_index=15, failed_row=None
    ).to_message()
    NonNullableConstraintFailure(sheet="Project Details", column="Lat/Long", row_index=21, failed_row=None).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress", column="Start Date", row_index=1, failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress", column="Completion Date", row_index=4, failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress", column="Commentary on Status and RAG Ratings", row_index=2, failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress", column="Most Important Upcoming Comms Milestone", row_index=7, failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress",
        column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
        row_index=6,
        failed_row=None,
    ).to_message()
    NonNullableConstraintFailure(sheet="Programme Progress", column="Answer", row_index=4, failed_row=None).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress", column="Current Project Delivery Stage", row_index=3, failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Outcome_Data", column="UnitofMeasurement", row_index=16, failed_row=failed_rows
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Outcome_Data", column="Amount", row_index=5, failed_row=failed_rows
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Outcome_Data", column="GeographyIndicator", row_index=5, failed_row=failed_rows
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Output_Data", column="Unit of Measurement", row_index=17, failed_row=None
    ).to_message()
    NonNullableConstraintFailure(sheet="Output_Data", column="Amount", row_index=6, failed_row=None).to_message()
    NonNullableConstraintFailure(
        sheet="RiskRegister", column="Short Description", row_index=20, failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="RiskRegister", column="Full Description", row_index=21, failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="RiskRegister", column="Consequences", row_index=22, failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="RiskRegister", column="Mitigatons", row_index=23, failed_row=None
    ).to_message()  # typo throughout code
    NonNullableConstraintFailure(
        sheet="RiskRegister", column="RiskOwnerRole", row_index=24, failed_row=None
    ).to_message()
    NonNullableConstraintFailure(sheet="RiskRegister", column="RiskName", row_index=25, failed_row=None).to_message()
    NonNullableConstraintFailure(
        sheet="RiskRegister", column="RiskCategory", row_index=26, failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Funding", column="Spend for Reporting Period", row_index=7, failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress", column="Start Date", row_index=2, failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="RiskRegister", column="Short Description", row_index=5, failed_row=None
    ).to_message()


def test_wrong_type_messages():
    failed_rows = pd.Series({"Start_Date": pd.to_datetime("2023-05-01 12:00:00")}, name=22)
    WrongTypeFailure(
        sheet="Project Progress",
        column="Start Date",
        expected_type="datetime64[ns]",
        actual_type="string",
        row_index=22,
        failed_row=None,
    ).to_message()
    WrongTypeFailure(
        sheet="Project Progress",
        column="Completion Date",
        expected_type="datetime64[ns]",
        actual_type="string",
        row_index=22,
        failed_row=None,
    ).to_message()
    WrongTypeFailure(
        sheet="Project Progress",
        column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
        expected_type="datetime64[ns]",
        actual_type="string",
        row_index=22,
        failed_row=None,
    ).to_message()
    WrongTypeFailure(
        sheet="Private Investments",
        column="Private Sector Funding Required",
        expected_type="float64",
        actual_type="string",
        row_index=22,
        failed_row=None,
    ).to_message()
    WrongTypeFailure(
        sheet="Private Investments",
        column="Private Sector Funding Secured",
        expected_type="float64",
        actual_type="string",
        row_index=22,
        failed_row=None,
    ).to_message()
    WrongTypeFailure(
        sheet="Funding",
        column="Spend for Reporting Period",
        expected_type="float64",
        actual_type="string",
        row_index=22,
        failed_row=None,
    ).to_message()
    WrongTypeFailure(
        sheet="Output_Data",
        column="Amount",
        expected_type="float64",
        actual_type="string",
        row_index=22,
        failed_row=None,
    ).to_message()
    WrongTypeFailure(
        sheet="Outcome_Data",
        column="Amount",
        expected_type="float64",
        actual_type="string",
        row_index=22,
        failed_row=failed_rows,
    ).to_message()
    WrongTypeFailure(
        sheet="Outcome_Data",
        column="Amount",
        expected_type="float64",
        actual_type="object",
        row_index=22,
        failed_row=failed_rows,
    ).to_message()


def test_enum_failure_with_footfall_geography_indicator_wrong():
    failure = InvalidEnumValueFailure(
        sheet="Outcome_Data",
        column="GeographyIndicator",
        row_index=60,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4", "Year-on-year % change in monthly footfall"),
    )

    assert failure.to_message() == (
        "Outcomes",
        "Footfall Indicator",
        "C65",
        "You’ve entered your own content, instead of selecting from the dropdown list "
        "provided. Select an option from the dropdown list.",
    )


def test_non_unique_composite_key_messages():
    NonUniqueCompositeKeyFailure(
        sheet="Funding",
        column=["Project ID", "Funding Source Name", "Funding Source Type", "Secured", "Start_Date", "End_Date"],
        row=[
            "HS-GRA-02",
            "Norfolk County Council",
            "Local Authority",
            "Yes",
            "2021-04-01 00:00:00",
            "2021-09-30 00:00:00",
        ],
        row_index=78,
    ).to_message()
    NonUniqueCompositeKeyFailure(
        sheet="Output_Data",
        column=["Project ID", "Output", "Start_Date", "End_Date", "Unit of Measurement", "Actual/Forecast"],
        row=[
            "HS-GRA-02",
            "Total length of new cycle ways",
            "2020-04-01 00:00:00",
            "2020-09-30 00:00:00",
            "Km of cycle way",
            "Actual",
        ],
        row_index=82,
    ).to_message()
    NonUniqueCompositeKeyFailure(
        sheet="Outcome_Data",
        column=["Project ID", "Outcome", "Start_Date", "End_Date", "GeographyIndicator"],
        row=[
            "HS-GRA-03",
            "Road traffic flows in corridors of interest (for road schemes)",
            "2020-04-01 00:00:00",
            "Travel corridor",
        ],
        row_index=1,
    ).to_message()
    NonUniqueCompositeKeyFailure(
        sheet="RiskRegister",
        column=["Programme ID", "Project ID", "RiskName"],
        row=["HS-GRA", pd.NA, "Delivery Timeframe"],
        row_index=1,
    ).to_message()
    NonUniqueCompositeKeyFailure(
        sheet="RiskRegister",
        column=["Programme ID", "Project ID", "RiskName"],
        row=[pd.NA, "HS-GRA-01", "Project Delivery"],
        row_index=23,
    ).to_message()

    with pytest.raises(UnimplementedErrorMessageException):
        NonUniqueCompositeKeyFailure(
            sheet="Project Progress",
            column=["Programme ID", "Project ID", "RiskName"],
            row=[pd.NA, "HS-GRA-01", "Project Delivery"],
            row_index=7,
        ).to_message()


def test_authorised_submission():
    UnauthorisedSubmissionFailure(unauthorised_place_name="Newark", authorised_place_names=("Wigan",)).to_message()


def test_generic_failure():
    GenericFailure(
        sheet="A Sheet",
        section="A Section",
        cell_index="C1",
        message="A message",
    ).to_message()


def test_failures_to_messages():
    failure1 = InvalidEnumValueFailure(
        sheet="Project Details",
        column="Single or Multiple Locations",
        row_index=1,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
    )
    failure2 = NonNullableConstraintFailure(sheet="Project Details", column="Lat/Long", row_index=1, failed_row=None)
    failure3 = WrongTypeFailure(
        sheet="Project Progress",
        column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
        expected_type="datetime64[ns]",
        actual_type="string",
        row_index=22,
        failed_row=None,
    )
    failure4 = NonUniqueCompositeKeyFailure(
        sheet="RiskRegister",
        column=["Project ID", "RiskName"],
        row=[pd.NA, "HS-GRA-01", "Project Delivery"],
        row_index=23,
    )
    failure5 = NonUniqueCompositeKeyFailure(
        sheet="RiskRegister",
        column=["Project ID", "RiskName"],
        row=[pd.NA, "HS-GRA-01", "Project Delivery"],
        row_index=25,
    )  # intentional duplicate message, should only show up as a single message in the assertion

    failures = [failure1, failure2, failure3, failure4, failure5]
    output = failures_to_messages(failures)

    assert "validation_errors" in output
    message = output["validation_errors"][0]
    assert "sheet" in message
    assert "section" in message
    assert "cell_index" in message
    assert "description" in message
    assert len(output["validation_errors"]) == 4  # two messages should combine to make a single message


def test_group_validation_messages():
    data = [
        # A - combine these
        ("Project Admin", "Project Details", "A1", "You left cells blank."),
        ("Project Admin", "Project Details", "A2", "You left cells blank."),
        # B - combine these
        ("Project Admin", "Programme Details", "D4", "You left cells blank."),
        ("Project Admin", "Programme Details", "D4, D5, D7", "You left cells blank."),
        # C - do not combine these due to different sections
        ("Risk Register", "Project Risks - Project 1", "G24", "Select from the dropdown."),
        ("Risk Register", "Project Risks - Project 2", "G43", "Select from the dropdown."),
        # D - do not combine these due to different descriptions
        ("Outcomes", "Programme-level Outcomes", "E5", "You left cells blank."),
        ("Outcomes", "Programme-level Outcomes", "E7", "Select from the dropdown."),
    ]

    grouped = group_validation_messages(data)

    assert grouped == [
        ("Project Admin", "Project Details", "A1, A2", "You left cells blank."),
        ("Project Admin", "Programme Details", "D4, D4, D5, D7", "You left cells blank."),
        ("Risk Register", "Project Risks - Project 1", "G24", "Select from the dropdown."),
        ("Risk Register", "Project Risks - Project 2", "G43", "Select from the dropdown."),
        ("Outcomes", "Programme-level Outcomes", "E5", "You left cells blank."),
        ("Outcomes", "Programme-level Outcomes", "E7", "Select from the dropdown."),
    ]


@pytest.mark.parametrize(
    "index_input, expected",
    [
        (("Place Details", "Question", 1), "C1"),
        (("Project Details", "Locations", 2), "H2 or K2"),
        (("Programme Progress", "Answer", 3), "D3"),
        (("Project Progress", "Delivery (RAG)", 4), "J4"),
        (("Funding Questions", "All Columns", 5), "E5"),
        (("Funding Comments", "Comment", 6), "C6 to E6"),
        (("Project Details", "Primary Intervention Theme", 27), "F27"),
    ],
)
def test_construct_cell_index(index_input, expected):
    assert construct_cell_index(*index_input) == expected


def test_remove_errors_already_caught_by_null_failure():
    errors = [
        ("Tab 1", "Sheet 1", "C7", "The cell is blank but is required."),
        ("Tab 1", "Sheet 1", "C8", "The cell is blank but is required. Enter a value, even if it’s zero."),
        ("Tab 1", "Sheet 1", "C7", "Some other message"),
    ]

    errors = remove_errors_already_caught_by_null_failure(errors)

    assert errors == [
        ("Tab 1", "Sheet 1", "C7", "The cell is blank but is required."),
        ("Tab 1", "Sheet 1", "C8", "The cell is blank but is required. Enter a value, even if it’s zero."),
    ]


def test_remove_errors_already_caught_by_null_failure_complex():
    errors = [
        ("Tab 1", "Sheet 1", "C7, C8, C9", "The cell is blank but is required."),
        ("Tab 1", "Sheet 1", "C7", "Some other message"),
    ]

    errors = remove_errors_already_caught_by_null_failure(errors)

    assert errors == [("Tab 1", "Sheet 1", "C7, C8, C9", "The cell is blank but is required.")]


def test_remove_errors_already_caught_by_null_failure_risks():
    errors = [
        ("Tab 1", "Programme / Project Risks", "C12, C13, C17", "The cell is blank but is required."),
        ("Tab 1", "Programme Risks", "C12", "Some other message"),
        ("Tab 1", "Project Risks - Project 1", "C13", "Some other message"),
        ("Tab 1", "Project Risks - Project 2", "C17", "Some other message"),
        ("Tab 1", "Project Risks - Project 2", "C19", "Some other message"),
    ]

    errors = remove_errors_already_caught_by_null_failure(errors)

    assert errors == [
        ("Tab 1", "Project Risks - Project 2", "C19", "Some other message"),
        ("Tab 1", "Programme / Project Risks", "C12, C13, C17", "The cell is blank but is required."),
    ]


def test_failures_to_message_with_outcomes_column_amount():
    failed_rows1 = pd.Series({"Start_Date": pd.to_datetime("2023-05-01 12:00:00")}, name=60)
    failed_rows2 = pd.Series({"Start_Date": pd.to_datetime("2023-06-01 12:00:00")}, name=23)
    failure1 = NonNullableConstraintFailure(
        sheet="Outcome_Data",
        column="Amount",
        row_index=60,
        failed_row=failed_rows1,
    )
    failure2 = WrongTypeFailure(
        sheet="Outcome_Data",
        column="Amount",
        expected_type="float64",
        actual_type="string",
        row_index=23,
        failed_row=failed_rows2,
    )

    assert failure1.to_message() == (
        "Outcomes",
        "Outcome Indicators (excluding footfall) / Footfall Indicator",
        "E75",
        "The cell is blank but is required. Enter a value, even if it’s zero.",
    )
    assert failure2.to_message() == (
        "Outcomes",
        "Outcome Indicators (excluding footfall) and Footfall Indicator",
        "I23",
        "You entered text instead of a number. Remove any units of measurement and only use numbers, for example, 9.",
    )


def test_failures_to_message_with_duplicated_errors():
    failed_row1 = pd.Series({"Start_Date": pd.to_datetime("2023-05-01 12:00:00")}, name=60)
    failed_row2 = pd.Series({"Start_Date": pd.to_datetime("2023-06-01 12:00:00")}, name=60)
    errors = [
        NonNullableConstraintFailure(
            sheet="Outcome_Data",
            column="Outcome",
            row_index=22,
            failed_row=failed_row1,
        ),
        NonNullableConstraintFailure(
            sheet="Outcome_Data",
            column="Outcome",
            row_index=22,
            failed_row=failed_row1,
        ),
        NonNullableConstraintFailure(
            sheet="Outcome_Data",
            column="Outcome",
            row_index=23,
            failed_row=failed_row1,
        ),
        NonNullableConstraintFailure(
            sheet="Outcome_Data",
            column="Amount",
            row_index=60,
            failed_row=failed_row1,
        ),
        NonNullableConstraintFailure(
            sheet="Outcome_Data",
            column="Amount",
            row_index=60,
            failed_row=failed_row2,
        ),
    ]

    filtered_errors = failures_to_messages(errors)

    assert filtered_errors["validation_errors"] == [
        {
            "sheet": "Outcomes",
            "section": "Outcome Indicators (excluding footfall) / Footfall " "Indicator",
            "cell_index": "B22, B23",
            "description": "The cell is blank but is required.",
        },
        {
            "sheet": "Outcomes",
            "section": "Outcome Indicators (excluding footfall) / Footfall " "Indicator",
            "cell_index": "E75, F75",
            "description": "The cell is blank but is required. Enter a value, " "even if it’s zero.",
        },
    ]
