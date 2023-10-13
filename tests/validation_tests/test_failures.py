import pandas as pd
import pytest

from core.const import TF_ROUND_4_TEMPLATE_VERSION
from core.util import construct_index
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
    failures_to_messages,
)


def test_test_failures_to_messages():
    failure1 = InvalidEnumValueFailure(
        sheet="Project Details",
        column="Single or Multiple Locations",
        row=1,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    )
    failure2 = NonNullableConstraintFailure(
        sheet="Project Details",
        column="Lat/Long",
    )
    failure3 = WrongTypeFailure(
        sheet="Project Progress",
        column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
        expected_type="datetime64[ns]",
        actual_type="string",
        index=[22],
    )
    failure4 = NonUniqueCompositeKeyFailure(
        sheet="RiskRegister",
        cols=("Programme ID", "Project ID", "RiskName"),
        row=[pd.NA, "HS-GRA-01", "Project Delivery"],
    )
    failure5 = NonUniqueCompositeKeyFailure(
        sheet="RiskRegister",
        cols=("Programme ID", "Project ID", "RiskName"),
        row=[pd.NA, "HS-GRA-01", "Project Delivery"],
    )  # intentional duplicate message, should only show up as a single message in the assertion

    failures = [failure1, failure2, failure3, failure4, failure5]
    output = failures_to_messages(failures)

    assert output == {
        "TabErrors": {
            "Project Admin": {
                "Project Details": [
                    'For column "Does the project have a single location (e.g. one site) or multiple (e.g. multiple '
                    'sites or across a number of post codes)?", you have entered "Value" which isn\'t correct. You '
                    "must select an option from the list provided",
                    'There are blank cells in column: "Project Location - Lat/Long Coordinates (3.d.p e.g. 51.496, '
                    '-0.129)". Use the space provided to tell us the relevant information',
                ]
            },
            "Programme Progress": {
                "Projects Progress Summary": [
                    'For column "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)" you entered text when '
                    "we expected a date. You must enter dates in the correct format, for example, Dec-22, Jun-23",
                ]
            },
            "Risk Register": {
                "Project Risks - Project 1": [
                    'You have entered the risk "Project Delivery" repeatedly. Only enter a risk once per project',
                ],
            },
        }
    }


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
        "PreTransformationErrors": [
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


def test_construct_index():
    # single index
    test_index1 = construct_index("Place Details", "Question", [1])
    assert test_index1 == "C3"

    test_index2 = construct_index("Project Details", "Locations", [2])
    assert test_index2 == "H4/K4"

    test_index3 = construct_index("Programme Progress", "Answer", [3])
    assert test_index3 == "D5"

    test_index4 = construct_index("Project Progress", "Delivery (RAG)", [4])
    assert test_index4 == "J6"

    test_index5 = construct_index("Funding Questions", "Response", [5])
    assert test_index5 == "E7-L7"

    test_index6 = construct_index("Funding Comments", "Comment", [6])
    assert test_index6 == "C8-E8"

    # multi-index
    test_index7 = construct_index("Funding", "Funding Source Type", [7, 8])
    assert test_index7 == "D9, D10"

    test_index8 = construct_index("Private Investments", "Private Sector Funding Required", [9, 10])
    assert test_index8 == "G11, G12"

    test_index9 = construct_index("Output_Data", "Amount", [11, 12, 13])
    assert test_index9 == "E13-W13, E14-W14, E15-W15"

    test_index10 = construct_index("Outcome_Data", "Higher Frequency", [8, 2, 11, 5, 9])
    assert test_index10 == "P10, P4, P13, P7, P11"


def test_invalid_enum_messages():
    failure1 = InvalidEnumValueFailure(
        sheet="Project Details",
        column="Single or Multiple Locations",
        row=1,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    )
    failure3 = InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Project Delivery Status",
        row=2,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    )
    failure4 = InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Delivery (RAG)",
        row=2,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    )
    failure5 = InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Spend (RAG)",
        row=2,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    )
    failure6 = InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Risk (RAG)",
        row=2,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    )
    failure7 = InvalidEnumValueFailure(
        sheet="Funding",
        column="Secured",
        row=2,
        row_values=("TD-ABC-1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    )
    failure8 = InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="Pre-mitigatedImpact",
        row=2,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    )
    failure9 = InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="Pre-mitigatedLikelihood",
        row=2,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    )
    failure10 = InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="PostMitigatedImpact",
        row=2,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    )
    failure11 = InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="PostMitigatedLikelihood",
        row=2,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    )
    failure12 = InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="Proximity",
        row=2,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    )
    failure13 = InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Project Adjustment Request Status",
        row=2,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    )
    failure14 = InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Current Project Delivery Stage",
        row=2,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    )
    failure15 = InvalidEnumValueFailure(
        sheet="Project Progress",
        column="Leading Factor of Delay",
        row=2,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    )
    failure16 = InvalidEnumValueFailure(
        sheet="RiskRegister",
        column="RiskCategory",
        row=2,
        row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        value="Value",
    )

    assert failure1.to_message() == (
        "Project Admin",
        "Project Details",
        'For column "Does the project have a single location (e.g. one site) or '
        'multiple (e.g. multiple sites or across a number of post codes)?", you have '
        'entered "Value" which isn\'t correct. You must select an option from the '
        "list provided",
    )
    assert failure3.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'For column "Project Delivery Status", you have entered "Value" which isn\'t '
        "correct. You must select an option from the list provided",
    )
    assert failure4.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'For column "Delivery (RAG)", you have entered "Value" which isn\'t correct. '
        "You must select an option from the list provided",
    )
    assert failure5.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'For column "Spend (RAG)", you have entered "Value" which isn\'t correct. You '
        "must select an option from the list provided",
    )
    assert failure6.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'For column "Risk (RAG)", you have entered "Value" which isn\'t correct. You '
        "must select an option from the list provided",
    )
    assert failure7.to_message() == (
        "Funding Profiles",
        "Project Funding Profiles - Project 1",
        'For column "Has this funding source been secured?", you have entered "Value" '
        "which isn't correct. You must select an option from the list provided",
    )
    assert failure8.to_message() == (
        "Risk Register",
        "Project Risks - Project 1",
        'For column "Pre-mitigated Impact", you have entered "Value" which isn\'t '
        "correct. You must select an option from the list provided",
    )
    assert failure9.to_message() == (
        "Risk Register",
        "Project Risks - Project 1",
        'For column "Pre-mitigated Likelihood", you have entered "Value" which isn\'t '
        "correct. You must select an option from the list provided",
    )
    assert failure10.to_message() == (
        "Risk Register",
        "Project Risks - Project 1",
        'For column "Post-Mitigated Impact", you have entered "Value" which isn\'t '
        "correct. You must select an option from the list provided",
    )
    assert failure11.to_message() == (
        "Risk Register",
        "Project Risks - Project 1",
        'For column "Post-mitigated Likelihood", you have entered "Value" which '
        "isn't correct. You must select an option from the list provided",
    )
    assert failure12.to_message() == (
        "Risk Register",
        "Project Risks - Project 1",
        'For column "Proximity", you have entered "Value" which isn\'t correct. You '
        "must select an option from the list provided",
    )
    assert failure13.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'For column "Project Adjustment Request Status", you have entered "Value" which isn\'t correct. You '
        "must select an option from the list provided",
    )
    assert failure14.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'For column "Current Project Delivery Stage", you have entered "Value" which isn\'t correct. You '
        "must select an option from the list provided",
    )
    assert failure15.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'For column "Leading Factor of Delay", you have entered "Value" which isn\'t correct. You '
        "must select an option from the list provided",
    )
    assert failure16.to_message() == (
        "Risk Register",
        "Project Risks - Project 1",
        'For column "Risk Category", you have entered "Value" which isn\'t correct. You '
        "must select an option from the list provided",
    )


def test_non_nullable_messages_project_details():
    failure1 = NonNullableConstraintFailure(
        sheet="Project Details",
        column="Locations",
    )
    failure2 = NonNullableConstraintFailure(
        sheet="Project Details",
        column="Lat/Long",
    )

    assert failure1.to_message() == (
        "Project Admin",
        "Project Details",
        'There are blank cells in column: "Project Location(s) - Post Code (e.g. SW1P 4DF)". Use the space '
        "provided to tell us the relevant information",
    )
    assert failure2.to_message() == (
        "Project Admin",
        "Project Details",
        'There are blank cells in column: "Project Location - Lat/Long Coordinates (3.d.p e.g. 51.496, '
        '-0.129)". Use the space provided to tell us the relevant information',
    )


def test_non_nullable_messages_project_progress():
    failure1 = NonNullableConstraintFailure(sheet="Project Progress", column="Start Date")
    failure2 = NonNullableConstraintFailure(sheet="Project Progress", column="Completion Date")
    failure3 = NonNullableConstraintFailure(sheet="Project Progress", column="Commentary on Status and RAG Ratings")
    failure4 = NonNullableConstraintFailure(sheet="Project Progress", column="Most Important Upcoming Comms Milestone")
    failure5 = NonNullableConstraintFailure(
        sheet="Project Progress", column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)"
    )
    failure6 = NonNullableConstraintFailure(sheet="Programme Progress", column="Answer")
    failure7 = NonNullableConstraintFailure(sheet="Project Progress", column="Current Project Delivery Stage")

    assert failure1.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'There are blank cells in column: "Start Date - mmm/yy (e.g. Dec-22)". Use the space provided to '
        "tell us the relevant information",
    )
    assert failure2.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'There are blank cells in column: "Completion Date - mmm/yy (e.g. Dec-22)". Use the space provided '
        "to tell us the relevant information",
    )
    assert failure3.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'There are blank cells in column: "Commentary on Status and RAG Ratings". Use the space provided '
        "to tell us the relevant information",
    )
    assert failure4.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'There are blank cells in column: "Most Important Upcoming Comms Milestone". Use the space '
        "provided to tell us the relevant information",
    )
    assert failure5.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'There are blank cells in column: "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)". '
        "Use the space provided to tell us the relevant information",
    )
    assert failure6.to_message() == (
        "Programme Progress",
        "Programme-Wide Progress Summary",
        "Do not leave this blank. Use the space provided to tell us the relevant information",
    )
    assert failure7.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'There are blank cells in column: "Current Project Delivery Stage". '
        "Use the space provided to tell us the relevant information",
    )


def test_non_nullable_messages_unit_of_measurement():
    """
    Alternative message should be displayed for null values of unit of measurement - this means the user hasn't
    selected an indicator from the dropdown.
    """
    failure1 = NonNullableConstraintFailure(
        sheet="Outcome_Data",
        column="UnitofMeasurement",
    )
    failure2 = NonNullableConstraintFailure(
        sheet="Output_Data",
        column="Unit of Measurement",
    )

    assert failure1.to_message() == (
        "Outcomes",
        "Outcome Indicators (excluding footfall) / Footfall Indicator",
        "There are blank cells in column: Unit of Measurement. Please ensure you have selected valid "
        "indicators for all Outcomes on the Outcomes tab, and that the Unit of Measurement is correct for "
        "this outcome",
    )
    assert failure2.to_message() == (
        "Project Outputs",
        "Project Outputs",
        "There are blank cells in column: Unit of Measurement. Please ensure you have selected valid "
        "indicators for all Outputs on the Project Outputs tab, and that the Unit of Measurement is correct"
        " for this output",
    )


def test_non_nullable_messages_outcomes():
    """
    Validation error should be raise if user leaves geography indicator blank
    """
    failure1 = NonNullableConstraintFailure(
        sheet="Outcome_Data",
        column="GeographyIndicator",
    )
    assert failure1.to_message() == (
        "Outcomes",
        "Outcome Indicators (excluding footfall)",
        'There are blank cells in column: "Geography Indicator". '
        "Use the space provided to tell us the relevant information",
    )


def test_non_nullable_messages_risk_register():
    failure1 = NonNullableConstraintFailure(sheet="RiskRegister", column="Short Description")
    failure2 = NonNullableConstraintFailure(sheet="RiskRegister", column="Full Description")
    failure3 = NonNullableConstraintFailure(sheet="RiskRegister", column="Consequences")
    failure4 = NonNullableConstraintFailure(sheet="RiskRegister", column="Mitigatons")  # typo throughout code
    failure5 = NonNullableConstraintFailure(sheet="RiskRegister", column="RiskOwnerRole")
    failure6 = NonNullableConstraintFailure(sheet="RiskRegister", column="RiskName")
    failure7 = NonNullableConstraintFailure(sheet="RiskRegister", column="RiskCategory")

    assert failure1.to_message() == (
        "Risk Register",
        "Programme / Project Risks",
        'There are blank cells in column: "Short description of the Risk". Use the space provided to tell '
        "us the relevant information",
    )
    assert failure2.to_message() == (
        "Risk Register",
        "Programme / Project Risks",
        'There are blank cells in column: "Full Description". Use the space provided to tell us the '
        "relevant information",
    )
    assert failure3.to_message() == (
        "Risk Register",
        "Programme / Project Risks",
        'There are blank cells in column: "Consequences". Use the space provided to tell us the relevant '
        "information",
    )
    assert failure4.to_message() == (
        "Risk Register",
        "Programme / Project Risks",
        'There are blank cells in column: "Mitigations". Use the space provided to tell us the relevant ' "information",
    )
    assert failure5.to_message() == (
        "Risk Register",
        "Programme / Project Risks",
        'There are blank cells in column: "Risk Owner/Role". Use the space provided to tell us the relevant '
        "information",
    )
    assert failure6.to_message() == (
        "Risk Register",
        "Programme / Project Risks",
        'There are blank cells in column: "Risk Name". Use the space provided to tell us the relevant ' "information",
    )
    assert failure7.to_message() == (
        "Risk Register",
        "Programme / Project Risks",
        'There are blank cells in column: "Risk Category". Use the space provided to tell us the relevant '
        "information",
    )


def test_non_nullable_fill_rows():
    failure1 = NonNullableConstraintFailure(sheet="Outcome_Data", column="Amount")
    failure2 = NonNullableConstraintFailure(sheet="Output_Data", column="Amount")
    failure3 = NonNullableConstraintFailure(sheet="Funding", column="Spend for Reporting Period")

    assert failure1.to_message() == (
        "Outcomes",
        "Outcome Indicators (excluding footfall) / Footfall Indicator",
        "You must enter a figure into all required cells for specified indicators reporting period, "
        "even if it’s zero.For example, £0.00 or 0",
    )
    assert failure2.to_message() == (
        "Project Outputs",
        "Project Outputs",
        "You must enter a figure into all required cells for specified indicators reporting period, "
        "even if it’s zero. For example, £0.00 or 0",
    )
    assert failure3.to_message() == (
        "Funding Profiles",
        "Project Funding Profiles",
        "You must enter a figure into all required cells for spend during reporting period, even if it’s "
        "zero.For example, £0.00 or 0",
    )


def test_non_nullable_messages_multiple_tabs():
    failure1 = NonNullableConstraintFailure(sheet="Project Progress", column="Start Date")
    failure2 = NonNullableConstraintFailure(sheet="RiskRegister", column="Short Description")

    assert failure1.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'There are blank cells in column: "Start Date - mmm/yy (e.g. Dec-22)". Use the space provided to '
        "tell us the relevant information",
    )
    assert failure2.to_message() == (
        "Risk Register",
        "Programme / Project Risks",
        'There are blank cells in column: "Short description of the Risk". Use the space provided to tell'
        " us the relevant information",
    )


def test_pretransformation_messages():
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
        value_descriptor="Place Name",
        entered_value="wrong place",
        expected_values=set("correct place"),
    )
    failure4 = WrongInputFailure(
        value_descriptor="Form Version",
        entered_value="wrong version",
        expected_values=set("correct version"),
    )

    assert failure1.to_message() == (
        None,
        None,
        "The reporting period is incorrect on the Start Here tab in cell B6. Make sure you submit the correct "
        "reporting period for the round commencing 1 April 2023 to 30 September 2023",
    )
    assert failure2.to_message() == (
        None,
        None,
        "You must select a fund from the list provided on the Project Admin tab in cell E7. Do not populate the "
        "cell with your own content",
    )
    assert failure3.to_message() == (
        None,
        None,
        "You must select a place name from the list provided on the Project Admin tab in cell E8. Do not populate "
        "the cell with your own content",
    )
    assert failure4.to_message() == (
        None,
        None,
        "You have submitted the wrong reporting template. Make sure you submit Town Deals and Future High Streets "
        f"Fund Reporting Template ({TF_ROUND_4_TEMPLATE_VERSION})",
    )


def test_wrong_type_messages():
    failure1 = WrongTypeFailure(
        sheet="Project Progress",
        column="Start Date",
        expected_type="datetime64[ns]",
        actual_type="string",
        index=[22],
    )
    failure2 = WrongTypeFailure(
        sheet="Project Progress",
        column="Completion Date",
        expected_type="datetime64[ns]",
        actual_type="string",
        index=[22],
    )
    failure3 = WrongTypeFailure(
        sheet="Project Progress",
        column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
        expected_type="datetime64[ns]",
        actual_type="string",
        index=[22],
    )
    failure4 = WrongTypeFailure(
        sheet="Private Investments",
        column="Private Sector Funding Required",
        expected_type="float64",
        actual_type="string",
        index=[22],
    )
    failure5 = WrongTypeFailure(
        sheet="Private Investments",
        column="Private Sector Funding Secured",
        expected_type="float64",
        actual_type="string",
        index=[22],
    )
    failure6 = WrongTypeFailure(
        sheet="Funding",
        column="Spend for Reporting Period",
        expected_type="float64",
        actual_type="string",
        index=[22],
    )
    failure7 = WrongTypeFailure(
        sheet="Output_Data",
        column="Amount",
        expected_type="float64",
        actual_type="string",
        index=[22],
    )
    failure8 = WrongTypeFailure(
        sheet="Outcome_Data",
        column="Amount",
        expected_type="float64",
        actual_type="string",
        index=[22],
    )
    failure9 = WrongTypeFailure(
        sheet="Project Details",
        column="Spend for Reporting Period",
        expected_type="float64",
        actual_type="string",
        index=[22],
    )
    failure10 = WrongTypeFailure(
        sheet="Outcome_Data",
        column="Amount",
        expected_type="float64",
        actual_type="object",
        index=[22],
    )

    assert failure1.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'For column "Start Date - mmm/yy (e.g. Dec-22)" you entered text when we expected a date. '
        "You must enter dates in the correct format, for example, Dec-22, Jun-23",
    )
    assert failure2.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'For column "Completion Date - mmm/yy (e.g. Dec-22)" you entered text when we expected a date. '
        "You must enter dates in the correct format, for example, Dec-22, Jun-23",
    )
    assert failure3.to_message() == (
        "Programme Progress",
        "Projects Progress Summary",
        'For column "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)" you entered text when '
        "we expected a date. You must enter dates in the correct format, for example, Dec-22, Jun-23",
    )
    assert failure4.to_message() == (
        "PSI",
        "Private Sector Investment",
        'For column "Private Sector Funding Required" you entered text when we expected a number. '
        "You must enter the required data in the correct format, for example, £5,588.13 or £238,062.50",
    )
    assert failure5.to_message() == (
        "PSI",
        "Private Sector Investment",
        'For column "Private Sector Funding Secured" you entered text when we expected a number. '
        "You must enter the required data in the correct format, for example, £5,588.13 or £238,062.50",
    )
    assert failure6.to_message() == (
        "Funding Profiles",
        "Project Funding Profiles",
        'Between columns "Financial Year 2022/21 - Financial Year 2025/26" you entered text when we '
        "expected a number. You must enter the required data in the correct format, for example, £5,"
        "588.13 or £238,062.50",
    )
    assert failure7.to_message() == (
        "Project Outputs",
        "Project Outputs",
        'Between columns "Financial Year 2022/21 - Financial Year 2025/26" you entered text when we '
        "expected a number. You must enter data using the correct format, for example, 9 rather than 9m2. "
        "Only use numbers",
    )
    assert failure8.to_message() == (
        "Outcomes",
        "Outcome Indicators (excluding footfall) and Footfall Indicator",
        'Between columns "Financial Year 2022/21 - Financial Year 2029/30" you entered text when we '
        "expected a number. You must enter data using the correct format, for example, 9 rather than 9m2. "
        "Only use numbers",
    )

    with pytest.raises(UnimplementedErrorMessageException):
        failure9.to_message()

    assert failure10.to_message() == (
        "Outcomes",
        "Outcome Indicators (excluding footfall) and Footfall Indicator",
        'Between columns "Financial Year 2022/21 - Financial Year 2029/30" you entered an unknown datatype when we '
        "expected a number. You must enter data using the correct format, for example, 9 rather than 9m2. "
        "Only use numbers",
    )


def test_non_unique_composite_key_messages():
    failure1 = NonUniqueCompositeKeyFailure(
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
    )
    failure2 = NonUniqueCompositeKeyFailure(
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
    )
    failure3 = NonUniqueCompositeKeyFailure(
        sheet="Outcome_Data",
        cols=("Project ID", "Outcome", "Start_Date", "End_Date", "GeographyIndicator"),
        row=[
            "HS-GRA-03",
            "Road traffic flows in corridors of interest (for road schemes)",
            "2020-04-01 00:00:00",
            "Travel corridor",
        ],
    )
    failure4 = NonUniqueCompositeKeyFailure(
        sheet="RiskRegister",
        cols=("Programme ID", "Project ID", "RiskName"),
        row=["HS-GRA", pd.NA, "Delivery Timeframe"],
    )
    failure5 = NonUniqueCompositeKeyFailure(
        sheet="RiskRegister",
        cols=("Programme ID", "Project ID", "RiskName"),
        row=[pd.NA, "HS-GRA-01", "Project Delivery"],
    )
    failure6 = NonUniqueCompositeKeyFailure(
        sheet="Project Progress",
        cols=("Programme ID", "Project ID", "RiskName"),
        row=[pd.NA, "HS-GRA-01", "Project Delivery"],
    )

    assert failure1.to_message() == (
        "Funding Profiles",
        "Funding Profiles - Project 2",
        "You have repeated funding information. You must use a new row for each project, funding source "
        'name, funding type and if its been secured. You have repeat entries for "Norfolk County Council, '
        'Local Authority, Yes"',
    )
    assert failure2.to_message() == (
        "Project Outputs",
        "Project Outputs - Project 2",
        'You have entered the indicator "Total length of new cycle ways" repeatedly. Only enter an indicator '
        "once per project",
    )
    assert failure3.to_message() == (
        "Outcomes",
        "Outcome Indicators (excluding footfall)",
        'You have entered the indicator "Road traffic flows in corridors of interest (for road schemes)" '
        "repeatedly for the same project and geography indicator. Only enter an indicator once per project",
    )
    assert failure4.to_message() == (
        "Risk Register",
        "Programme Risks",
        'You have entered the risk "Delivery Timeframe" repeatedly. Only enter a risk once per project',
    )
    assert failure5.to_message() == (
        "Risk Register",
        "Project Risks - Project 1",
        'You have entered the risk "Project Delivery" repeatedly. Only enter a risk once per project',
    )

    with pytest.raises(UnimplementedErrorMessageException):
        failure6.to_message()


def test_invalid_project_outcome_failure():
    failure1 = InvalidOutcomeProjectFailure(
        invalid_project="Invalid Project", section="Outcome Indicators (excluding footfall)"
    )
    failure2 = InvalidOutcomeProjectFailure(invalid_project="Invalid Project", section="Footfall Indicator")

    assert failure1.to_message() == (
        "Outcomes",
        "Outcome Indicators (excluding footfall)",
        "You must select a project from the drop-down provided for 'Relevant project(s)'. "
        "Do not populate the cell with your own content",
    )

    assert failure2.to_message() == (
        "Outcomes",
        "Footfall Indicator",
        "You must select a project from the drop-down provided for 'Relevant project(s)'. "
        "Do not populate the cell with your own content",
    )


def test_authorised_submission():
    failure1 = UnauthorisedSubmissionFailure(unauthorised_place_name="Newark", authorised_place_names=("Wigan",))

    assert failure1.to_message() == (
        None,
        None,
        "You are not authorised to submit for Newark. Please ensure you submit for a "
        "place within your local authority. "
        "You can submit for the following places: Wigan",
    )


def test_sign_off_failure():
    failure1 = SignOffFailure(
        tab="Review & Sign-Off",
        section="Section 151 Officer / Chief Finance Officer",
        missing_value="Name",
        sign_off_officer="an S151 Officer or Chief Finance Officer",
    )
    failure2 = SignOffFailure(
        tab="Review & Sign-Off", section="Town Board Chair", missing_value="Date", sign_off_officer="a programme SRO"
    )
    assert failure1.to_message() == (
        None,
        None,
        "In the tab 'Review & Sign-Off' you must fill out the "
        "'Name' for 'Section 151 Officer / Chief Finance Officer'. "
        "You need to get sign off from an S151 Officer or Chief Finance Officer",
    )
    assert failure2.to_message() == (
        None,
        None,
        "In the tab 'Review & Sign-Off' you must fill out the "
        "'Date' for 'Town Board Chair'. "
        "You need to get sign off from a programme SRO",
    )
