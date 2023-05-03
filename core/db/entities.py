import uuid  # noqa

import sqlalchemy as sqla

from core.db import db
from core.db.types import GUID


class Organisation(db.Model):
    """Stores organisation information."""

    __tablename__ = "organisation_dim"

    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres
    organisation_name = sqla.Column(sqla.String, nullable=False, unique=True)
    # TODO: geography needs review, field definition may change
    geography = sqla.Column(sqla.String, nullable=True)

    contacts = sqla.orm.relationship("Contact", back_populates="organisation")
    packages = sqla.orm.relationship("Package", back_populates="organisation")


class Contact(db.Model):
    """Stores contact information."""

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

    name_packages = sqla.orm.relationship(
        "Package", back_populates="name_contact", foreign_keys="Package.name_contact_id"
    )
    project_sro_packages = sqla.orm.relationship(
        "Package",
        back_populates="project_sro_contact",
        foreign_keys="Package.project_sro_contact_id",
    )
    cfo_packages = sqla.orm.relationship("Package", back_populates="cfo_contact", foreign_keys="Package.cfo_contact_id")
    m_and_e_packages = sqla.orm.relationship(
        "Package",
        back_populates="m_and_e_contact",
        foreign_keys="Package.m_and_e_contact_id",
    )


class Package(db.Model):
    """Stores Package entities."""

    __tablename__ = "package_dim"

    id = sqla.Column(
        GUID(),  # this should be UUIDType once using Postgres
        default=uuid.uuid4,
        primary_key=True,
    )
    package_name = sqla.Column(sqla.String, nullable=False, unique=True)
    # TODO: should we limit string length here?
    fund_type_id = sqla.Column(sqla.String, nullable=False)
    # TODO: Check that we need organisation directly referenced from Package SEPARATELY from the organisation
    #  lookups via each contact fk.
    organisation_id = sqla.Column(
        sqla.String,
        sqla.ForeignKey("organisation_dim.id"),
        nullable=False,
    )
    # TODO: Generic name definition in model, should we be more specific?
    name_contact_id = sqla.Column(
        sqla.String,
        sqla.ForeignKey("contact_dim.id"),
        nullable=False,
    )
    project_sro_contact_id = sqla.Column(
        sqla.String,
        sqla.ForeignKey("contact_dim.id"),
        nullable=False,
    )
    cfo_contact_id = sqla.Column(
        sqla.String,
        sqla.ForeignKey("contact_dim.id"),
        nullable=False,
    )
    m_and_e_contact_id = sqla.Column(
        sqla.String,
        sqla.ForeignKey("contact_dim.id"),
        nullable=False,
    )

    organisation = sqla.orm.relationship("Organisation", back_populates="packages")
    name_contact = sqla.orm.relationship("Contact", back_populates="name_packages", foreign_keys=[name_contact_id])
    project_sro_contact = sqla.orm.relationship(
        "Contact",
        back_populates="project_sro_packages",
        foreign_keys=[project_sro_contact_id],
    )
    cfo_contact = sqla.orm.relationship("Contact", back_populates="cfo_packages", foreign_keys=[cfo_contact_id])
    m_and_e_contact = sqla.orm.relationship(
        "Contact", back_populates="m_and_e_packages", foreign_keys=[m_and_e_contact_id]
    )


class ProjectProgress(db.Model):
    """Stores Project Progress answers."""

    __tablename__ = "project_progress"

    id = sqla.Column(
        GUID(),  # this should be UUIDType once using Postgres
        default=uuid.uuid4,
        primary_key=True,
    )

    package_id = sqla.Column(
        sqla.String,
        sqla.ForeignKey("package_dim.id"),
        nullable=False,
    )

    answer_1 = sqla.Column(
        sqla.String,
        nullable=True,
    )
    answer_2 = sqla.Column(
        sqla.String,
        nullable=True,
    )
    answer_3 = sqla.Column(
        sqla.String,
        nullable=True,
    )
    answer_4 = sqla.Column(
        sqla.String,
        nullable=True,
    )
    answer_5 = sqla.Column(
        sqla.String,
        nullable=True,
    )
    answer_6 = sqla.Column(
        sqla.String,
        nullable=True,
    )
