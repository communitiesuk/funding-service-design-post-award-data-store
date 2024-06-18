import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from core.db import db
from core.db import entities as ents


def test_programme_contact_organisation(test_client_rollback):
    """
    Test basic relationship structure between Contact, Organisation and Package.

    Basic confidence check that data can be inserted and FK relations are as expected.
    """

    # Populate organisation table (1 row)
    organisation = ents.Organisation(
        organisation_name="Test Organisation",
        geography="Earth",
    )
    db.session.add(organisation)

    fund = ents.Fund(fund_code="JP")
    db.session.add(fund)

    read_org = ents.Organisation.query.first()
    assert read_org.organisation_name == "Test Organisation"

    # Populate programme table (1 row). Various fk ref's set to existing organisation and contact rows.
    programme = ents.Programme(
        programme_id="XXXYY",
        programme_name="test programme",
        fund_type_id=ents.Fund.query.first().id,
        organisation_id=read_org.id,
    )
    db.session.add(programme)
    read_programme = ents.Programme.query.first()
    assert read_programme.programme_name == "test programme"
    assert read_programme.organisation.organisation_name == "Test Organisation"


def test_database_integrity_error(test_client_rollback):
    """Test that an invalid FK ref raises IntegrityError exception."""

    fund = ents.Fund(fund_code="JP")
    db.session.add(fund)

    programme = ents.Programme(
        programme_id="XXXYY",
        programme_name="test programme",
        fund_type_id=ents.Fund.query.first().id,
        organisation_id=uuid.uuid4(),
    )
    db.session.add(programme)
    with pytest.raises(IntegrityError):
        db.session.flush()


def test_project_finance_change_table(seeded_test_client_rollback):
    """Tests basic behaviour of ProjectFinanceChange table"""

    prog_j_id = ents.ProgrammeJunction.query.first().id

    project_finance_change = ents.ProjectFinanceChange(
        programme_junction_id=prog_j_id,
        data_blob={"event_data_1": "crucial data", "event_data_2": "even more crucial data"},
    )
    db.session.add(project_finance_change)
    read_project_finance_change = ents.ProjectFinanceChange.query.first()
    assert read_project_finance_change.programme_junction_id == prog_j_id
    assert read_project_finance_change.data_blob == {
        "event_data_1": "crucial data",
        "event_data_2": "even more crucial data",
    }

    project_finance_change = ents.ProjectFinanceChange(
        programme_junction_id=None,
        data_blob={"event_data_1": "crucial data", "event_data_2": "even more crucial data"},
    )

    db.session.add(project_finance_change)
    with pytest.raises(IntegrityError):
        db.session.flush()


def test_geospatial_dim_table(seeded_test_client_rollback):
    """
    Tests GeospatialDim table is correctly populated with reference data from
    resources/geospatial_dim csv seed data, including checking the number
    of rows in the table and that all itl1 region code and names are valid
    pairs.

    This test should fail if any new data is added to the csv or the
    existing data is mutated. If the test fails it will need to be updated
    and the database will likely need to be reseeded with the updated reference data
    if this comes from an extension of the reference data.
    """

    all_geospatial_data = ents.GeospatialDim.query.order_by(ents.GeospatialDim.postcode_prefix).all()

    assert len(all_geospatial_data) == 124

    assert all_geospatial_data[0].postcode_prefix == "AB"
    assert all_geospatial_data[0].itl1_region_code == "TLM"
    assert all_geospatial_data[0].itl1_region_name == "Scotland"

    assert all_geospatial_data[-1].postcode_prefix == "ZE"
    assert all_geospatial_data[-1].itl1_region_code == "TLM"
    assert all_geospatial_data[-1].itl1_region_name == "Scotland"

    itl1_region_pairs = {
        "TLC": "North East",
        "TLD": "North West",
        "TLE": "Yorkshire and The Humber",
        "TLF": "East Midlands",
        "TLG": "West Midlands",
        "TLH": "East",
        "TLI": "London",
        "TLJ": "South East",
        "TLK": "South West",
        "TLL": "Wales",
        "TLM": "Scotland",
        "TLN": "Northern Ireland",
        "TLZ": "Non-ITL1 Region",
    }

    geospatial_data_itl1_region_pairs = ents.GeospatialDim.query.with_entities(
        ents.GeospatialDim.itl1_region_code, ents.GeospatialDim.itl1_region_name
    ).distinct()

    for row in geospatial_data_itl1_region_pairs:
        region_code = row.itl1_region_code
        region_name = row.itl1_region_name
        assert itl1_region_pairs[region_code] == region_name


def test_project_geospatial_association_delete_behaviour(seeded_test_client_rollback):
    all_projects = ents.Project.query.all()
    all_projects_with_geospatial_dims_before = (
        ents.Project.query.join(ents.project_geospatial_association).join(ents.GeospatialDim).all()
    )
    project_geospatial_associations_before = (
        db.session.query(
            ents.project_geospatial_association.c.project_id, ents.project_geospatial_association.c.geospatial_id
        )
        .select_from(ents.project_geospatial_association)
        .all()
    )
    assert len(all_projects_with_geospatial_dims_before) == 8
    assert len(project_geospatial_associations_before) == 9

    # All projects in the seed data have postcodes starting "SW", except one which has a second postcode starting "BT"
    sw_geospatial_data = ents.GeospatialDim.query.filter_by(postcode_prefix="SW").one()
    db.session.delete(sw_geospatial_data)
    db.session.flush()

    all_projects_after = ents.Project.query.all()
    all_projects_with_geospatial_dims_after = (
        ents.Project.query.join(ents.project_geospatial_association).join(ents.GeospatialDim).one()
    )
    project_geospatial_associations_after = (
        db.session.query(
            ents.project_geospatial_association.c.project_id, ents.project_geospatial_association.c.geospatial_id
        )
        .select_from(ents.project_geospatial_association)
        .one()
    )
    project_with_non_sw_postcode = (
        ents.Project.query.join(ents.project_geospatial_association)
        .join(ents.GeospatialDim)
        .filter(ents.GeospatialDim.postcode_prefix == "BT")
        .one()
    )

    # Checks none of the Projects have been deleted but the associations with geospatial_dim have changed
    assert len(all_projects) == len(all_projects_after)
    assert (
        project_with_non_sw_postcode.id
        == all_projects_with_geospatial_dims_after.id
        == project_geospatial_associations_after.project_id
    )
