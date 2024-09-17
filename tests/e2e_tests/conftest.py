import datetime
import uuid
import warnings

import jwt
import pytest
from playwright.sync_api import BrowserContext, ConsoleMessage, Page
from pytest import FixtureRequest
from pytest_playwright.pytest_playwright import CreateContextCallback

from config import Config
from tests.e2e_tests.config import AWSEndToEndSecrets, EndToEndTestSecrets, LocalEndToEndSecrets
from tests.e2e_tests.dataclasses import Account, FundingServiceDomains, TestFundConfig
from tests.e2e_tests.helpers import generate_email_address


@pytest.fixture(autouse=True)
def _viewport(request: FixtureRequest, page: Page):
    width, height = request.config.getoption("viewport").split("x")
    page.set_viewport_size({"width": int(width), "height": int(height)})


@pytest.fixture()
def domains(request: FixtureRequest) -> FundingServiceDomains:
    e2e_env = request.config.getoption("e2e_env")

    if e2e_env == "local":
        return FundingServiceDomains(
            cookie=".levellingup.gov.localhost",
            authenticator=f"http://{Config.AUTHENTICATOR_HOST}.levellingup.gov.localhost:4004",
            find=f"http://{Config.FIND_HOST}",
            submit=f"http://{Config.SUBMIT_HOST}",
        )
    elif e2e_env == "dev":
        return FundingServiceDomains(
            cookie=".dev.access-funding.test.levellingup.gov.uk",
            authenticator="https://authenticator.dev.access-funding.test.levellingup.gov.uk",
            find="https://find-monitoring-data.dev.access-funding.test.levellingup.gov.uk",
            submit="https://submit-monitoring-data.dev.access-funding.test.levellingup.gov.uk",
        )
    elif e2e_env == "test":
        return FundingServiceDomains(
            cookie=".test.access-funding.test.levellingup.gov.uk",
            authenticator="https://authenticator.test.access-funding.test.levellingup.gov.uk",
            find="https://find-monitoring-data.test.access-funding.test.levellingup.gov.uk",
            submit="https://submit-monitoring-data.test.access-funding.test.levellingup.gov.uk",
        )
    else:
        raise ValueError(f"not configured for {e2e_env}")


@pytest.fixture()
def authenticator_fund_config(request: FixtureRequest) -> TestFundConfig:
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


@pytest.fixture
def context(new_context: CreateContextCallback, request: FixtureRequest, e2e_test_secrets: EndToEndTestSecrets):
    e2e_env = request.config.getoption("e2e_env")
    http_credentials = e2e_test_secrets.HTTP_BASIC_AUTH if e2e_env in {"dev", "test"} else None
    return new_context(http_credentials=http_credentials)


@pytest.fixture
def e2e_test_secrets(request: FixtureRequest) -> EndToEndTestSecrets:
    e2e_env = request.config.getoption("e2e_env")
    e2e_aws_vault_profile = request.config.getoption("e2e_aws_vault_profile")

    if e2e_env == "local":
        return LocalEndToEndSecrets()

    if e2e_env in {"dev", "test"}:
        return AWSEndToEndSecrets(e2e_env=e2e_env, e2e_aws_vault_profile=e2e_aws_vault_profile)

    raise ValueError(f"Unknown e2e_env: {e2e_env}.")


@pytest.fixture()
def user_auth(
    request: FixtureRequest,
    domains: FundingServiceDomains,
    authenticator_fund_config: TestFundConfig,
    context: BrowserContext,
    e2e_test_secrets: EndToEndTestSecrets,
) -> Account:
    """This fixture sets up the browser with an auth cookie so that the test user is 'logged in' correctly.

    It bypasses the standard authentication process of doing this (using Authenticator), and instead (ab)uses our
    JWT authentication model by self-signing the blob of data that authenticator provides.

    We should be careful to keep this blob of JWT data in sync with what Authenticator would actually set."""
    email_address = generate_email_address(
        test_name=request.node.originalname,
        email_domain="communities.gov.uk",
    )
    roles_marker = request.node.get_closest_marker("user_roles")
    user_roles = roles_marker.args[0] if roles_marker else []

    now = int(datetime.datetime.timestamp(datetime.datetime.now()))
    jwt_data = {
        "accountId": str(uuid.uuid4()),
        "azureAdSubjectId": str(uuid.uuid4()),
        "email": email_address,
        "fullName": f"E2E Test User - {request.node.originalname}",
        "roles": user_roles,
        "iat": now,
        "exp": now + (15 * 60),  # 15 minutes from now
    }

    # Algorithm below must match that used by fsd-authenticator
    cookie_value = jwt.encode(jwt_data, e2e_test_secrets.JWT_SIGNING_KEY, algorithm="RS256")

    context.add_cookies(
        [
            {
                "name": Config.FSD_USER_TOKEN_COOKIE_NAME,
                "value": cookie_value,
                "domain": domains.cookie,
                "path": "/",
                "httpOnly": True,
                "secure": True,
            }
        ]
    )

    return Account(email_address=email_address, roles=user_roles)


@pytest.fixture(autouse=True)
def check_browser_console_logs(context: BrowserContext, page: Page):
    def record_console_message(message: ConsoleMessage):
        if message.type == "error":
            warnings.warn(
                f"Browser console logged an error at URL `{message.page.url}`:\n\n{message.text}",
                Warning,
                stacklevel=1,
            )

    page.on("console", record_console_message)

    yield
