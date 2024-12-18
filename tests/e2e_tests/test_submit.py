import pytest
from playwright.sync_api import Page, expect

from tests.e2e_tests.config import EndToEndTestSecrets
from tests.e2e_tests.helpers import (
    assert_and_download_fund_email_file,
    lookup_confirmation_emails,
    validate_general_validation_errors,
    validate_initial_validation_errors,
    validate_success_files,
)
from tests.e2e_tests.pages.submit import (
    SubmitDashboardPage,
    SubmitUploadPage,
)

pytestmark = pytest.mark.e2e


@pytest.mark.user_roles(["PF_MONITORING_RETURN_SUBMITTER", "TF_MONITORING_RETURN_SUBMITTER"])
def test_pathfinders_submit_report(domains, user_auth, page: Page, e2e_test_secrets: EndToEndTestSecrets):
    PATH_TO_TEST_REPORTS = "tests/integration_tests/mock_pf_returns/"
    INITIAL_VALIDATION_FAILED_FILE = f"{PATH_TO_TEST_REPORTS}PF_Round_2_Initial_Validation_Failures.xlsx"
    GENERAL_VALIDATION_FAILED_FILE = f"{PATH_TO_TEST_REPORTS}PF_Round_2_General_Validation_Failures.xlsx"
    SUCCESS_FILE = f"{PATH_TO_TEST_REPORTS}PF_Round_2_Success.xlsx"
    la_email_subject = "Your Pathfinders data return has been submitted"
    fund_email_subject = "Record of a Pathfinders submission for Pathfinders Bolton Council"

    dashboard_page = SubmitDashboardPage(page, domain=domains.submit)
    dashboard_page.navigate()

    expect(
        page.get_by_role(
            "heading",
            name="Submit monitoring and evaluation data dashboard",
        )
    ).to_be_visible()

    submit_upload_page: SubmitUploadPage = dashboard_page.click_fund("Pathfinders")

    validate_initial_validation_errors(submit_upload_page, INITIAL_VALIDATION_FAILED_FILE)
    validate_general_validation_errors(submit_upload_page, GENERAL_VALIDATION_FAILED_FILE)
    validate_success_files(submit_upload_page, SUCCESS_FILE)

    _, fund_email = lookup_confirmation_emails(
        user_auth.email_address, e2e_test_secrets, la_email_subject, fund_email_subject
    )

    assert_and_download_fund_email_file(fund_email, page)


@pytest.mark.user_roles(["TF_MONITORING_RETURN_SUBMITTER", "TF_MONITORING_RETURN_SUBMITTER"])
def test_towns_fund_submit_report(domains, user_auth, page: Page, e2e_test_secrets: EndToEndTestSecrets):
    PATH_TO_TEST_REPORTS = "tests/integration_tests/mock_tf_returns/"
    INITIAL_VALIDATION_FAILED_FILE = f"{PATH_TO_TEST_REPORTS}TF_Round_6_Project_Initial_Validation_Failures.xlsx"
    GENERAL_VALIDATION_FAILED_FILE = f"{PATH_TO_TEST_REPORTS}TF_Round_6_General_Validation_Failures.xlsx"
    SUCCESS_FILE = f"{PATH_TO_TEST_REPORTS}TF_Round_6_Success.xlsx"
    la_email_subject = "Your Towns Fund data return has been submitted"
    fund_email_subject = "Record of a Towns Fund submission for Town Deal Worcester"

    dashboard_page = SubmitDashboardPage(page, domain=domains.submit)
    dashboard_page.navigate()

    expect(
        page.get_by_role(
            "heading",
            name="Submit monitoring and evaluation data dashboard",
        )
    ).to_be_visible()

    submit_upload_page: SubmitUploadPage = dashboard_page.click_fund("Towns Fund")
    validate_initial_validation_errors(submit_upload_page, INITIAL_VALIDATION_FAILED_FILE)
    validate_general_validation_errors(submit_upload_page, GENERAL_VALIDATION_FAILED_FILE)
    validate_success_files(submit_upload_page, SUCCESS_FILE)

    _, fund_email = lookup_confirmation_emails(
        user_auth.email_address, e2e_test_secrets, la_email_subject, fund_email_subject
    )

    assert_and_download_fund_email_file(fund_email, page)
