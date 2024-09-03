import re
import secrets
import time

import requests
from notifications_python_client import NotificationsAPIClient
from playwright._impl._errors import Error as PlaywrightError
from playwright.sync_api import Page

from config import Config
from tests.e2e_tests.conftest import FundingServiceDomains, TestFundConfig


def login_via_magic_link(
    page: Page,
    test_name: str,
    domains: FundingServiceDomains,
    fund_config: TestFundConfig,
    email_domain: str = "levellingup.gov.test",
):
    response = requests.get(f"{domains.authenticator}/magic-links")

    magic_links_before = set(response.json())

    url = f"{domains.authenticator}/service/magic-links/new?fund={fund_config.short_name}&round={fund_config.round}"
    page.goto(url)

    # Help disambiguate tests running around the same time by injecting a random token into the email, so that
    # when we lookup the email it should be unique. We avoid a UUID so as to keep the emails 'short enough'.
    token = secrets.token_urlsafe(8)
    email_address = f"fsd-e2e-tests+{test_name}-{token}@{email_domain}".lower()
    page.get_by_role("textbox", name="email").fill(email_address)
    page.get_by_role("button", name="Continue").click()

    response = requests.get(f"{domains.authenticator}/magic-links")
    magic_links_after = set(response.json())

    new_magic_links = magic_links_after - magic_links_before
    for magic_link in new_magic_links:
        if magic_link.startswith("link:"):
            break
    else:
        raise KeyError("Could not generate/retrieve a new magic link via authenticator")

    magic_link_id = magic_link.split(":")[1]
    try:
        page.goto(f"{domains.authenticator}/magic-links/{magic_link_id}")

    except PlaywrightError:
        # FIXME: Authenticator gets into a weird redirect loop locally... We just ignore that error.
        pass

    return email_address


def lookup_find_download_link_for_user_in_govuk_notify(email_address: str, retries: int = 30, delay: int = 1) -> str:
    client = NotificationsAPIClient(Config.E2E_NOTIFY_FIND_API_KEY)

    while retries >= 0:
        emails = client.get_all_notifications(template_type="email", status="delivered")["notifications"]
        for email in emails:
            if email["email_address"] == email_address:
                return re.findall(
                    r"\[Visit the data download page to download your file\]"
                    r"\(\s*([^\)]+?)\s*\)\s+"
                    r"This link will stop working after 7 days.",
                    email["body"],
                )[0]

        time.sleep(delay)
        retries -= 1

    raise LookupError("Could not find a corresponding find download link in GOV.UK Notify")
