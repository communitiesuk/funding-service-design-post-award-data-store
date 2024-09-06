from tests.e2e_tests.pages import BasePage


class NewMagicLinkPage(BasePage):
    def navigate(self):
        url = (
            f"{self.domain}/service/magic-links/new"
            f"?fund={self.fund_config.short_name}"
            f"&round={self.fund_config.round}"
        )

        self.page.goto(url)

    def insert_email_address(self, email_address: str):
        self.page.get_by_role("textbox", name="email").fill(email_address)

    def press_continue(self):
        self.page.get_by_role("button", name="Continue").click()


class MagicLinkPage(BasePage):
    def navigate(self, magic_link_id: str):
        self.page.goto(f"{self.domain}/magic-links/{magic_link_id}")
