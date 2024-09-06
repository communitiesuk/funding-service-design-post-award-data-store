from playwright.sync_api import Page

from tests.e2e_tests.models import TestFundConfig


class BasePage:
    def __init__(self, page: Page, domain: str | None = None, fund_config: TestFundConfig | None = None):
        self.page = page
        self.domain = domain
        self.fund_config = fund_config
