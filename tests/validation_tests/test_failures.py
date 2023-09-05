import pytest

from core.errors import UnimplementedUCException
from core.validation.failures import (
    InvalidEnumValueFailure,
    NoInputFailure,
    NonNullableConstraintFailure,
    WrongInputFailure,
    WrongTypeFailure,
    serialise_user_centered_failures,
)


def test_invalid_enum_user_centered_failures():
    failure1 = InvalidEnumValueFailure(
        sheet="Project Details",
        column="Single or Multiple Locations",
        row=1,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    )
    failure2 = InvalidEnumValueFailure(
        sheet="Project Details",
        column="GIS Provided",
        row=2,
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
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
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

    assert failure1.to_user_centered_components() == (
        "Project Admin",
        "Project Details",
        'For column "Does the project have a single location (e.g. one site) or '
        'multiple (e.g. multiple sites or across a number of post codes)?", you have '
        'entered "Value" which isn\'t correct. You must select an option from the '
        "list provided",
    )
    assert failure2.to_user_centered_components() == (
        "Project Admin",
        "Project Details",
        'For column "Are you providing a GIS map (see guidance) with your return?", '
        'you have entered "Value" which isn\'t correct. You must select an option '
        "from the list provided",
    )
    assert failure3.to_user_centered_components() == (
        "Programme Progress",
        "Projects Progress Summary",
        'For column "Project Delivery Status", you have entered "Value" which isn\'t '
        "correct. You must select an option from the list provided",
    )
    assert failure4.to_user_centered_components() == (
        "Programme Progress",
        "Projects Progress Summary",
        'For column "Delivery (RAG)", you have entered "Value" which isn\'t correct. '
        "You must select an option from the list provided",
    )
    assert failure5.to_user_centered_components() == (
        "Programme Progress",
        "Projects Progress Summary",
        'For column "Spend (RAG)", you have entered "Value" which isn\'t correct. You '
        "must select an option from the list provided",
    )
    assert failure6.to_user_centered_components() == (
        "Programme Progress",
        "Projects Progress Summary",
        'For column "Risk (RAG)", you have entered "Value" which isn\'t correct. You '
        "must select an option from the list provided",
    )
    assert failure7.to_user_centered_components() == (
        "Funding Profiles",
        "Project Funding Profiles",
        'For column "Has this funding source been secured?", you have entered "Value" '
        "which isn't correct. You must select an option from the list provided",
    )
    assert failure8.to_user_centered_components() == (
        "Risk Register",
        "Project 1 Risks",
        'For column "Pre-mitigated Impact", you have entered "Value" which isn\'t '
        "correct. You must select an option from the list provided",
    )
    assert failure9.to_user_centered_components() == (
        "Risk Register",
        "Project 1 Risks",
        'For column "Pre-mitigated Likelihood", you have entered "Value" which isn\'t '
        "correct. You must select an option from the list provided",
    )
    assert failure10.to_user_centered_components() == (
        "Risk Register",
        "Project 1 Risks",
        'For column "Post-Mitigated Impact", you have entered "Value" which isn\'t '
        "correct. You must select an option from the list provided",
    )
    assert failure11.to_user_centered_components() == (
        "Risk Register",
        "Project 1 Risks",
        'For column "Post-mitigated Likelihood", you have entered "Value" which '
        "isn't correct. You must select an option from the list provided",
    )
    assert failure12.to_user_centered_components() == (
        "Risk Register",
        "Project 1 Risks",
        'For column "Proximity", you have entered "Value" which isn\'t correct. You '
        "must select an option from the list provided",
    )


def test_non_nullable_user_centered_failures_project_details():
    failure1 = NonNullableConstraintFailure(
        sheet="Project Details",
        column="Locations",
    )
    failure2 = NonNullableConstraintFailure(
        sheet="Project Details",
        column="Lat/Long",
    )

    failures = [failure1, failure2]
    output = serialise_user_centered_failures(failures)
    assert output == {
        "TabErrors": {
            "Project Admin": {
                "Project Details": [
                    'There are blank cells in column: "Project Location(s) - Post Code (e.g. SW1P 4DF)". Use the space '
                    "provided to tell us the relevant information",
                    'There are blank cells in column: "Project Location - Lat/Long Coordinates (3.d.p e.g. 51.496, '
                    '-0.129)". Use the space provided to tell us the relevant information',
                ]
            },
        }
    }


def test_non_nullable_user_centered_failures_project_progress():
    failure1 = NonNullableConstraintFailure(sheet="Project Progress", column="Start Date")
    failure2 = NonNullableConstraintFailure(sheet="Project Progress", column="Completion Date")
    failure3 = NonNullableConstraintFailure(sheet="Project Progress", column="Commentary on Status and RAG Ratings")
    failure4 = NonNullableConstraintFailure(sheet="Project Progress", column="Most Important Upcoming Comms Milestone")
    failure5 = NonNullableConstraintFailure(
        sheet="Project Progress", column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)"
    )

    failures = [failure1, failure2, failure3, failure4, failure5]
    output = serialise_user_centered_failures(failures)

    assert output == {
        "TabErrors": {
            "Programme Progress": {
                "Projects Progress Summary": [
                    'There are blank cells in column: "Start Date - mmm/yy (e.g. Dec-22)". Use the space provided to '
                    "tell us the relevant information",
                    'There are blank cells in column: "Completion Date - mmm/yy (e.g. Dec-22)". Use the space provided '
                    "to tell us the relevant information",
                    'There are blank cells in column: "Commentary on Status and RAG Ratings". Use the space provided '
                    "to tell us the relevant information",
                    'There are blank cells in column: "Most Important Upcoming Comms Milestone". Use the space '
                    "provided to tell us the relevant information",
                    'There are blank cells in column: "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)". '
                    "Use the space provided to tell us the relevant information",
                ]
            }
        }
    }


def test_non_nullable_user_centered_failures_unit_of_measurement():
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

    failures = [failure1, failure2]
    output = serialise_user_centered_failures(failures)

    assert output == {
        "TabErrors": {
            "Outcomes": {
                "Outcome Indicators (excluding footfall) / Footfall Indicator": [
                    "There are blank cells in column: Unit of Measurement. Please ensure you have selected valid "
                    "indicators for all Outcomes on the Outcomes tab, and that the Unit of Measurement is correct for "
                    "this outcome"
                ]
            },
            "Project Outputs": {
                "Project Outputs": [
                    "There are blank cells in column: Unit of Measurement. Please ensure you have selected valid "
                    "indicators for all Outputs on the Project Outputs tab, and that the Unit of Measurement is correct"
                    " for this output"
                ]
            },
        }
    }


def test_non_nullable_user_centered_failures_risk_register():
    failure1 = NonNullableConstraintFailure(sheet="RiskRegister", column="Short Description")
    failure2 = NonNullableConstraintFailure(sheet="RiskRegister", column="Full Description")
    failure3 = NonNullableConstraintFailure(sheet="RiskRegister", column="Consequences")
    failure4 = NonNullableConstraintFailure(sheet="RiskRegister", column="Mitigatons")  # typo throughout code

    failures = [failure1, failure2, failure3, failure4]
    output = serialise_user_centered_failures(failures)

    assert output == {
        "TabErrors": {
            "Risk Register": {
                "Programme / Project Risks": [
                    'There are blank cells in column: "Short description of the Risk". Use the space provided to tell '
                    "us the relevant information",
                    'There are blank cells in column: "Full Description". Use the space provided to tell us the '
                    "relevant information",
                    'There are blank cells in column: "Consequences". Use the space provided to tell us the relevant '
                    "information",
                    'There are blank cells in column: "Mitigations". Use the space provided to tell us the relevant '
                    "information",
                ]
            }
        }
    }


def test_non_nullable_user_centered_failures_multiple_tabs():
    failure1 = NonNullableConstraintFailure(sheet="Project Progress", column="Start Date")
    failure2 = NonNullableConstraintFailure(sheet="RiskRegister", column="Short Description")

    failures = [failure1, failure2]
    output = serialise_user_centered_failures(failures)

    assert output == {
        "TabErrors": {
            "Programme Progress": {
                "Projects Progress Summary": [
                    'There are blank cells in column: "Start Date - mmm/yy (e.g. Dec-22)". Use the space provided to '
                    "tell us the relevant information"
                ]
            },
            "Risk Register": {
                "Programme / Project Risks": [
                    'There are blank cells in column: "Short description of the Risk". Use the space provided to tell'
                    " us the relevant information"
                ]
            },
        }
    }


def test_pretransformation_user_centered_failures():
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
    failure3 = NoInputFailure(
        value_descriptor="Place Name",
    )
    failure4 = WrongInputFailure(
        value_descriptor="Form Version",
        entered_value="wrong version",
        expected_values=set("correct version"),
    )
    failures = [failure1, failure2, failure3, failure4]
    output = serialise_user_centered_failures(failures)

    assert output == {
        "PreTransformationErrors": [
            "The reporting period is incorrect on the Start Here tab in cell B6. Make sure you submit the correct "
            "reporting period for the round commencing 1 April 2023 to 30 September 2023",
            "You must select a fund from the list provided on the Project Admin tab in cell E7. Do not populate the "
            "cell with your own content",
            "You must select a place name from the list provided on the Project Admin tab in cell E8. Do not populate "
            "the cell with your own content",
            "You have submitted the wrong reporting template. Make sure you submit Town Deals and Future High Streets "
            "Fund Reporting Template (v4.0)",
        ]
    }


def test_wrong_type_user_centered_failures():
    failure1 = WrongTypeFailure(
        sheet="Project Progress", column="Start Date", expected_type="datetime64[ns]", actual_type="object"
    )
    failure2 = WrongTypeFailure(
        sheet="Project Progress", column="Completion Date", expected_type="datetime64[ns]", actual_type="object"
    )
    failure3 = WrongTypeFailure(
        sheet="Project Progress",
        column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
        expected_type="datetime64[ns]",
        actual_type="object",
    )
    failure4 = WrongTypeFailure(
        sheet="Private Investments",
        column="Private Sector Funding Required",
        expected_type="float64",
        actual_type="object",
    )
    failure5 = WrongTypeFailure(
        sheet="Private Investments",
        column="Private Sector Funding Secured",
        expected_type="float64",
        actual_type="object",
    )
    failure6 = WrongTypeFailure(
        sheet="Funding", column="Spend for Reporting Period", expected_type="float64", actual_type="object"
    )
    failure7 = WrongTypeFailure(sheet="Output_Data", column="Amount", expected_type="float64", actual_type="object")
    failure8 = WrongTypeFailure(sheet="Outcome_Data", column="Amount", expected_type="float64", actual_type="object")
    failure9 = WrongTypeFailure(
        sheet="Project Details", column="Spend for Reporting Period", expected_type="float64", actual_type="object"
    )
    failures = [
        failure1,
        failure2,
        failure3,
        failure4,
        failure5,
        failure6,
        failure7,
        failure8,
    ]
    output = serialise_user_centered_failures(failures)
    assert output == {
        "TabErrors": {
            "Programme Progress": {
                "Projects Progress Summary": [
                    "For column Start Date - mmm/yy (e.g. Dec-22) you entered text when we expected a date. "
                    "You must enter dates in the correct format, for example, Dec-22, Jun-23",
                    "For column Completion Date - mmm/yy (e.g. Dec-22) you entered text when we expected a date. "
                    "You must enter dates in the correct format, for example, Dec-22, Jun-23",
                    "For column Date of Most Important Upcoming Comms Milestone (e.g. Dec-22) you entered text when "
                    "we expected a date. You must enter dates in the correct format, for example, Dec-22, Jun-23",
                ]
            },
            "PSI": {
                "Private Sector Investment": [
                    "For column Private Sector Funding Required you entered text when we expected a number. "
                    "You must enter the required data in the correct format, for example, £5,588.13 or £238,062.50",
                    "For column Private Sector Funding Secured you entered text when we expected a number. "
                    "You must enter the required data in the correct format, for example, £5,588.13 or £238,062.50",
                ]
            },
            "Funding Profiles": {
                "Project Funding Profiles": [
                    "Between columns Financial Year 2022/21 - Financial Year 2025/26 you entered text when we "
                    "expected a number. You must enter the required data in the correct format, for example, £5,"
                    "588.13 or £238,062.50"
                ]
            },
            "Project Outputs": {
                "Project Outputs": [
                    "Between columns Financial Year 2022/21 - Financial Year 2025/26 you entered text when we "
                    "expected a number. You must enter data using the correct format, for example, 9 rather than 9m2. "
                    "Only use numbers"
                ]
            },
            "Outcomes": {
                "Outcome Indicators (excluding footfall) and Footfall Indicator": [
                    "Between columns Financial Year 2022/21 - Financial Year 2029/30 you entered text when we "
                    "expected a number. You must enter data using the correct format, for example, 9 rather than 9m2. "
                    "Only use numbers"
                ]
            },
        }
    }
    with pytest.raises(UnimplementedUCException):
        serialise_user_centered_failures([failure9])
