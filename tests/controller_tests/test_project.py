from flask.testing import FlaskClient


def test_invalid_project_input(app: FlaskClient):
    """Asserts 400 error if project_id not in db."""

    project_response = app.get("/project/LUF01")

    assert project_response.status_code == 404
    assert project_response.json["detail"] == "The provided project_id: LUF01 did not return any results."


def test_invalid_package_input(app: FlaskClient):
    """Asserts 400 error if programme_id not in db."""

    package_response = app.get("/programme/LUF01")

    assert package_response.status_code == 404
    assert package_response.json["detail"] == "The provided programme_id: LUF01 did not return any results."
