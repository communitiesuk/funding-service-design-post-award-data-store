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
    failures = [failure1, failure2, failure3, failure4]
    output = failures_to_messages(failures)

    assert output == {
        "pre_transformation_errors": [
            "The reporting period is incorrect on the Start Here tab in cell B6. Make sure you submit the correct "
            "reporting period for the round commencing 1 April 2023 to 30 September 2023",
            "You must select a fund from the list provided on the Project Admin tab in cell E7. Do not populate the "
            "cell with your own content",
            "You must select a place name from the list provided on the Project Admin tab in cell E8. Do not populate "
            "the cell with your own content",
            "You have submitted the wrong reporting template. Make sure you submit Town Deals and Future High Streets "
            f"Fund Reporting Template ({TF_ROUND_4_TEMPLATE_VERSION})",
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
    NonNullableConstraintFailure(sheet="Project Details", column="Locations", row_indexes=[15, 16]).to_message()
    NonNullableConstraintFailure(sheet="Project Details", column="Lat/Long", row_indexes=[21, 22]).to_message()
    NonNullableConstraintFailure(sheet="Project Progress", column="Start Date", row_indexes=[1, 2]).to_message()
    NonNullableConstraintFailure(sheet="Project Progress", column="Completion Date", row_indexes=[4]).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress", column="Commentary on Status and RAG Ratings", row_indexes=[2]
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress", column="Most Important Upcoming Comms Milestone", row_indexes=[7]
    ).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress",
        column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
        row_indexes=[6],
    ).to_message()
    NonNullableConstraintFailure(sheet="Programme Progress", column="Answer", row_indexes=[4]).to_message()
    NonNullableConstraintFailure(
        sheet="Project Progress", column="Current Project Delivery Stage", row_indexes=[3]
    ).to_message()
    NonNullableConstraintFailure(sheet="Outcome_Data", column="UnitofMeasurement", row_indexes=[16, 21]).to_message()
    NonNullableConstraintFailure(sheet="Outcome_Data", column="Amount", row_indexes=[5]).to_message()
    NonNullableConstraintFailure(sheet="Outcome_Data", column="GeographyIndicator", row_indexes=[5, 6]).to_message()
    NonNullableConstraintFailure(sheet="Output_Data", column="Unit of Measurement", row_indexes=[17, 22]).to_message()
    NonNullableConstraintFailure(sheet="Output_Data", column="Amount", row_indexes=[6]).to_message()
    NonNullableConstraintFailure(sheet="RiskRegister", column="Short Description", row_indexes=[20]).to_message()
    NonNullableConstraintFailure(sheet="RiskRegister", column="Full Description", row_indexes=[21]).to_message()
    NonNullableConstraintFailure(sheet="RiskRegister", column="Consequences", row_indexes=[22]).to_message()
    NonNullableConstraintFailure(
        sheet="RiskRegister", column="Mitigatons", row_indexes=[23]
    ).to_message()  # typo throughout code
    NonNullableConstraintFailure(sheet="RiskRegister", column="RiskOwnerRole", row_indexes=[24]).to_message()
    NonNullableConstraintFailure(sheet="RiskRegister", column="RiskName", row_indexes=[25]).to_message()
    NonNullableConstraintFailure(sheet="RiskRegister", column="RiskCategory", row_indexes=[26]).to_message()
    NonNullableConstraintFailure(sheet="Funding", column="Spend for Reporting Period", row_indexes=[7]).to_message()
    NonNullableConstraintFailure(sheet="Project Progress", column="Start Date", row_indexes=[2, 3]).to_message()
    NonNullableConstraintFailure(sheet="RiskRegister", column="Short Description", row_indexes=[5, 6]).to_message()


def test_wrong_type_messages():
    WrongTypeFailure(
        sheet="Project Progress",
        column="Start Date",
        expected_type="datetime64[ns]",
        actual_type="string",
        row_indexes=[22],
    ).to_message()
    WrongTypeFailure(
        sheet="Project Progress",
        column="Completion Date",
        expected_type="datetime64[ns]",
        actual_type="string",
        row_indexes=[22],
    ).to_message()
    WrongTypeFailure(
        sheet="Project Progress",
        column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
        expected_type="datetime64[ns]",
        actual_type="string",
        row_indexes=[22],
    ).to_message()
    WrongTypeFailure(
        sheet="Private Investments",
        column="Private Sector Funding Required",
        expected_type="float64",
        actual_type="string",
        row_indexes=[22],
    ).to_message()
    WrongTypeFailure(
        sheet="Private Investments",
        column="Private Sector Funding Secured",
        expected_type="float64",
        actual_type="string",
        row_indexes=[22],
    ).to_message()
    WrongTypeFailure(
        sheet="Funding",
        column="Spend for Reporting Period",
        expected_type="float64",
        actual_type="string",
        row_indexes=[22],
    ).to_message()
    WrongTypeFailure(
        sheet="Output_Data",
        column="Amount",
        expected_type="float64",
        actual_type="string",
        row_indexes=[22],
    ).to_message()
    WrongTypeFailure(
        sheet="Outcome_Data",
        column="Amount",
        expected_type="float64",
        actual_type="string",
        row_indexes=[22],
    ).to_message()
    WrongTypeFailure(
        sheet="Outcome_Data",
        column="Amount",
        expected_type="float64",
        actual_type="object",
        row_indexes=[22],
    ).to_message()


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
        invalid_project="Invalid Project", section="Footfall Indicator", row_indexes=None
    ).to_message()


def test_authorised_submission():
    UnauthorisedSubmissionFailure(unauthorised_place_name="Newark", authorised_place_names=("Wigan",)).to_message()


def test_sign_off_failure():
    SignOffFailure(
        tab="Review & Sign-Off",
        section="Section 151 Officer / Chief Finance Officer",
        missing_value="Name",
        sign_off_officer="an S151 Officer or Chief Finance Officer",
    ).to_message()
    SignOffFailure(
        tab="Review & Sign-Off", section="Town Board Chair", missing_value="Date", sign_off_officer="a programme SRO"
    ).to_message()


def test_failures_to_messages():
    failure1 = InvalidEnumValueFailure(
        sheet="Project Details",
        column="Single or Multiple Locations",
        row_indexes=[1],
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    )
    failure2 = NonNullableConstraintFailure(sheet="Project Details", column="Lat/Long", row_indexes=[1])
    failure3 = WrongTypeFailure(
        sheet="Project Progress",
        column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
        expected_type="datetime64[ns]",
        actual_type="string",
        row_indexes=[22],
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


def test_construct_cell_index():
    # single index
    test_index1 = construct_cell_index("Place Details", "Question", [1])
    assert test_index1 == "C1"

    test_index2 = construct_cell_index("Project Details", "Locations", [2])
    assert test_index2 == "H2/K2"

    test_index3 = construct_cell_index("Programme Progress", "Answer", [3])
    assert test_index3 == "D3"

    test_index4 = construct_cell_index("Project Progress", "Delivery (RAG)", [4])
    assert test_index4 == "J4"

    test_index5 = construct_cell_index("Funding Questions", "Response", [5])
    assert test_index5 == "E5-L5"

    test_index6 = construct_cell_index("Funding Comments", "Comment", [6])
    assert test_index6 == "C6-E6"

    # multi-index
    test_index7 = construct_cell_index("Funding", "Funding Source Type", [7, 8])
    assert test_index7 == "D7, D8"

    test_index8 = construct_cell_index("Private Investments", "Private Sector Funding Required", [9, 10])
    assert test_index8 == "G9, G10"

    test_index9 = construct_cell_index("Output_Data", "Amount", [11, 12, 13])
    assert test_index9 == "E11-W11, E12-W12, E13-W13"

    # should remove duplicates but retain order of row indexes - results in the same as test_index9
    test_index10 = construct_cell_index("Output_Data", "Amount", [11, 11, 11, 12, 12, 13])
    assert test_index10 == "E11-W11, E12-W12, E13-W13"

    test_index11 = construct_cell_index("Outcome_Data", "Higher Frequency", [8, 2, 11, 5, 9])
    assert test_index11 == "P8, P2, P11, P5, P9"
