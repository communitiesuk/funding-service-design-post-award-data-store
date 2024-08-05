import pytest
from playwright.sync_api import Page


@pytest.fixture(autouse=True)
def _viewport(request, page: Page):
    width, height = request.config.getoption("viewport").split("x")
    page.set_viewport_size({"width": int(width), "height": int(height)})
