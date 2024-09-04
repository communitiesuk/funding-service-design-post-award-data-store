from playwright.sync_api import Page


class BasePage:
    def __init__(self, page: Page, domain: str | None = None):
        self.page = page
        self.domain = domain
