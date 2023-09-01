from core.validation.failures import (
    InvalidEnumValueFailure,
    NoInputFailure,
    NonNullableConstraintFailure,
    WrongInputFailure,
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
        sheet="Project Details",
        column="GIS Provided",
        row=2,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        value="Value",
    )
    failures = [failure1, failure2, failure3]
    output = serialise_user_centered_failures(failures)

    assert output == {
        "TabErrors": {
            "Project Admin": {
                "Project Details": [
                    'For column "Does the project have a single location (e.g. one site) or multiple (e.g. multiple '
                    'sites or across a number of post codes)?", you have entered "Value" which isn\'t correct. You '
                    "must select an option from the list provided",
                    'For column "Are you providing a GIS map (see guidance) with your return?", you have entered '
                    '"Value" '
                    "which isn't correct. You must select an option from the list provided",
                    'For column "Are you providing a GIS map (see guidance) with your return?", you have entered '
                    '"Value" '
                    "which isn't correct. You must select an option from the list provided",
                ]
            }
        }
    }


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


def test_non_nullable_user_centered_failures_outcome_data():
    failure1 = NonNullableConstraintFailure(
        sheet="Outcome_Data",
        column="Unit of Measurement",
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
