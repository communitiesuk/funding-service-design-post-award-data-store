from flask.testing import FlaskClient


def test_get_organisation_names_failure(app: FlaskClient):
    """Asserts failed retrieval of organisation names."""

    response = app.get("/organisations")

    assert response.status_code == 404
    assert response.json["detail"] == "No organisation names found."


def test_get_organisation_names(seeded_app_ctx):
    """Asserts successful retrieval of organisation names."""

    response = seeded_app_ctx.get("/organisations")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    response_json = response.json

    assert any("name" in org for org in response_json)
    assert all(isinstance(org["name"], str) for org in response_json)

    assert any("id" in org for org in response_json)
    assert all(isinstance(org["id"], str) for org in response_json)
