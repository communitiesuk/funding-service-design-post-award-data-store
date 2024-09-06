import pytest
import requests
from playwright._impl._errors import Error as PlaywrightError
from playwright.sync_api import Page

from config import Config
from tests.e2e_tests.helpers import create_account_with_roles, generate_email_address
from tests.e2e_tests.models import FundingServiceDomains, TestFundConfig
from tests.e2e_tests.pages.authenticator import MagicLinkPage, NewMagicLinkPage


@pytest.fixture(autouse=True)
def _viewport(request, page: Page):
    width, height = request.config.getoption("viewport").split("x")
    page.set_viewport_size({"width": int(width), "height": int(height)})


@pytest.fixture()
def domains(request) -> FundingServiceDomains:
    e2e_env = request.config.getoption("e2e_env")
    devtest_basic_auth = Config.E2E_DEVTEST_BASIC_AUTH

    if e2e_env in {"dev", "test"} and not devtest_basic_auth:
        raise ValueError("E2E_DEVTEST_BASIC_AUTH is not set to `username:password` for accessing dev/test environments")

    if e2e_env == "local":
        return FundingServiceDomains(
            authenticator=f"http://{Config.AUTHENTICATOR_HOST}.levellingup.gov.localhost:4004",
            find=f"http://{Config.FIND_HOST}",
            submit=f"http://{Config.SUBMIT_HOST}",
        )
    elif e2e_env == "dev":
        return FundingServiceDomains(
            authenticator=f"https://{devtest_basic_auth}@authenticator.dev.access-funding.test.levellingup.gov.uk",
            find=f"https://{devtest_basic_auth}@find-monitoring-data.dev.access-funding.test.levellingup.gov.uk",
            submit=f"https://{devtest_basic_auth}@submit-monitoring-data.dev.access-funding.test.levellingup.gov.uk",
        )
    elif e2e_env == "test":
        return FundingServiceDomains(
            authenticator=f"https://{devtest_basic_auth}@authenticator.test.access-funding.test.levellingup.gov.uk",
            find=f"https://{devtest_basic_auth}@find-monitoring-data.test.access-funding.test.levellingup.gov.uk",
            submit=f"https://{devtest_basic_auth}@submit-monitoring-data.test.access-funding.test.levellingup.gov.uk",
        )
    else:
        raise ValueError(f"not configured for {e2e_env}")


@pytest.fixture()
def authenticator_fund_config(request) -> TestFundConfig:
    e2e_env = request.config.getoption("e2e_env")

    if e2e_env == "local":
        return TestFundConfig(
            short_name="post-award-e2e-tests",
            round="r1w1",
        )
    elif e2e_env in {"dev", "test"}:
        # A fairly arbitrary choice of fund/round that exists on those environments currently
        return TestFundConfig(
            short_name="HSRA",
            round="R1",
        )
    else:
        raise ValueError(f"not configured for {e2e_env}")


@pytest.fixture()
def user_auth(domains, authenticator_fund_config, page):
    email_address = generate_email_address(
        test_name="test_submit_report",
        email_domain="communities.gov.uk",
    )

    account = create_account_with_roles(
        email_address=email_address,
        roles=["PF_MONITORING_RETURN_SUBMITTER", "TF_MONITORING_RETURN_SUBMITTER"],
    )

    response = requests.get(f"{domains.authenticator}/magic-links")
    magic_links_before = set(response.json())

    new_magic_link_page = NewMagicLinkPage(page, domain=domains.authenticator, fund_config=authenticator_fund_config)
    new_magic_link_page.navigate()
    new_magic_link_page.insert_email_address(account.email_address)
    new_magic_link_page.press_continue()

    response = requests.get(f"{domains.authenticator}/magic-links")
    magic_links_after = set(response.json())

    new_magic_links = magic_links_after - magic_links_before
    for magic_link in new_magic_links:
        if magic_link.startswith("link:"):
            break
    else:
        raise KeyError("Could not generate/retrieve a new magic link via authenticator")

    magic_link_id = magic_link.split(":")[1]
    magic_link_page = MagicLinkPage(page, domain=domains.authenticator)

    try:
        magic_link_page.navigate(magic_link_id)
    except PlaywrightError:
        # FIXME: Authenticator gets into a weird redirect loop locally... We just ignore that error.
        pass

    return account
