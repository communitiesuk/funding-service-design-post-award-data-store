import uuid

import sqlalchemy as sqla

from core.db import db
from core.db.entities import Contact, Organisation, Package, Project


def test_package_contact_organisation(app_ctx):
    """
    Test basic relationship structure between Contact, Organisation and Package.

    Basic confidence check that fk relationships are looked up as expected.
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
    assert read_project.package.package_name == "test package"


def test_database_seed(seed_test_dataset):
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

    # TODO: extend these tests to check stuff has been added to DB. Doesn't need to be very complicated, the
    #  main part of the test is, does the database actually seed without error.
