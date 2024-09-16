import random

import pytest
from playwright.sync_api import Page, expect

from tests.e2e_tests.config import EndToEndTestSecrets
from tests.e2e_tests.helpers import (
    lookup_find_download_link_for_user_in_govuk_notify,
)
from tests.e2e_tests.pages.find import DownloadDataPage, FindRequestDataPage, FindRequestDataSuccessPage

pytestmark = pytest.mark.e2e


def test_find_download(domains, user_auth, page: Page, e2e_test_secrets: EndToEndTestSecrets):
    request_data_page = FindRequestDataPage(page, domain=domains.find)
    request_data_page.navigate()

    random_fund = random.choice(request_data_page.get_funds())
    request_data_page.filter_funds(random_fund)

    random_region = random.choice(request_data_page.get_regions())
    request_data_page.filter_regions(random_region)

    random_org = random.choice(request_data_page.get_organisations())
    request_data_page.filter_organisations(random_org)

    random_outcomes = random.choices(request_data_page.get_outcomes(), k=2)
    request_data_page.filter_outcomes(*random_outcomes)

    request_data_page.filter_returns_period(from_quarter=2, from_year="2022/2023", to_quarter=3, to_year="2022/2023")
    request_data_page.select_file_format("XLSX (Microsoft Excel)")

    find_request_data_success_page: FindRequestDataSuccessPage = request_data_page.request_data()

    expect(find_request_data_success_page.get_title()).to_be_visible()

    download_file_url = lookup_find_download_link_for_user_in_govuk_notify(user_auth.email_address, e2e_test_secrets)

    download_page = DownloadDataPage(page)
    download_page.navigate(download_file_url)

    filename = download_page.download_file()
    assert filename.endswith(".xlsx")

    with open(filename, "rb") as f:
        download_data = f.read()
        assert len(download_data)
