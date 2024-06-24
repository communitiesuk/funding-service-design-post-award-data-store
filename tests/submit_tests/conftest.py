from typing import Any, Generator

import pytest
from flask.testing import FlaskClient
from werkzeug.datastructures import FileStorage
from werkzeug.test import TestResponse

import config
from app import create_app
from config.envs.unit_test import UnitTestConfig
from submit.main.fund import TOWNS_FUND_APP_CONFIG


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
def mocked_pf_and_tf_auth(mocker):
    # mock authorised user with Pathfinders role
    mocker.patch(
        "fsd_utils.authentication.decorators._check_access_token",
        return_value={
            "accountId": "pf-tf-test-user",
            "roles": ["PF_MONITORING_RETURN_SUBMITTER", "TF_MONITORING_RETURN_SUBMITTER"],
            "email": "test-user@wigan.gov.uk",
        },
    )


class _SubmitFlaskClient(FlaskClient):
    def open(
        self,
        *args: Any,
        buffered: bool = False,
        follow_redirects: bool = False,
        **kwargs: Any,
    ) -> TestResponse:
        if "headers" in kwargs:
            kwargs["headers"].setdefault("Host", UnitTestConfig.SUBMIT_HOST)
        else:
            kwargs.setdefault("headers", {"Host": UnitTestConfig.SUBMIT_HOST})
        return super().open(*args, buffered=buffered, follow_redirects=follow_redirects, **kwargs)


@pytest.fixture()
def submit_test_client(mocked_auth) -> Generator[FlaskClient, None, None]:
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.

    NOTE: Auth is mocked here because it's required for all routes.

    :return: A flask test client.
    """
    app = create_app(config.Config)
    app.test_client_class = _SubmitFlaskClient
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture()
def unauthenticated_submit_test_client() -> Generator[FlaskClient, None, None]:
    """
    :return: An unauthenticated flask test client.
    """
    app = create_app(config.Config)
    app.test_client_class = _SubmitFlaskClient
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(scope="function")
def example_pre_ingest_data_file() -> Generator[FileStorage, None, None]:
    """An example pre ingest spreadsheet in towns-fund format."""
    with open(UnitTestConfig.EXAMPLE_INGEST_DATA_PATH, "rb") as file:
        yield FileStorage(file)


@pytest.fixture(scope="function")
def example_ingest_wrong_format() -> Generator[FileStorage, None, None]:
    """An example pre ingest spreadsheet in towns-fund format."""
    with open(UnitTestConfig.EXAMPLE_INGEST_WRONG_FORMAT, "rb") as file:
        yield FileStorage(file)
