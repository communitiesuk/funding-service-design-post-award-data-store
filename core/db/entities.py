import uuid  # noqa

import sqlalchemy as sqla

from core.db import db
from core.db.types import GUID


class Organisation(db.Model):
    __tablename__ = "organisation_dim"

    id = sqla.Column(
        GUID(), default=uuid.uuid4, primary_key=True
    )  # this should be UUIDType once using Postgres
    organisation_name = sqla.Column(sqla.String, nullable=False, unique=True)
    # TODO: geography needs review, field definition may change
    geography = sqla.Column(sqla.String, nullable=True)

    contacts = sqla.orm.relationship("Contact", back_populates="organisation")


class Contact(db.Model):
    __tablename__ = "contact_dim"

    id = sqla.Column(
        GUID(),  # this should be UUIDType once using Postgres
        default=uuid.uuid4,
        primary_key=True,
    )
    email_address = sqla.Column(sqla.String, nullable=False, unique=True)
    contact_name = sqla.Column(sqla.String, nullable=True)
    organisation_id = sqla.Column(
        sqla.String,
        sqla.ForeignKey("organisation_dim.id"),
        nullable=False,
    )
    telephone = sqla.Column(sqla.String, nullable=True)

    organisation = sqla.orm.relationship("Organisation", back_populates="contacts")
