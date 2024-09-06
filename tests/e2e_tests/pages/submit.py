from tests.e2e_tests.pages import BasePage


class SubmitDashboardPage(BasePage):
    def navigate(self):
        self.page.goto(f"{self.domain}/dashboard")

    def select_fund(self, fund_name: str) -> "SubmitUploadPage":
        self.page.get_by_text(fund_name).click()

        return SubmitUploadPage(self.page)


class SubmitUploadPage(BasePage):
    def upload_report(self, file_path: str):
        self.page.set_input_files("input[type='file']", file_path)

    def submit_report(self) -> "SubmitUploadSuccessPage":
        request_data_button = self.page.get_by_role("button", name="Upload and check for errors")
        request_data_button.click()

        return SubmitUploadSuccessPage(self.page)


class SubmitUploadSuccessPage(BasePage):
    def get_title(self):
        return self.page.get_by_role("heading", name="No errors found")

    def get_subtitle(self):
        return self.page.get_by_text("Return submitted")
