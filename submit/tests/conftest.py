import pytest
from flask.testing import FlaskClient

import config
from app import create_app


@pytest.fixture()
def flask_test_client() -> FlaskClient:
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.

    NOTE: Auth is mocked here because it's required for all routes.

    :return: A flask test client.
    """
    with create_app(config.Config).test_client() as test_client:
        yield test_client
