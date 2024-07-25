from datetime import datetime

import pytest
from flask.testing import FlaskClient

from data_store.controllers.get_filters import (
    get_funds,
    get_geospatial_regions,
    get_organisation_names,
    get_outcome_categories,
    get_reporting_period_range,
)
from data_store.db import db, entities
from data_store.db.entities import Fund, Organisation, Programme, Submission


def test_get_organisation_names_failure(test_session):
    """Asserts failed retrieval of organisation names."""

    with pytest.raises(RuntimeError) as e:
        get_organisation_names()

    assert str(e.value) == "No organisation names found."


def test_get_funds_not_found(test_session):
    """Asserts failed retrieval of funds."""

    with pytest.raises(RuntimeError) as e:
        get_funds()

    assert str(e.value) == "No funds found."


def test_get_outcome_categories_not_found(test_session):
    """Asserts failed retrieval of outcome categories."""

    with pytest.raises(RuntimeError) as e:
        get_outcome_categories()

    assert str(e.value) == "No outcome categories found."


def test_get_regions_not_found(test_session):
    """Asserts failed retrieval of regions."""

    with pytest.raises(RuntimeError) as e:
        get_geospatial_regions()

    assert str(e.value) == "No regions found."


def test_get_reporting_period_range_not_found(test_session: FlaskClient):
    """Asserts failed retrieval of funds."""

    with pytest.raises(RuntimeError) as e:
        get_reporting_period_range()

    assert str(e.value) == "No reporting period range found."


def test_get_organisation_names(seeded_test_client):
    """Asserts successful retrieval of organisation names."""

    data = get_organisation_names()

    assert all("name" in org for org in data)
    assert all(isinstance(org["name"], str) for org in data)

    assert all("id" in org for org in data)
    assert all(isinstance(org["id"], str) for org in data)


def test_get_organisation_names_does_not_include_unreferenced_orgs(seeded_test_client_rollback):
    """Asserts successful retrieval of organisation names."""

    unreferenced_org = Organisation(organisation_name="unreferenced org")
    referenced_org = Organisation(organisation_name="referenced org")
    db.session.add_all([unreferenced_org, referenced_org])
    db.session.flush()  # create UUIDs

    fund_id = Fund.query.first().id

    programme = Programme(
        programme_id="Prog ID", programme_name="Prog Name", fund_type_id=fund_id, organisation_id=referenced_org.id
    )
    db.session.add(programme)

    data = get_organisation_names()

    response_names = [record["name"] for record in data]
    assert unreferenced_org.organisation_name not in response_names
    assert referenced_org.organisation_name in response_names


def test_get_organisations_alphabetically(seeded_test_client_rollback):
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

    fund_id_1 = Fund.query.all()[0].id
    fund_id_2 = Fund.query.all()[1].id

    # Populate programme table as to register organisations (2 rows)
    beta = Programme(programme_id="Beta", programme_name="Beta", fund_type_id=fund_id_1, organisation_id=beta_org.id)
    alpha = Programme(
        programme_id="Alpha", programme_name="Alpha", fund_type_id=fund_id_2, organisation_id=alpha_org.id
    )

    db.session.add_all([beta, alpha])

    read_org = entities.Organisation.query.first()
    assert read_org.organisation_name == "A District Council From Hogwarts"

    data = get_organisation_names()

    # this asserts that the HS is odered before the TD
    assert data[0]["name"] == "A District Council From Hogwarts"
    # this asserts that row 2/3 has been ordered to position 3/3 hence alphabetical sorting is a success
    assert data[2]["name"] == "Beta"


def test_get_funds(seeded_test_client):
    """Asserts successful retrieval of funds."""

    data = get_funds()

    assert all("name" in fund for fund in data)
    assert all(isinstance(fund["name"], str) for fund in data)

    assert all("id" in fund for fund in data)
    assert all(isinstance(fund["id"], str) for fund in data)


def test_get_funds_alphabetically(seeded_test_client_rollback):
    """
    Test the function that retrieves funds in alphabetical order via the fund_id.

    :Raises:
        AssertionError: If the response to the GET request does not match the expected output.
    """
    data = get_funds()

    # This asserts that fund with TD has been sorted to appear after HS to prove alphabetical sorting of the fund_ID
    assert data == [
        {"id": "HS", "name": "High Street Fund"},
        {"id": "PF", "name": "Pathfinders"},
        {"id": "TD", "name": "Town Deal"},
    ]


def test_get_outcome_categories(seeded_test_client):
    """Asserts successful retrieval of outcome categories."""

    data = get_outcome_categories()

    assert data
    assert all(isinstance(cat, str) for cat in data)


def test_get_outcome_alphabetical_sorting(seeded_test_client):
    """Asserts that the outcomes in get filters are alphabetically sorted by outcome_category"""

    data = get_outcome_categories()

    # Tests that the list has been sorted - with no sorting the output is ['Transport', 'Culture', 'Place', 'Economy']
    assert data == ["Culture", "Economy", "Place", "Transport"]


def test_get_geospatial_regions(seeded_test_client):
    """Asserts successful retrieval of regions."""

    data = get_geospatial_regions()

    assert all("name" in region for region in data)
    assert all(isinstance(region["name"], str) for region in data)

    assert all("id" in region for region in data)
    assert all(isinstance(region["id"], str) for region in data)

    # This asserts that the region with Northern Ireland has been sorted to appear after London to prove
    # alphabetical sorting of the region name
    assert data == [{"id": "TLI", "name": "London"}, {"id": "TLN", "name": "Northern Ireland"}]


def test_get_reporting_period_range(seeded_test_client_rollback):
    """Asserts successful retrieval of financial periods."""

    # Create some sample submissions for testing
    sub1 = Submission(
        submission_id="1",
        submission_date=datetime(2023, 5, 1),
        reporting_period_start=datetime(2023, 4, 1),
        reporting_period_end=datetime(2023, 4, 30),
    )
    sub2 = Submission(
        submission_id="2",
        submission_date=datetime(2024, 5, 5),
        reporting_period_start=datetime(2024, 5, 1),
        reporting_period_end=datetime(2024, 5, 31),
    )
    sub3 = Submission(
        submission_id="3",
        submission_date=datetime(2025, 6, 1),
        reporting_period_start=datetime(2025, 6, 1),
        reporting_period_end=datetime(2025, 6, 30),
    )
    sub4 = Submission(
        submission_id="4",
        submission_date=datetime(2021, 6, 5),
        reporting_period_start=datetime(2021, 6, 1),
        reporting_period_end=datetime(2021, 6, 30),
    )
    submissions = [sub1, sub2, sub3, sub4]
    db.session.add_all(submissions)

    data = get_reporting_period_range()

    expected_start = datetime(2021, 6, 1)
    expected_end = datetime(2025, 6, 30)

    assert data == {"start_date": expected_start, "end_date": expected_end}
