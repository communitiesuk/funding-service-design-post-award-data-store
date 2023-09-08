import os

import pandas as pd
import pytest
from openpyxl import Workbook
from openpyxl.drawing.image import Image

from core.validation.specific_validations.towns_fund_round_four import (
    TownsFundRoundFourValidationFailure,
    validate,
    validate_programme_risks,
    validate_project_admin_gis_provided,
    validate_project_risks,
    validate_sign_off,
)


@pytest.fixture
def excel_file_success(tmp_path):
    excel_file = tmp_path / "fake_excel.xlsx"

    wb = Workbook()
    sheet = wb.active
    sheet.title = "8 - Review & Sign-Off"

    current_dir = os.getcwd()
    image_path = os.path.join(current_dir, "tests/validation_tests/resources", "fake_signature.png")
    img1 = Image(image_path)
    img2 = Image(image_path)
    sheet.add_image(img1, "C10")
    sheet.add_image(img2, "C17")
    sheet["B8"] = "Field"
    sheet["C8"] = "Value"
    sheet["B9"] = "Field"
    sheet["C9"] = "Value"
    sheet["B11"] = "Field"
    sheet["C11"] = "Value"
    sheet["B15"] = "Field"
    sheet["C15"] = "Value"
    sheet["B16"] = "Field"
    sheet["C16"] = "Value"
    sheet["B18"] = "Field"
    sheet["C18"] = "Value"

    wb.save(excel_file)

    return excel_file


@pytest.fixture
def excel_file_failure(tmp_path):
    excel_file_failure = tmp_path / "fake_excel_failure.xlsx"

    wb_failure = Workbook()
    sheet = wb_failure.active
    sheet.title = "8 - Review & Sign-Off"

    current_dir = os.getcwd()
    image_path = os.path.join(current_dir, "tests/validation_tests/resources", "fake_signature.png")
    img1 = Image(image_path)
    sheet.add_image(img1, "C10")
    sheet["C17"] = None
    sheet["B8"] = "Name"
    sheet["C8"] = None
    sheet["B9"] = "Field"
    sheet["C9"] = "Value"
    sheet["B11"] = "Field"
    sheet["C11"] = "Value"
    sheet["B15"] = "Field"
    sheet["C15"] = "FValue"
    sheet["B16"] = "Field"
    sheet["C16"] = "Value"
    sheet["B18"] = "Field"
    sheet["C18"] = "Value"

    wb_failure.save(excel_file_failure)

    return excel_file_failure


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
    mocker.patch(
        "core.validation.specific_validations.towns_fund_round_four.validate_project_admin_gis_provided",
        return_value=None,
    )

    mocker.patch(
        "core.validation.specific_validations.towns_fund_round_four.validate_sign_off",
        return_value=None,
    )

    mock_workbook = {"Sheet 1": pd.DataFrame()}
    failures = validate(mock_workbook, None)
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
    mocker.patch(
        "core.validation.specific_validations.towns_fund_round_four.validate_project_admin_gis_provided",
        return_value=None,
    )

    mocker.patch(
        "core.validation.specific_validations.towns_fund_round_four.validate_sign_off",
        return_value=None,
    )

    mock_workbook = {"Sheet 1": pd.DataFrame()}
    failures = validate(mock_workbook, None)
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


def test_validate_project_admin_gis_provided_returns_correct_failure():
    # contains two projects, one with multiple location and no GIS data (causing a failure), the other is single with
    # no GIS data
    project_details_df = pd.DataFrame(
        data=[
            {"Single or Multiple Locations": "Multiple", "GIS Provided": pd.NA},
            {"Single or Multiple Locations": "Single", "GIS Provided": pd.NA},
        ]
    )
    workbook = {"Project Details": project_details_df}

    failures = validate_project_admin_gis_provided(workbook)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Project Admin",
            section="Project Details",
            message='There are blank cells in column: "Are you providing a GIS map (see guidance) with your '
            'return?". Use the space provided to tell us the relevant information',
        )
    ]


def test_validate_project_admin_gis_provided_returns_no_failure():
    # contains two projects, one with multiple location and GIS data, the other is single with
    # no GIS data
    project_details_df = pd.DataFrame(
        data=[
            {"Single or Multiple Locations": "Multiple", "GIS Provided": "Yes"},
            {"Single or Multiple Locations": "Single", "GIS Provided": pd.NA},
        ]
    )
    workbook = {"Project Details": project_details_df}

    failures = validate_project_admin_gis_provided(workbook)

    assert failures is None


def test_validate_sign_off_failure(excel_file_failure):
    failures = validate_sign_off(excel_file_failure)

    assert failures == [
        TownsFundRoundFourValidationFailure(
            tab="Review & Sign-Off",
            section="Town Board Chair",
            message="You must fill out the Signature for this "
            "section. You need to get sign off from a "
            "programme SRO",
        ),
        TownsFundRoundFourValidationFailure(
            tab="Review & Sign-Off",
            section="Section 151 Officer / " "Chief Finance Officer",
            message="You must fill out the Name for this section. You "
            "need to get sign off from an S151 Officer or "
            "Chief Finance Officer",
        ),
    ]


def test_validate_sign_off_success(excel_file_success):
    failures = validate_sign_off(excel_file_success)

    assert failures is None
