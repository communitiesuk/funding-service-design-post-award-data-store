import uuid

from core.db import db
from core.db.entities import Contact, Organisation, Package


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

    org_fk_id = str(read_org.id)  # hacky as SQLite does not support UUID

    # Populate contact table (1 row), with fk looked up from single row in organisation.
    contact = Contact(
        email_address="jane@example.com",
        contact_name="Jane Doe",
        organisation_id=org_fk_id,
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

    contact_fk_id = str(read_contact.id)  # hacky as SQLite does not support UUID

    # Populate package table (1 row). Various fk ref's set to existing organisation and contact rows.
    package = Package(
        package_name="test package",
        fund_type_id="ABCD",
        organisation_id=org_fk_id,
        name_contact_id=contact_fk_id,
        project_sro_contact_id=contact_fk_id,
        cfo_contact_id=contact_fk_id,
        m_and_e_contact_id=contact_fk_id,
    )
    db.session.add(package)
    db.session.flush()
    read_package = Package.query.first()
    assert read_package.package_name == "test package"
    assert read_package.organisation.organisation_name == "Test Organisation"

    # Check parent table's row fields available as ORM attributes
    assert read_package.cfo_contact.contact_name == "Jane Doe"
    assert read_package.m_and_e_contact.organisation.geography == "Earth"
