from flask.testing import FlaskClient

from .assertion_data.mock_package_data import MOCK_PACKAGE_RESPONSE
from .assertion_data.mock_project_data import MOCK_PROJECT_RESPONSE


def test_invalid_project_input(flask_test_client: FlaskClient):
    """Asserts 400 error if project_id not in db."""

    project_response = flask_test_client.get("/project/LUF01")

    assert project_response.status_code == 404
    assert (
        project_response.json["detail"]
        == "The provided project_id: LUF01 did not return any results."
    )


def test_invalid_package_input(flask_test_client: FlaskClient):
    """Asserts 400 error if package_id not in db."""

    package_response = flask_test_client.get("/package/LUF01")

    assert package_response.status_code == 404
    assert (
        package_response.json["detail"]
        == "The provided package_id: LUF01 did not return any results."
    )


def test_get_project_endpoint(flask_test_client: FlaskClient):
    """Asserts that the correct project data is returned from the mock db."""

    response = flask_test_client.get(
        "/project/FHSFDCC001",
    )

    assert response.status_code == 200
    assert response.json == MOCK_PROJECT_RESPONSE


def test_get_package_endpoint(flask_test_client: FlaskClient):
    """Asserts that the correct package data is returned from the mock db."""

    response = flask_test_client.get(
        "/package/FHSF001",
    )

    assert response.status_code == 200
    assert response.json == MOCK_PACKAGE_RESPONSE
