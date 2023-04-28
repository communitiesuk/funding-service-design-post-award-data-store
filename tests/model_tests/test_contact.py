import uuid

from core.db import db
from core.db.entities import Contact


def test_contact(app_ctx):
    contact = Contact(
        email_address="jane@example.com",
        contact_name="Jane Doe",
        organisation="ACME",
        telephone="123",
    )
    db.session.add(contact)
    db.session.commit()

    read_contact = Contact.query.first()
    assert read_contact.email_address == "jane@example.com"
    assert read_contact.contact_name == "Jane Doe"
    assert read_contact.organisation == "ACME"
    assert read_contact.telephone == "123"
    assert type(read_contact.id) is uuid.UUID
