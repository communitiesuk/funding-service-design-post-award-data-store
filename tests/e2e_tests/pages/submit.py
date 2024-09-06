from tests.e2e_tests.pages import BasePage


class SubmitDashboardPage(BasePage):
    def navigate(self):
        self.page.goto(f"{self.domain}/dashboard")

    def select_fund(self, fund_name: str):
        self.page.get_by_text(fund_name).click()


class SubmitUploadPage(BasePage):
    def upload_report(self, file_path: str):
        self.page.set_input_files("input[type='file']", file_path)

    def submit_report(self):
        request_data_button = self.page.get_by_role("button", name="Upload and check for errors")
        request_data_button.click()
