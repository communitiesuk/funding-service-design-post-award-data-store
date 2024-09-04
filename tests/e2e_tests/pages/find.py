import tempfile
from typing import Literal

from tests.e2e_tests.pages import BasePage


class FindRequestDataPage(BasePage):
    def navigate(self):
        self.page.goto(f"{self.domain}/download")

    def reveal_funds(self):
        if self.page.get_by_label("Filter by fund , Show this section").is_visible():
            self.page.get_by_label("Filter by fund , Show this section").click()

    def reveal_regions(self):
        if self.page.get_by_label("Filter by region , Show this section").is_visible():
            self.page.get_by_label("Filter by region , Show this section").click()

    def reveal_organisations(self):
        if self.page.get_by_label("Filter by funded organisation , Show this section").is_visible():
            self.page.get_by_label("Filter by funded organisation , Show this section").click()

    def reveal_outcomes(self):
        if self.page.get_by_label("Filter by outcomes , Show this section").is_visible():
            self.page.get_by_label("Filter by outcomes , Show this section").click()

    def reveal_returns_period(self):
        if self.page.get_by_label("Filter by returns period , Show this section").is_visible():
            self.page.get_by_label("Filter by returns period , Show this section").click()

    def filter_funds(self, *funds: str):
        self.reveal_funds()

        for fund in funds:
            self.page.get_by_label(fund).check()

    def filter_regions(self, *regions: str):
        self.reveal_regions()

        for region in regions:
            self.page.get_by_label(region).check()

    def filter_organisations(self, *organisations: str):
        self.reveal_organisations()

        for organisation in organisations:
            self.page.get_by_label(organisation).check()

    def filter_outcomes(self, *outcomes: str):
        self.reveal_outcomes()

        for outcome in outcomes:
            self.page.get_by_label(outcome).check()

    def filter_returns_period(
        self, from_quarter: Literal[1, 2, 3, 4], from_year: str, to_quarter: Literal[1, 2, 3, 4], to_year: str
    ):
        self.reveal_returns_period()

        self.page.locator("#from-quarter").select_option(str(from_quarter))
        self.page.locator("#from-year").select_option(from_year)

        self.page.locator("#to-quarter").select_option(str(to_quarter))
        self.page.locator("#to-year").select_option(to_year)

    def select_file_format(self, file_format: Literal["XLSX (Microsoft Excel)", "JSON"]):
        self.page.get_by_text(file_format).click()

    def request_data(self):
        request_data_button = self.page.get_by_role("button", name="Confirm and request data")
        request_data_button.click()


class DownloadDataPage(BasePage):
    def download_file(self) -> str:
        with self.page.expect_download() as download_info:
            self.page.get_by_role("button", name="Download your data").click()

        download = download_info.value
        tempdir = tempfile.gettempdir()
        download_filename = tempdir + "/" + download_info.value.suggested_filename
        download.save_as(download_filename)
        return download_filename
