import pandas as pd
import pytest

from core.const import TF_ROUND_4_TEMPLATE_VERSION
from core.validation.exceptions import UnimplementedErrorMessageException
from core.validation.failures import (
    InvalidEnumValueFailure,
    InvalidOutcomeProjectFailure,
    NonNullableConstraintFailure,
    NonUniqueCompositeKeyFailure,
    SignOffFailure,
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
        row_indexes=[1],
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    ).to_message()
    InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Project Delivery Status",
        row_indexes=[2],
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    ).to_message()
    InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Delivery (RAG)",
        row_indexes=[2],
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    ).to_message()
    InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Spend (RAG)",
        row_indexes=[2],
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    ).to_message()
    InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Risk (RAG)",
        row_indexes=[2],
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    ).to_message()
    InvalidEnumValueFailure(
        sheet="Funding",
        column="Secured",
        row_indexes=[50],
        row_values=("TD-ABC-1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    ).to_message()
    InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="Pre-mitigatedImpact",
        row_indexes=[23],
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    ).to_message()
    InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="Pre-mitigatedLikelihood",
        row_indexes=[24],
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    ).to_message()
    InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="PostMitigatedImpact",
        row_indexes=[25],
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    ).to_message()
    InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="PostMitigatedLikelihood",
        row_indexes=[23],
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    ).to_message()
    InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="Proximity",
        row_indexes=[24],
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    ).to_message()
    InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Project Adjustment Request Status",
        row_indexes=[2],
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    ).to_message()
    InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Current Project Delivery Stage",
        row_indexes=[2],
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    ).to_message()
    InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Leading Factor of Delay",
        row_indexes=[2],
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    ).to_message()
    InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="RiskCategory",
        row_indexes=[25],
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    ).to_message()


def test_non_nullable_messages_project_details():
    failed_rows = pd.Series({"Start_Date": pd.to_datetime("2023-05-01 12:00:00")}, name=22)
    NonNullableConstraintFailure(
        sheet="Project Details", column="Locations", row_indexes=[15, 16], failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Project Details", column="Lat/Long", row_indexes=[21, 22], failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress", column="Start Date", row_indexes=[1, 2], failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress", column="Completion Date", row_indexes=[4], failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress", column="Commentary on Status and RAG Ratings", row_indexes=[2], failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress",
        column="Most Important Upcoming Comms Milestone",
        row_indexes=[7],
        failed_row=None,
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress",
        column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
        row_indexes=[6],
        failed_row=None,
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Programme Progress", column="Answer", row_indexes=[4], failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress", column="Current Project Delivery Stage", row_indexes=[3], failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Outcome_Data",
        column="UnitofMeasurement",
        row_indexes=[16, 21],
        failed_row=failed_rows,
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Outcome_Data",
        column="Amount",
        row_indexes=[5],
        failed_row=failed_rows,
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Outcome_Data",
        column="GeographyIndicator",
        row_indexes=[5, 6],
        failed_row=failed_rows,
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Output_Data", column="Unit of Measurement", row_indexes=[17, 22], failed_row=None
    ).to_message()
    NonNullableConstraintFailure(sheet="Output_Data", column="Amount", row_indexes=[6], failed_row=None).to_message()
    NonNullableConstraintFailure(
        sheet="RiskRegister", column="Short Description", row_indexes=[20], failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="RiskRegister", column="Full Description", row_indexes=[21], failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="RiskRegister", column="Consequences", row_indexes=[22], failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="RiskRegister", column="Mitigatons", row_indexes=[23], failed_row=None
    ).to_message()  # typo throughout code
    NonNullableConstraintFailure(
        sheet="RiskRegister", column="RiskOwnerRole", row_indexes=[24], failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="RiskRegister", column="RiskName", row_indexes=[25], failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="RiskRegister", column="RiskCategory", row_indexes=[26], failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Funding", column="Spend for Reporting Period", row_indexes=[7], failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress", column="Start Date", row_indexes=[2, 3], failed_row=None
    ).to_message()
    NonNullableConstraintFailure(
        sheet="RiskRegister", column="Short Description", row_indexes=[5, 6], failed_row=None
    ).to_message()


def test_wrong_type_messages():
    failed_rows = pd.Series({"Start_Date": pd.to_datetime("2023-05-01 12:00:00")}, name=22)
    WrongTypeFailure(
        sheet="Project Progress",
        column="Start Date",
        expected_type="datetime64[ns]",
        actual_type="string",
        row_indexes=[22],
        failed_row=None,
    ).to_message()
    WrongTypeFailure(
        sheet="Project Progress",
        column="Completion Date",
        expected_type="datetime64[ns]",
        actual_type="string",
        row_indexes=[22],
        failed_row=None,
    ).to_message()
    WrongTypeFailure(
        sheet="Project Progress",
        column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
        expected_type="datetime64[ns]",
        actual_type="string",
        row_indexes=[22],
        failed_row=None,
    ).to_message()
    WrongTypeFailure(
        sheet="Private Investments",
        column="Private Sector Funding Required",
        expected_type="float64",
        actual_type="string",
        row_indexes=[22],
        failed_row=None,
    ).to_message()
    WrongTypeFailure(
        sheet="Private Investments",
        column="Private Sector Funding Secured",
        expected_type="float64",
        actual_type="string",
        row_indexes=[22],
        failed_row=None,
    ).to_message()
    WrongTypeFailure(
        sheet="Funding",
        column="Spend for Reporting Period",
        expected_type="float64",
        actual_type="string",
        row_indexes=[22],
        failed_row=None,
    ).to_message()
    WrongTypeFailure(
        sheet="Output_Data",
        column="Amount",
        expected_type="float64",
        actual_type="string",
        row_indexes=[22],
        failed_row=None,
    ).to_message()
    WrongTypeFailure(
        sheet="Outcome_Data",
        column="Amount",
        expected_type="float64",
        actual_type="string",
        row_indexes=[22],
        failed_row=failed_rows,
    ).to_message()
    WrongTypeFailure(
        sheet="Outcome_Data",
        column="Amount",
        expected_type="float64",
        actual_type="object",
        row_indexes=[22],
        failed_row=failed_rows,
    ).to_message()


def test_enum_failure_with_footfall_geography_indicator_wrong():
    failure = InvalidEnumValueFailure(
        sheet="Outcome_Data",
        column="GeographyIndicator",
        row_indexes=[60],
        row_values=("Value 1", "Value 2", "Value 3", "Value 4", "Year-on-year % change in monthly footfall"),
        value="Value",
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
        cols=("Project ID", "Funding Source Name", "Funding Source Type", "Secured", "Start_Date", "End_Date"),
        row=[
            "HS-GRA-02",
            "Norfolk County Council",
            "Local Authority",
            "Yes",
            "2021-04-01 00:00:00",
            "2021-09-30 00:00:00",
        ],
        row_indexes=[78],
    ).to_message()
    NonUniqueCompositeKeyFailure(
        sheet="Output_Data",
        cols=("Project ID", "Output", "Start_Date", "End_Date", "Unit of Measurement", "Actual/Forecast"),
        row=[
            "HS-GRA-02",
            "Total length of new cycle ways",
            "2020-04-01 00:00:00",
            "2020-09-30 00:00:00",
            "Km of cycle way",
            "Actual",
        ],
        row_indexes=[82],
    ).to_message()
    NonUniqueCompositeKeyFailure(
        sheet="Outcome_Data",
        cols=("Project ID", "Outcome", "Start_Date", "End_Date", "GeographyIndicator"),
        row=[
            "HS-GRA-03",
            "Road traffic flows in corridors of interest (for road schemes)",
            "2020-04-01 00:00:00",
            "Travel corridor",
        ],
        row_indexes=[1],
    ).to_message()
    NonUniqueCompositeKeyFailure(
        sheet="RiskRegister",
        cols=("Programme ID", "Project ID", "RiskName"),
        row=["HS-GRA", pd.NA, "Delivery Timeframe"],
        row_indexes=[1],
    ).to_message()
    NonUniqueCompositeKeyFailure(
        sheet="RiskRegister",
        cols=("Programme ID", "Project ID", "RiskName"),
        row=[pd.NA, "HS-GRA-01", "Project Delivery"],
        row_indexes=[23],
    ).to_message()

    with pytest.raises(UnimplementedErrorMessageException):
        NonUniqueCompositeKeyFailure(
            sheet="Project Progress",
            cols=("Programme ID", "Project ID", "RiskName"),
            row=[pd.NA, "HS-GRA-01", "Project Delivery"],
            row_indexes=[7],
        ).to_message()


def test_invalid_project_outcome_failure():
    InvalidOutcomeProjectFailure(
        invalid_project="Invalid Project", section="Outcome Indicators (excluding footfall)", row_indexes=[5]
    ).to_message()
    InvalidOutcomeProjectFailure(
        invalid_project="Invalid Project", section="Footfall Indicator", row_indexes=[65]
    ).to_message()


def test_authorised_submission():
    UnauthorisedSubmissionFailure(unauthorised_place_name="Newark", authorised_place_names=("Wigan",)).to_message()


def test_sign_off_failure():
    SignOffFailure(
        tab="Review & Sign-Off",
        section="Section 151 Officer / Chief Finance Officer",
        missing_value="Name",
        sign_off_officer="an S151 Officer or Chief Finance Officer",
        cell="C9",
    ).to_message()
    SignOffFailure(
        tab="Review & Sign-Off",
        section="Town Board Chair",
        missing_value="Date",
        sign_off_officer="a programme SRO",
        cell="C15",
    ).to_message()


def test_failures_to_messages():
    failure1 = InvalidEnumValueFailure(
        sheet="Project Details",
        column="Single or Multiple Locations",
        row_indexes=[1],
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    )
    failure2 = NonNullableConstraintFailure(
        sheet="Project Details", column="Lat/Long", row_indexes=[1], failed_row=None
    )
    failure3 = WrongTypeFailure(
        sheet="Project Progress",
        column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
        expected_type="datetime64[ns]",
        actual_type="string",
        row_indexes=[22],
        failed_row=None,
    )
    failure4 = NonUniqueCompositeKeyFailure(
        sheet="RiskRegister",
        cols=("Project ID", "RiskName"),
        row=[pd.NA, "HS-GRA-01", "Project Delivery"],
        row_indexes=[23],
    )
    failure5 = NonUniqueCompositeKeyFailure(
        sheet="RiskRegister",
        cols=("Project ID", "RiskName"),
        row=[pd.NA, "HS-GRA-01", "Project Delivery"],
        row_indexes=[25],
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


def test_construct_cell_index_single():
    # single index
    test_index1 = construct_cell_index("Place Details", "Question", [1])
    assert test_index1 == "C1"

    test_index2 = construct_cell_index("Project Details", "Locations", [2])
    assert test_index2 == "H2 or K2"

    test_index3 = construct_cell_index("Programme Progress", "Answer", [3])
    assert test_index3 == "D3"

    test_index4 = construct_cell_index("Project Progress", "Delivery (RAG)", [4])
    assert test_index4 == "J4"

    test_index5 = construct_cell_index("Funding Questions", "All Columns", [5])
    assert test_index5 == "E5"

    test_index6 = construct_cell_index("Funding Comments", "Comment", [6])
    assert test_index6 == "C6 to E6"

    test_index7 = construct_cell_index("Project Details", "Primary Intervention Theme", [27])
    assert test_index7 == "F27"


def test_construct_cell_index_multiple():
    # multi-index
    test_index1 = construct_cell_index("Funding", "Funding Source Type", [7, 8])
    assert test_index1 == "D7, D8"

    test_index2 = construct_cell_index("Private Investments", "Private Sector Funding Required", [9, 10])
    assert test_index2 == "G9, G10"

    test_index3 = construct_cell_index("Output_Data", "Amount", [11, 12, 13])
    assert test_index3 == "E11 to W11, E12 to W12, E13 to W13"


def test_construct_cell_index_remove_duplicates():
    # should remove duplicates but retain order of row indexes - results in the same as test_index9
    test_index1 = construct_cell_index("Output_Data", "Amount", [11, 11, 11, 12, 12, 13])
    assert test_index1 == "E11 to W11, E12 to W12, E13 to W13"

    test_index2 = construct_cell_index("Outcome_Data", "Higher Frequency", [8, 2, 11, 5, 9])
    assert test_index2 == "P8, P2, P11, P5, P9"


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
        row_indexes=[60],
        failed_row=failed_rows1,
    )
    failure2 = WrongTypeFailure(
        sheet="Outcome_Data",
        column="Amount",
        expected_type="float64",
        actual_type="string",
        row_indexes=[23],
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
            row_indexes=[22],
            failed_row=failed_row1,
        ),
        NonNullableConstraintFailure(
            sheet="Outcome_Data",
            column="Outcome",
            row_indexes=[22],
            failed_row=failed_row1,
        ),
        NonNullableConstraintFailure(
            sheet="Outcome_Data",
            column="Outcome",
            row_indexes=[23],
            failed_row=failed_row1,
        ),
        NonNullableConstraintFailure(
            sheet="Outcome_Data",
            column="Amount",
            row_indexes=[60],
            failed_row=failed_row1,
        ),
        NonNullableConstraintFailure(
            sheet="Outcome_Data",
            column="Amount",
            row_indexes=[60],
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
