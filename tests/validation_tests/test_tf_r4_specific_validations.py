import pandas as pd

from core.validation.specific_validations.towns_fund_round_four import (
    TownsFundRoundFourValidationFailure,
    validate,
    validate_project_risks,
)


def test_validate_returns_failures(mocker):
    mocked_failure = TownsFundRoundFourValidationFailure(tab="Test Tab", section="Test Section", message="Test Message")
    mocker.patch(
        "core.validation.specific_validations.towns_fund_round_four.validate_project_risks",
        return_value=[mocked_failure],
    )

    mock_workbook = {"Sheet 1": pd.DataFrame()}
    failures = validate(mock_workbook)
    assert failures == [mocked_failure]


def test_validate_returns_empty_list(mocker):
    mocker.patch(
        "core.validation.specific_validations.towns_fund_round_four.validate_project_risks",
        return_value=None,
    )

    mock_workbook = {"Sheet 1": pd.DataFrame()}
    failures = validate(mock_workbook)
    assert failures == []


def test_validate_project_risks_returns_correct_failure():
    project_details_df = pd.DataFrame(data=[{"Project ID": "TD-ABC-01"}, {"Project ID": "TD-ABC-02"}])
    # Risk Register is missing a risk for Project 2
    risk_register_df = pd.DataFrame(data=[{"Project ID": "TD-ABC-01"}])
    workbook = {"Project Details": project_details_df, "RiskRegister": risk_register_df}

    failures = validate_project_risks(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Project Risks - Project 2",
            message="You have not entered any risks for this project. You must enter at least 1 risk per project",
        )
    ]


def test_validate_project_risks_returns_no_failure():
    project_details_df = pd.DataFrame(data=[{"Project ID": "TD-ABC-01"}])
    risk_register_df = pd.DataFrame(data=[{"Project ID": "TD-ABC-01"}])
    workbook = {"Project Details": project_details_df, "RiskRegister": risk_register_df}

    failures = validate_project_risks(workbook)

    assert failures is None
