from datetime import datetime

from flask.testing import FlaskClient

from core.const import DATETIME_ISO_8610
from core.db import db, entities

# isort: off
from core.db.entities import Organisation, Programme, Submission


# isort: on

# TODO: Test these endpoints with specific seeded data that doesn't rely on being seeded via the example data model ss


def test_get_organisation_names_failure(test_client):
    """Asserts failed retrieval of organisation names."""

    response = test_client.get("/organisations")

    assert response.status_code == 404
    assert response.json["detail"] == "No organisation names found."


def test_get_organisation_names(seeded_test_client):
    """Asserts successful retrieval of organisation names."""

    response = seeded_test_client.get("/organisations")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    response_json = response.json

    assert all("name" in org for org in response_json)
    assert all(isinstance(org["name"], str) for org in response_json)

    assert all("id" in org for org in response_json)
    assert all(isinstance(org["id"], str) for org in response_json)


def test_get_organisation_names_does_not_include_unreferenced_orgs(test_client):
    """Asserts successful retrieval of organisation names."""

    unreferenced_org = Organisation(organisation_name="unreferenced org")
    referenced_org = Organisation(organisation_name="referenced org")
    db.session.add_all([unreferenced_org, referenced_org])
    db.session.flush()  # create UUIDs

    programme = Programme(
        programme_id="Prog ID", programme_name="Prog Name", fund_type_id="Fund ID", organisation_id=referenced_org.id
    )
    db.session.add(programme)

    response = test_client.get("/organisations")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    response_json = response.json

    assert unreferenced_org.organisation_name not in response_json


def test_get_organisations_alphabetically(seeded_test_client):
    """
    Test the function that retrieves organisations in alphabetical order.

    :seeded_test_client: A testing client with seeded data.

    :Raises:
        AssertionError: If the response to the GET request does not match the expected output.
    """
    # Populate organisation table (2 rows)
    beta_org = entities.Organisation(organisation_name="Beta")
    alpha_org = entities.Organisation(organisation_name="Alpha")
    db.session.add(beta_org)
    db.session.add(alpha_org)
    db.session.flush()

    # Populate programme table as to register organisations (2 rows)
    beta = Programme(programme_id="Beta", programme_name="Beta", fund_type_id="TD", organisation_id=beta_org.id)
    alpha = Programme(programme_id="Alpha", programme_name="Alpha", fund_type_id="HS", organisation_id=alpha_org.id)

    db.session.add_all([beta, alpha])

    read_org = entities.Organisation.query.first()
    assert read_org.organisation_name == "A District Council From Hogwarts"

    response = seeded_test_client.get("/organisations")

    assert response.status_code == 200
    assert response.content_type == "application/json"
    # this asserts that the HS is odered before the TD
    assert response.json[0]["name"] == "A District Council From Hogwarts"
    # this asserts that row 2/3 has been ordered to position 3/3 hence alphabetical sorting is a success
    assert response.json[2]["name"] == "Beta"


def test_get_funds_not_found(test_client):
    """Asserts failed retrieval of funds."""

    response = test_client.get("/funds")

    assert response.status_code == 404
    assert response.json["detail"] == "No funds found."


def test_get_funds(seeded_test_client):
    """Asserts successful retrieval of funds."""

    response = seeded_test_client.get("/funds")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    response_json = response.json

    assert all("name" in fund for fund in response_json)
    assert all(isinstance(fund["name"], str) for fund in response_json)

    assert all("id" in fund for fund in response_json)
    assert all(isinstance(fund["id"], str) for fund in response_json)


def test_get_funds_alphabetically(seeded_test_client):
    """
    Test the function that retrieves funds in alphabetical order via the fund_id.

    :Raises:
        AssertionError: If the response to the GET request does not match the expected output.
    """
    read_org = entities.Organisation.query.first()

    programme1 = entities.Programme(
        programme_id="1",
        programme_name="test programme",
        fund_type_id="TD",
        organisation_id=read_org.id,
    )

    programme2 = entities.Programme(
        programme_id="2",
        programme_name="test programme2",
        fund_type_id="TD",
        organisation_id=read_org.id,
    )

    programme3 = entities.Programme(
        programme_id="3",
        programme_name="test programme3",
        fund_type_id="HS",
        organisation_id=read_org.id,
    )

    db.session.add_all([programme1, programme2, programme3])

    response = seeded_test_client.get("/funds")

    assert response.status_code == 200
    assert response.content_type == "application/json"
    # This asserts that fund with TD has been sorted to appear after HS to prove alphabetical sorting of the fund_ID
    assert response.get_json() == [{"name": "High Street Fund", "id": "HS"}, {"name": "Town Deal", "id": "TD"}]

    db.session.flush()


def test_get_outcome_categories_not_found(test_client):
    """Asserts failed retrieval of outcome categories."""

    response = test_client.get("/outcome-categories")

    assert response.status_code == 404
    assert response.json["detail"] == "No outcome categories found."


def test_get_outcome_categories(seeded_test_client):
    """Asserts successful retrieval of outcome categories."""

    response = seeded_test_client.get("/outcome-categories")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    response_json = response.json

    assert response_json
    assert all(isinstance(cat, str) for cat in response_json)


def test_get_outcome_alphabetical_sorting(seeded_test_client, test_client):
    """Asserts that the outcomes in get filters are alphabetically sorted by outcome_category"""

    response = seeded_test_client.get("/outcome-categories")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    # Tests that the list has been sorted - with no sorting the output is ['Transport', 'Culture ', 'Place', 'Economy']
    assert response.json == ["Culture ", "Economy", "Place", "Transport"]


def test_get_regions_not_found(test_client):
    """Asserts failed retrieval of regions."""

    response = test_client.get("/regions")

    assert response.status_code == 404
    assert response.json["detail"] == "No regions found."


def test_get_regions(seeded_test_client):
    """Asserts successful retrieval of regions."""

    response = seeded_test_client.get("/regions")

    assert response.status_code == 200
    response_json = response.json

    assert response_json
    assert all(isinstance(region, str) for region in response_json)


def test_get_reporting_period_range_not_found(test_client: FlaskClient):
    """Asserts failed retrieval of funds."""

    response = test_client.get("/reporting-period-range")

    assert response.status_code == 404
    assert response.json["detail"] == "No reporting period range found."


def test_get_reporting_period_range(test_client):
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

    response = test_client.get("/reporting-period-range")

    assert response.status_code == 200
    assert response.content_type == "application/json"

    expected_start = datetime(2021, 6, 1).strftime(DATETIME_ISO_8610) + "Z"
    expected_end = datetime(2025, 6, 30).strftime(DATETIME_ISO_8610) + "Z"

    response_json = response.json
    assert response_json == {"start_date": expected_start, "end_date": expected_end}
