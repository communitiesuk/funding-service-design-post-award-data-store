import pytest

import tests.db_tests.resources.db_seed_data as db_seed
from app import create_app
from core.db import db
from core.db.entities import Contact, Organisation
from tests.util_test import seed_test_database


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


@pytest.fixture
def seed_test_dataset(flask_test_client):
    """
    Pushes an application context to a test.

    :return: a test application context.
    """
    with flask_test_client.application.app_context():
        seed_test_database(Organisation, db_seed.ORGANISATION_DATA)
        seed_test_database(Contact, db_seed.CONTACT_DATA)
        # TODO: Add further models like this. In order -> package -> project -> the rest

        db.session.commit()

        yield
        db.session.remove()
        db.drop_all()
