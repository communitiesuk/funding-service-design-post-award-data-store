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

    assert all("name" in org for org in response_json)
    assert all(isinstance(org["name"], str) for org in response_json)

    assert all("id" in org for org in response_json)
    assert all(isinstance(org["id"], str) for org in response_json)


def test_get_funds_not_found(app: FlaskClient):
    """Asserts failed retrieval of funds."""

    response = app.get("/funds")

    assert response.status_code == 404
    assert response.json["detail"] == "No funds found."


def test_get_funds(seeded_app_ctx):
    """Asserts successful retrieval of funds."""

    response = seeded_app_ctx.get("/funds")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    response_json = response.json

    assert all("name" in fund for fund in response_json)
    assert all(isinstance(fund["name"], str) for fund in response_json)

    assert all("id" in fund for fund in response_json)
    assert all(isinstance(fund["id"], str) for fund in response_json)


def test_get_outcome_categories_not_found(app: FlaskClient):
    """Asserts failed retrieval of outcome categories."""

    response = app.get("/outcome-categories")

    assert response.status_code == 404
    assert response.json["detail"] == "No outcome categories found."


def test_get_outcome_categories(seeded_app_ctx):
    """Asserts successful retrieval of outcome categories."""

    response = seeded_app_ctx.get("/outcome-categories")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    response_json = response.json

    assert response_json
    assert all(isinstance(cat, str) for cat in response_json)
