import uuid

import pytest
import sqlalchemy as sqla
from sqlalchemy.exc import IntegrityError

from core.db import db
from core.db.entities import Contact, Organisation, Package, Project


def test_package_contact_organisation(app_ctx):
    """
    Test basic relationship structure between Contact, Organisation and Package.

    Basic confidence check that data can be inserted and FK relations are as expected.
    """

    # Populate organisation table (1 row)
    organisation = Organisation(
        organisation_name="Test Organisation",
        geography="Earth",
    )
    db.session.add(organisation)
    db.session.flush()  # get the db-generated UUID without committing to session.

    read_org = Organisation.query.first()
    assert read_org.organisation_name == "Test Organisation"

    # Populate contact table (1 row), with fk looked up from single row in organisation.
    contact = Contact(
        email_address="jane@example.com",
        contact_name="Jane Doe",
        organisation_id=read_org.id,
        telephone="123",
    )
    db.session.add(contact)
    db.session.flush()

    read_contact = Contact.query.first()
    assert read_contact.email_address == "jane@example.com"
    assert read_contact.contact_name == "Jane Doe"
    # Check parent table's row fields available as ORM attributes
    assert read_contact.organisation.organisation_name == "Test Organisation"
    assert type(read_contact.id) is uuid.UUID

    # Populate package table (1 row). Various fk ref's set to existing organisation and contact rows.
    package = Package(
        package_name="test package",
        package_id="XXXYY",
        fund_type_id="ABCD",
        organisation_id=read_org.id,
        name_contact_id=read_contact.id,
        project_sro_contact_id=read_contact.id,
        cfo_contact_id=read_contact.id,
        m_and_e_contact_id=read_contact.id,
    )
    db.session.add(package)
    db.session.flush()
    read_package = Package.query.first()
    assert read_package.package_name == "test package"
    assert read_package.organisation.organisation_name == "Test Organisation"

    # Check parent table's row fields available as ORM attributes
    assert read_package.cfo_contact.contact_name == "Jane Doe"
    assert read_package.m_and_e_contact.organisation.geography == "Earth"

    project = Project(
        project_id="ABCDE",
        project_name="fake project",
        address="XX2 2YY",
        secondary_organisation="another fake org.",
        package_id=read_package.id,
    )
    db.session.add(project)
    db.session.flush()
    read_project = Project.query.first()
    assert read_project.project_name == "fake project"


def test_database_seed(seeded_app_ctx):
    """Tests the basic structure of seeded data looks correct."""
    read_org = Organisation.query.first()
    assert read_org.organisation_name == "Test Organisation"

    read_contact = Contact.query.first()
    assert read_contact.email_address == "jane@example.com"
    assert read_contact.contact_name == "Jane Doe"

    # Check parent table's row fields available as ORM attributes
    assert read_contact.organisation.organisation_name == "Test Organisation"

    # Check parent table's row fields available with standard SELECT method
    stmt = sqla.select(Organisation).where(Organisation.id == read_contact.organisation_id)
    parent_org_name = str(db.session.scalars(stmt).first().organisation_name)
    assert parent_org_name == "Test Organisation"

    read_package = Package.query.first()
    assert read_package.package_name == "Regeneration Project"
    assert read_package.fund_type_id == "HIJ"
    assert read_package.organisation_id == read_org.id
    assert read_package.cfo_contact_id == read_contact.id
    assert read_package.cfo_contact.organisation.organisation_name == "Test Organisation"


def test_database_integrity_error(app_ctx):
    """Test that an invalid FK ref raises IntegrityError exception."""
    organisation = Organisation(
        organisation_name="Test Organisation",
        geography="Earth",
    )
    db.session.add(organisation)

    contact = Contact(
        email_address="jane@example.com",
        contact_name="Jane Doe",
        organisation_id=uuid.uuid4(),
        telephone="123",
    )
    db.session.add(contact)
    with pytest.raises(IntegrityError):
        db.session.flush()
