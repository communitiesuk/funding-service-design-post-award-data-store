from abc import ABC, abstractmethod

from playwright.sync_api import Locator

from tests.e2e_tests.pages import BasePage


class SubmitDashboardPage(BasePage):
    def navigate(self):
        self.page.goto(f"{self.domain}/dashboard")

    def select_fund(self, fund_name: str) -> "SubmitUploadPage":
        self.page.get_by_text(fund_name).click()

        return SubmitUploadPage(self.page)


class SubmitUploadPage(BasePage):
    def upload_report(self, file_path: str) -> "SubmitUploadResponsePage":
        self.page.set_input_files("input[type='file']", file_path)

        request_data_button = self.page.get_by_role("button", name="Upload and check for errors")
        request_data_button.click()

        if "Initial_Validation_Failures" in file_path:
            return SubmitUploadInitialErrorPage(self.page)

        if "General_Validation_Failures" in file_path:
            return SubmitUploadGeneralErrorPage(self.page)

        if "Success" in file_path:
            return SubmitUploadSuccessPage(self.page)

        raise ValueError("Unrecognized file path: no matching response page found.")


class SubmitUploadResponsePage(ABC):
    @abstractmethod
    def get_title(self) -> Locator:
        pass

    @abstractmethod
    def get_subtitle(self) -> Locator:
        pass


class SubmitUploadInitialErrorPage(SubmitUploadPage, SubmitUploadResponsePage):
    def get_title(self) -> Locator:
        return self.page.get_by_role("heading", name="There is a problem")

    def get_subtitle(self) -> Locator:
        return self.page.get_by_text("Some of your data is not what we expect").first


class SubmitUploadGeneralErrorPage(SubmitUploadPage, SubmitUploadResponsePage):
    def get_title(self) -> Locator:
        return self.page.get_by_role("heading", name="There are errors in your return")

    def get_subtitle(self) -> Locator:
        return self.page.get_by_text("Fix these errors and re-upload your return.")


class SubmitUploadSuccessPage(BasePage, SubmitUploadResponsePage):
    def get_title(self) -> Locator:
        return self.page.get_by_role("heading", name="No errors found")

    def get_subtitle(self) -> Locator:
        return self.page.get_by_text("Return submitted")
