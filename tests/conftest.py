import pytest

from app import create_app
from core.db import db


@pytest.fixture
def app_ctx(flask_test_client):
    """
    Pushes an application context to a test.

    :return: a test application context.
    """
    with flask_test_client.application.app_context():
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture()
def flask_test_client():
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.
    :return: A flask test client.
    """
    with create_app().test_client() as test_client:
        yield test_client
