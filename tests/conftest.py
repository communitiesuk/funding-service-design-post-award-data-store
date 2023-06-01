from pathlib import Path

import pytest

from app import create_app
from core.db import db


@pytest.fixture()
def app():
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.
    :return: A flask test client.
    """
    with create_app().test_client() as test_client:
        yield test_client


@pytest.fixture
def app_ctx(app):
    """
    Pushes an application context to a test.

    Wipes db after use.

    :return: a flask test client with application context.
    """
    with app.application.app_context():
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def seeded_app_ctx(app_ctx):
    """
    Load seed data into test database.

    NOTE: This is currently seeded via the ingest endpoint due to time constraints.

    This is a fixture. Extends app_ctx.

    :return: a flask test client with application context and seeded db.
    """
    # TODO: Replace seeding via ingest with independent test seed data.
    with open(
        Path(__file__).parent / "controller_tests" / "resources" / "Data_Model_v3.7_EXAMPLE.xlsx", "rb"
    ) as example_data_model_file:
        endpoint = "/ingest"
        response = app_ctx.post(
            endpoint,
            data={
                "excel_file": example_data_model_file,
            },
        )
        # check endpoint gave a success response to ingest
        assert response.status_code == 200
        yield app_ctx
