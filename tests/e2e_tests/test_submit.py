import pytest
from playwright.sync_api import Page, expect

from tests.e2e_tests.helpers import (
    extract_email_link,
    lookup_confirmation_emails,
)
from tests.e2e_tests.pages.find import DownloadDataPage
from tests.e2e_tests.pages.submit import SubmitDashboardPage, SubmitUploadPage, SubmitUploadSuccessPage

pytestmark = pytest.mark.e2e


def test_submit_report(domains, user_auth, page: Page):
    dashboard_page = SubmitDashboardPage(page, domain=domains.submit)
    dashboard_page.navigate()

    expect(
        page.get_by_role(
            "heading",
            name="Submit monitoring and evaluation data dashboard",
        )
    ).to_be_visible()

    submit_upload_page: SubmitUploadPage = dashboard_page.select_fund("Pathfinders")
    submit_upload_page.upload_report("tests/integration_tests/mock_pf_returns/PF_Round_1_Success.xlsx")
    submit_upload_success_page: SubmitUploadSuccessPage = submit_upload_page.submit_report()

    expect(submit_upload_success_page.get_title()).to_be_visible()
    expect(submit_upload_success_page.get_subtitle()).to_be_visible()

    la_email, fund_email = lookup_confirmation_emails(user_auth.email_address)

    assert la_email is not None
    assert fund_email is not None

    fund_download_link = extract_email_link(fund_email)

    download_page = DownloadDataPage(page)
    download_page.navigate(fund_download_link)

    filename = download_page.download_file()
    assert filename.endswith(".xlsx")

    with open(filename, "rb") as f:
        download_data = f.read()
        assert len(download_data)
