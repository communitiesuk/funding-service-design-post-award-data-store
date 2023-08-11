import pytest
from werkzeug.datastructures import FileStorage

import config
from app import create_app
from config.envs.unit_test import UnitTestConfig


@pytest.fixture()
def mocked_auth(monkeypatch):
    def access_token(return_app):
        return {"accountId": "test-user", "roles": []}

    monkeypatch.setattr(
        "fsd_utils.authentication.decorators._check_access_token",
        access_token,
    )


@pytest.fixture()
def flask_test_client(mocked_auth):
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.

    NOTE: Auth is mocked here because it's required for all routes.

    :return: A flask test client.
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
