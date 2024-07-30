import pytest
from playwright.sync_api import Page, expect

from tests.e2e_tests.helpers import login_via_magic_link, lookup_find_download_link_for_user_in_govuk_notify
from tests.e2e_tests.pages.find import DownloadDataPage, FindRequestDataPage

pytestmark = pytest.mark.e2e


def test_find_download(page: Page):
    email_address = login_via_magic_link(page, "test_find_download", email_domain="communities.gov.uk")

    request_data_page = FindRequestDataPage(page)
    request_data_page.navigate()

    request_data_page.filter_funds("High Street Fund")
    request_data_page.filter_regions("North West")
    request_data_page.filter_organisations("Bolton Council")
    request_data_page.filter_outcomes("Health & Wellbeing", "Transport")
    request_data_page.filter_returns_period(from_quarter=2, from_year="2023/2024", to_quarter=3, to_year="2023/2024")

    request_data_page.select_file_format("XLSX (Microsoft Excel)")

    request_data_page.request_data()

    expect(page.get_by_role("heading", name="Request received")).to_be_visible()

    download_file_url = lookup_find_download_link_for_user_in_govuk_notify(email_address)
    page.goto(download_file_url)

    download_page = DownloadDataPage(page)
    filename = download_page.download_file()
    assert filename.endswith(".xlsx")

    with open(filename, "rb") as f:
        download_data = f.read()
        assert len(download_data)
