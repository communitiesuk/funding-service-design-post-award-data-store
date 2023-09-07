import pandas as pd

from core.validation.specific_validations.towns_fund_round_four import (
    TownsFundRoundFourValidationFailure,
    validate,
    validate_programme_risks,
    validate_project_risks,
)


def test_validate_returns_failures(mocker):
    mocked_failure = TownsFundRoundFourValidationFailure(tab="Test Tab", section="Test Section", message="Test Message")
    mocker.patch(
        "core.validation.specific_validations.towns_fund_round_four.validate_project_risks",
        return_value=[mocked_failure],
    )
    mocker.patch(
        "core.validation.specific_validations.towns_fund_round_four.validate_programme_risks",
        return_value=[mocked_failure],
    )

    mock_workbook = {"Sheet 1": pd.DataFrame()}
    failures = validate(mock_workbook)
    assert failures == [mocked_failure, mocked_failure]


def test_validate_returns_empty_list(mocker):
    mocker.patch(
        "core.validation.specific_validations.towns_fund_round_four.validate_project_risks",
        return_value=None,
    )
    mocker.patch(
        "core.validation.specific_validations.towns_fund_round_four.validate_programme_risks",
        return_value=None,
    )

    mock_workbook = {"Sheet 1": pd.DataFrame()}
    failures = validate(mock_workbook)
    assert failures == []


def test_validate_project_risks_returns_correct_failure():
    project_details_df = pd.DataFrame(data=[{"Project ID": "TD-ABC-01"}, {"Project ID": "TD-ABC-02"}])
    # Risk Register is missing a risk for Project 2
    # {"Project ID": pd.NA} simulates a programme level risk
    risk_register_df = pd.DataFrame(data=[{"Project ID": pd.NA}, {"Project ID": "TD-ABC-01"}])
    workbook = {"Project Details": project_details_df, "RiskRegister": risk_register_df}

    failures = validate_project_risks(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Project Risks - Project 2",
            message="You have not entered any risks for this project. You must enter at least 1 risk per project",
        )
    ]


def test_validate_project_risks_returns_correct_failure_no_risks():
    project_details_df = pd.DataFrame(
        data=[{"Project ID": "TD-ABC-01"}, {"Project ID": "TD-ABC-02"}, {"Project ID": "TD-ABC-03"}]
    )
    # Risk Register contains no risks at all
    risk_register_df = pd.DataFrame(columns=["Project ID"])
    workbook = {"Project Details": project_details_df, "RiskRegister": risk_register_df}

    failures = validate_project_risks(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Project Risks - Project 1",
            message="You have not entered any risks for this project. You must enter at least 1 risk per project",
        ),
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Project Risks - Project 2",
            message="You have not entered any risks for this project. You must enter at least 1 risk per project",
        ),
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Project Risks - Project 3",
            message="You have not entered any risks for this project. You must enter at least 1 risk per project",
        ),
    ]


def test_validate_project_risks_returns_no_failure():
    project_details_df = pd.DataFrame(data=[{"Project ID": "TD-ABC-01"}])
    risk_register_df = pd.DataFrame(data=[{"Project ID": "TD-ABC-01"}])
    workbook = {"Project Details": project_details_df, "RiskRegister": risk_register_df}

    failures = validate_project_risks(workbook)

    assert failures is None


def test_validate_programme_risks_returns_correct_failure():
    # simulates risks only containing 2 programme level risks - 3 are required as per the validation
    risk_register_df = pd.DataFrame(
        data=[{"Project ID": pd.NA, "Programme ID": "TD-ABC"}, {"Project ID": pd.NA, "Programme ID": "TD-ABC"}]
    )
    workbook = {"RiskRegister": risk_register_df}

    failures = validate_programme_risks(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Programme Risks",
            message="You have not entered enough programme level risks. You must enter 3 programme level risks",
        )
    ]


def test_validate_programme_risks_returns_correct_failure_no_risks():
    # Risk Register contains no risks at all
    risk_register_df = pd.DataFrame(columns=["Programme ID"])
    workbook = {"RiskRegister": risk_register_df}

    failures = validate_programme_risks(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Risk Register",
            section="Programme Risks",
            message="You have not entered enough programme level risks. You must enter 3 programme level risks",
        )
    ]


def test_validate_programme_risks_returns_no_failure():
    # simulates risks containing 3 programme level risks
    risk_register_df = pd.DataFrame(
        data=[
            {"Project ID": pd.NA, "Programme ID": "TD-ABC"},
            {"Project ID": pd.NA, "Programme ID": "TD-ABC"},
            {"Project ID": pd.NA, "Programme ID": "TD-ABC"},
        ]
    )
    workbook = {"RiskRegister": risk_register_df}

    failures = validate_programme_risks(workbook)

    assert failures is None
