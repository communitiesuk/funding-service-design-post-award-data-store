import uuid

import pytest
from sqlalchemy.exc import IntegrityError

from core.db import db
from core.db import entities as ents


def test_programme_contact_organisation(app_ctx):
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

    read_org = ents.Organisation.query.first()
    assert read_org.organisation_name == "Test Organisation"

    # Populate programme table (1 row). Various fk ref's set to existing organisation and contact rows.
    programme = ents.Programme(
        programme_id="XXXYY",
        programme_name="test programme",
        fund_type_id="ABCD",
        organisation_id=read_org.id,
    )
    db.session.add(programme)
    read_programme = ents.Programme.query.first()
    assert read_programme.programme_name == "test programme"
    assert read_programme.organisation.organisation_name == "Test Organisation"


def test_database_integrity_error(app_ctx):
    """Test that an invalid FK ref raises IntegrityError exception."""
    organisation = ents.Organisation(
        organisation_name="Test Organisation",
        geography="Earth",
    )
    db.session.add(organisation)

    programme = ents.Programme(
        programme_id="XXXYY",
        programme_name="test programme",
        fund_type_id="ABCD",
        organisation_id=uuid.uuid4(),
    )
    db.session.add(programme)
    with pytest.raises(IntegrityError):
        db.session.flush()
