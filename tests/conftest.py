import pytest

from app import create_app
from core.db import db


@pytest.fixture
def test_client():
    """
    Returns a test client with pushed application context.

    Wipes db after use.

    :return: a flask test client with application context.
    """
    with create_app().test_client() as test_client:
        with test_client.application.app_context():
            db.create_all()
            yield test_client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def seeded_test_client(test_client):
    """
    Load seed data into test database.

    NOTE: This is currently seeded via the ingest endpoint due to time constraints.

    This is a fixture. Extends test_client.

    :return: a flask test client with application context and seeded db.
    """
    # TODO: Replace seeding via ingest with independent test seed data.
    with open(test_client.application.config["EXAMPLE_DATA_MODEL_PATH"], "rb") as example_data_model_file:
        endpoint = "/ingest"
        response = test_client.post(
            endpoint,
            data={
                "excel_file": example_data_model_file,
            },
        )
        # check endpoint gave a success response to ingest
        assert response.status_code == 200
        yield test_client
