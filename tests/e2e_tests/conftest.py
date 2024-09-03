import dataclasses

import pytest
from playwright.sync_api import Page

from config import Config


@pytest.fixture(autouse=True)
def _viewport(request, page: Page):
    width, height = request.config.getoption("viewport").split("x")
    page.set_viewport_size({"width": int(width), "height": int(height)})


@dataclasses.dataclass
class FundingServiceDomains:
    authenticator: str
    find: str
    submit: str


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


@dataclasses.dataclass
class TestFundConfig:
    short_name: str
    round: str


@pytest.fixture()
def authenticator_fund_config(request):
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
