import pytest
from flask.testing import FlaskClient
from werkzeug.datastructures import FileStorage

import config
from app import create_app
from app.main.fund import TOWNS_FUND_APP_CONFIG
from config.envs.unit_test import UnitTestConfig


@pytest.fixture()
def mocked_auth(mocker):
    # mock authorised user
    mocker.patch(
        "fsd_utils.authentication.decorators._check_access_token",
        return_value={
            "accountId": "test-user",
            "roles": [TOWNS_FUND_APP_CONFIG.user_role],
            "email": "user@wigan.gov.uk",
        },
    )


@pytest.fixture()
def mocked_pf_auth(mocker):
    # mock authorised user with Pathfinders role
    mocker.patch(
        "fsd_utils.authentication.decorators._check_access_token",
        return_value={
            "accountId": "pf-test-user",
            "roles": ["PF_MONITORING_RETURN_SUBMITTER"],
            "email": "pf-user@wigan.gov.uk",
        },
    )


@pytest.fixture()
def flask_test_client(mocked_auth) -> FlaskClient:
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.

    NOTE: Auth is mocked here because it's required for all routes.

    :return: A flask test client.
    """
    with create_app(config.Config).test_client() as test_client:
        yield test_client


@pytest.fixture()
def unauthenticated_flask_test_client() -> FlaskClient:
    """
    :return: An unauthenticated flask test client.
    """
    with create_app(config.Config).test_client() as test_client:
        yield test_client


@pytest.fixture(scope="function")
def example_pre_ingest_data_file() -> FileStorage:
    """An example pre ingest spreadsheet in towns-fund format."""
    with open(UnitTestConfig.EXAMPLE_INGEST_DATA_PATH, "rb") as file:
        yield file


@pytest.fixture(scope="function")
def example_ingest_wrong_format() -> FileStorage:
    """An example pre ingest spreadsheet in towns-fund format."""
    with open(UnitTestConfig.EXAMPLE_INGEST_WRONG_FORMAT, "rb") as file:
        yield file
