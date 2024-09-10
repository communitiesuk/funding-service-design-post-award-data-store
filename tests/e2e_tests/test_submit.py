import pytest
from playwright.sync_api import Page, expect

from tests.e2e_tests.helpers import (
    extract_email_link,
    lookup_confirmation_emails,
)
from tests.e2e_tests.pages.find import DownloadDataPage
from tests.e2e_tests.pages.submit import (
    SubmitDashboardPage,
    SubmitUploadPage,
    SubmitUploadResponsePage,
)

pytestmark = pytest.mark.e2e


@pytest.mark.user_roles(["PF_MONITORING_RETURN_SUBMITTER", "TF_MONITORING_RETURN_SUBMITTER"])
def test_submit_report(domains, user_auth, page: Page):
    PATH_TO_TEST_REPORTS = "tests/integration_tests/mock_pf_returns/"

    dashboard_page = SubmitDashboardPage(page, domain=domains.submit)
    dashboard_page.navigate()

    expect(
        page.get_by_role(
            "heading",
            name="Submit monitoring and evaluation data dashboard",
        )
    ).to_be_visible()

    submit_upload_page: SubmitUploadPage = dashboard_page.click_fund("Pathfinders")

    # test initial validation error upload
    submit_upload_initial_error_page: SubmitUploadResponsePage = submit_upload_page.upload_report(
        f"{PATH_TO_TEST_REPORTS}/PF_Round_1_Initial_Validation_Failures.xlsx"
    )

    expect(submit_upload_initial_error_page.get_title()).to_be_visible()
    expect(submit_upload_initial_error_page.get_subtitle()).to_be_visible()

    # test general validation error upload
    submit_upload_general_error_page: SubmitUploadResponsePage = submit_upload_page.upload_report(
        f"{PATH_TO_TEST_REPORTS}/PF_Round_1_General_Validation_Failures.xlsx"
    )

    expect(submit_upload_general_error_page.get_title()).to_be_visible()
    expect(submit_upload_general_error_page.get_subtitle()).to_be_visible()

    # test successful upload
    submit_upload_success_page: SubmitUploadResponsePage = submit_upload_page.upload_report(
        f"{PATH_TO_TEST_REPORTS}/PF_Round_1_Success.xlsx"
    )

    expect(submit_upload_success_page.get_title()).to_be_visible()
    expect(submit_upload_success_page.get_subtitle()).to_be_visible()

    _, fund_email = lookup_confirmation_emails(user_auth.email_address)

    fund_download_link = extract_email_link(fund_email)

    download_page = DownloadDataPage(page)
    download_page.navigate(fund_download_link)

    filename = download_page.download_file()
    assert filename.endswith(".xlsx")

    with open(filename, "rb") as f:
        download_data = f.read()
        assert len(download_data)
