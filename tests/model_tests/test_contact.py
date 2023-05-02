import uuid

from core.db import db
from core.db.entities import Contact, Organisation


def test_contact_organisation(app_ctx):
    """
    Test basic relationship structure between Contact and Organisation.

    Basic confidence check that fk relationships are looked up as expected.
    """

    organisation = Organisation(
        organisation_name="Test Organisation",
        geography="Earth",
    )
    db.session.add(organisation)
    db.session.flush()  # get the db-generated UUID without committing to session.

    read_org = Organisation.query.first()
    assert read_org.organisation_name == "Test Organisation"

    org_fk_id = str(read_org.id)  # hacky as SQLite does not support UUID

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
    assert read_contact.organisation.organisation_name == "Test Organisation"
    assert type(read_contact.id) is uuid.UUID
