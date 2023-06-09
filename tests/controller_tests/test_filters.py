from datetime import datetime

from flask.testing import FlaskClient

from core.db import db
from core.db.entities import Submission


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


def test_get_returns_not_found(app: FlaskClient):
    """Asserts failed retrieval of funds."""

    response = app.get("/returns")

    assert response.status_code == 404
    assert response.json["detail"] == "No return periods found."


def test_get_returns(app_ctx):
    """Asserts successful retrieval of financial periods."""

    # Create some sample submissions for testing
    sub1 = Submission(
        submission_id="1",
        submission_date=datetime(2023, 5, 1),
        reporting_period_start=datetime(2023, 4, 1),
        reporting_period_end=datetime(2023, 4, 30),
        reporting_round=1,
    )
    sub2 = Submission(
        submission_id="2",
        submission_date=datetime(2024, 5, 5),
        reporting_period_start=datetime(2024, 5, 1),
        reporting_period_end=datetime(2024, 5, 31),
        reporting_round=2,
    )
    sub3 = Submission(
        submission_id="3",
        submission_date=datetime(2025, 6, 1),
        reporting_period_start=datetime(2025, 6, 1),
        reporting_period_end=datetime(2025, 6, 30),
        reporting_round=1,
    )
    sub4 = Submission(
        submission_id="4",
        submission_date=datetime(2021, 6, 5),
        reporting_period_start=datetime(2021, 6, 1),
        reporting_period_end=datetime(2021, 6, 30),
        reporting_round=2,
    )
    submissions = [sub1, sub2, sub3, sub4]
    db.session.add_all(submissions)
    db.session.flush()

    response = app_ctx.get("/returns")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    response_json = response.json

    assert response_json == {"start": datetime(2021, 6, 1), "end": datetime(2025, 6, 30)}
