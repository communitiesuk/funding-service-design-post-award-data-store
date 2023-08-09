import pytest

import config
from app import create_app


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
    :return: A flask test client.
    """
    with create_app(config.Config).test_client() as test_client:
        yield test_client
