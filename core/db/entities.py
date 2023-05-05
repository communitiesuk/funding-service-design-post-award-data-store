import uuid  # noqa

import sqlalchemy as sqla

from core import const
from core.db import db
from core.db.types import GUID


class Organisation(db.Model):
    """Stores organisation information."""

    __tablename__ = "organisation_dim"

    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres
    organisation_name = sqla.Column(sqla.String(), nullable=False, unique=True)

    # TODO: geography needs review, field definition may change
    geography = sqla.Column(sqla.String(), nullable=True)

    contacts = sqla.orm.relationship("Contact", back_populates="organisation")
    packages = sqla.orm.relationship("Package", back_populates="organisation")


class Contact(db.Model):
    """Stores contact information."""

    __tablename__ = "contact_dim"

    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres
    email_address = sqla.Column(sqla.String(), nullable=False, unique=True)
    contact_name = sqla.Column(sqla.String(), nullable=True)
    organisation_id = sqla.Column(sqla.String(), sqla.ForeignKey("organisation_dim.id"), nullable=False)
    telephone = sqla.Column(sqla.String(), nullable=True)

    organisation = sqla.orm.relationship("Organisation", back_populates="contacts")

    name_packages = sqla.orm.relationship(
        "Package", back_populates="name_contact", foreign_keys="Package.name_contact_id"
    )
    project_sro_packages = sqla.orm.relationship(
        "Package", back_populates="project_sro_contact", foreign_keys="Package.project_sro_contact_id"
    )
    cfo_packages = sqla.orm.relationship("Package", back_populates="cfo_contact", foreign_keys="Package.cfo_contact_id")
    m_and_e_packages = sqla.orm.relationship(
        "Package", back_populates="m_and_e_contact", foreign_keys="Package.m_and_e_contact_id"
    )


class Package(db.Model):
    """Stores Package entities."""

    __tablename__ = "package_dim"

    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres
    package_id = sqla.Column(sqla.String(), nullable=False, unique=True)
    package_name = sqla.Column(sqla.String(), nullable=False, unique=True)

    # TODO: should we limit string length here, for example?
    fund_type_id = sqla.Column(sqla.String(), nullable=False)

    # TODO: Check that we need organisation directly referenced from Package SEPARATELY from the organisation
    #  lookups via each contact fk.
    organisation_id = sqla.Column(sqla.String(), sqla.ForeignKey("organisation_dim.id"), nullable=False)

    # TODO: Generic name definition in model, should we be more specific?
    name_contact_id = sqla.Column(sqla.String(), sqla.ForeignKey("contact_dim.id"), nullable=False)
    project_sro_contact_id = sqla.Column(sqla.String(), sqla.ForeignKey("contact_dim.id"), nullable=False)
    cfo_contact_id = sqla.Column(sqla.String(), sqla.ForeignKey("contact_dim.id"), nullable=False)
    m_and_e_contact_id = sqla.Column(sqla.String(), sqla.ForeignKey("contact_dim.id"), nullable=False)

    organisation = sqla.orm.relationship("Organisation", back_populates="packages")
    name_contact = sqla.orm.relationship("Contact", back_populates="name_packages", foreign_keys=[name_contact_id])
    project_sro_contact = sqla.orm.relationship(
        "Contact",
        back_populates="project_sro_packages",
        foreign_keys=[project_sro_contact_id],
    )
    cfo_contact = sqla.orm.relationship("Contact", back_populates="cfo_packages", foreign_keys=[cfo_contact_id])
    m_and_e_contact = sqla.orm.relationship(
        "Contact",
        back_populates="m_and_e_packages",
        foreign_keys=[m_and_e_contact_id],
    )

    projects = sqla.orm.relationship("Project", back_populates="package")


class Project(db.Model):
    """Stores Project Entities."""

    __tablename__ = "project_dim"

    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres
    project_id = sqla.Column(sqla.String(), nullable=False, unique=True)

    # TODO: should this be unique?
    project_name = sqla.Column(sqla.String(), nullable=False)
    package_id = sqla.Column(sqla.String(), sqla.ForeignKey("package_dim.id"), nullable=True)

    # TODO: Should we change this field to "Postcode" from "Address" to match example data.
    #  Should we also have both as separate fields, or assume some front-end process combines them to be
    #  stored here?
    #  Also, should it be nullable?
    address = sqla.Column(sqla.String(), nullable=False)

    # TODO: should this be a fk to organisation?
    secondary_organisation = sqla.Column(sqla.String(), nullable=True)

    package = sqla.orm.relationship("Package", back_populates="projects")


class ProjectDeliveryPlan(db.Model):
    """Stores Project Delivery Plan data for projects."""

    __tablename__ = "project_delivery_plan"

    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres
    milestone = sqla.Column(sqla.String(), nullable=False)
    project_id = sqla.Column(sqla.String(), sqla.ForeignKey("project_dim.id"), nullable=False)
    start_date = sqla.Column(sqla.DateTime(), nullable=False)
    end_date = sqla.Column(sqla.DateTime(), nullable=False)
    status = sqla.Column(sqla.Enum(const.StatusEnum, name="project_delivery_plan_status"), nullable=False)

    # TODO: Should this be nullable? Is Status alone enough in some circumstances?
    comments = sqla.Column(sqla.String(), nullable=False)

    # TODO: does this unique index look right?
    # Unique index for data integrity.
    __table_args__ = (
        sqla.Index(
            "ix_unique_project_delivery_plan",
            "milestone",
            "project_id",
            unique=True,
        ),
    )


class Procurement(db.Model):
    """Stores Procurement data for projects."""

    __tablename__ = "procurement"

    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres

    construction_contract = sqla.Column(sqla.String(), nullable=False)
    project_id = sqla.Column(sqla.String(), sqla.ForeignKey("project_dim.id"), nullable=False)
    start_date = sqla.Column(sqla.DateTime(), nullable=False)
    end_date = sqla.Column(sqla.DateTime(), nullable=False)
    status = sqla.Column(sqla.Enum(const.StatusEnum, name="procurement_plan_status"), nullable=False)

    # TODO: Should this be nullable? Is Status alone enough in some circumstances?
    comments = sqla.Column(sqla.String(), nullable=False)

    # TODO: does this unique index look right?
    # Unique index for data integrity.
    __table_args__ = (
        sqla.Index(
            "ix_unique_procurement",
            "construction_contract",
            "project_id",
            unique=True,
        ),
    )


class ProjectProgress(db.Model):
    """Stores Project Progress answers."""

    __tablename__ = "project_progress"

    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres
    package_id = sqla.Column(sqla.String(), sqla.ForeignKey("package_dim.id"), nullable=False)
    answer_1 = sqla.Column(sqla.String(), nullable=True)
    answer_2 = sqla.Column(sqla.String(), nullable=True)
    answer_3 = sqla.Column(sqla.String(), nullable=True)
    answer_4 = sqla.Column(sqla.String(), nullable=True)
    answer_5 = sqla.Column(sqla.String(), nullable=True)
    answer_6 = sqla.Column(sqla.String(), nullable=True)


class DirectFund(db.Model):
    """Stores Direct Fund Data for projects."""

    __tablename__ = "direct_fund_data"

    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres
    project_id = sqla.Column(sqla.String(), sqla.ForeignKey("project_dim.id"), nullable=False)
    start_date = sqla.Column(sqla.DateTime(), nullable=False)
    end_date = sqla.Column(sqla.DateTime(), nullable=False)
    state = sqla.Column(sqla.Enum(const.StateEnum, name="direct_fund_state"), nullable=False)
    pra_or_other = sqla.Column(sqla.Enum(const.PRAEnum, name="direct_fund_pra"), nullable=False)
    amount = sqla.Column(sqla.Float(), nullable=False)

    # TODO: should we add a constraint to set this <= amount?
    contractually_committed_amount = sqla.Column(sqla.Float(), nullable=False)

    # TODO: does this unique index look right?
    # Unique index for data integrity. There can't be multiple direct fund rows for a single project with
    # the same date range and direct fund metrics.
    __table_args__ = (
        sqla.Index(
            "ix_unique_direct_fund",
            "project_id",
            "start_date",
            "end_date",
            "state",
            "pra_or_other",
            unique=True,
        ),
    )


class Capital(db.Model):
    """Stores Capital data for projects"""

    __tablename__ = "capital_data"

    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres
    project_id = sqla.Column(sqla.String(), sqla.ForeignKey("project_dim.id"), nullable=False)
    start_date = sqla.Column(sqla.DateTime(), nullable=False)
    end_date = sqla.Column(sqla.DateTime(), nullable=False)
    state = sqla.Column(sqla.Enum(const.StateEnum, name="capital_state"), nullable=False)
    amount = sqla.Column(sqla.Float(), nullable=False)

    # TODO: does this unique index look right?
    # Unique index for data integrity. There can't be multiple capital data rows for a single project with
    # the same date range and capital metrics.
    __table_args__ = (
        sqla.Index(
            "ix_unique_capital",
            "project_id",
            "start_date",
            "end_date",
            "state",
            unique=True,
        ),
    )


class IndirectFundSecured(db.Model):
    """Stores Indirect Fund Secured Data for Projects."""

    __tablename__ = "indirect_fund_secured_data"

    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres
    project_id = sqla.Column(sqla.String(), sqla.ForeignKey("project_dim.id"), nullable=False)
    start_date = sqla.Column(sqla.DateTime(), nullable=False)
    end_date = sqla.Column(sqla.DateTime(), nullable=False)

    # TODO: Should this reference entities in organisation model, or is it free-text
    funding_source_name = sqla.Column(sqla.String(), nullable=False)
    funding_source_category = sqla.Column(
        sqla.Enum(const.FundingSourceCategoryEnum, name="indirect_fund_secured_source_category"),
        nullable=False,
    )
    state = sqla.Column(sqla.Enum(const.StateEnum, name="indirect_fund_secured_state"), nullable=False)
    amount = sqla.Column(sqla.Float(), nullable=False)

    # TODO: does this unique index look right?
    # Unique index for data integrity. There can't be multiple indirect fund secured rows for a single project with
    # the same date range and fund metrics.
    __table_args__ = (
        sqla.Index(
            "ix_unique_indirect_fund_secured",
            "project_id",
            "start_date",
            "end_date",
            "funding_source_name",
            "state",
            unique=True,
        ),
    )


class IndirectFundUnsecured(db.Model):
    """Stores Indirect Fund Unsecured Data for Projects."""

    __tablename__ = "indirect_fund_unsecured_data"
    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres
    project_id = sqla.Column(sqla.String(), sqla.ForeignKey("project_dim.id"), nullable=False)
    start_date = sqla.Column(sqla.DateTime(), nullable=False)
    end_date = sqla.Column(sqla.DateTime(), nullable=False)

    # TODO: Should this reference entities in organisation model, or is it free-text
    funding_source_name = sqla.Column(sqla.String(), nullable=False)
    funding_source_category = sqla.Column(
        sqla.Enum(const.FundingSourceCategoryEnum, name="indirect_fund_unsecured_source_category"),
        nullable=False,
    )
    state = sqla.Column(sqla.Enum(const.StateEnum, name="indirect_fund_unsecured_state"), nullable=False)
    amount = sqla.Column(sqla.Float(), nullable=False)

    # TODO: assumed to be String / free-text. Should this be Enum? If so, what is the definition?
    current_status = sqla.Column(sqla.String(), nullable=True)
    comments = sqla.Column(sqla.String(), nullable=True)
    potential_secure_date = sqla.Column(sqla.DateTime(), nullable=True)

    # TODO: does this unique index look right?
    # Unique index for data integrity. There can't be multiple indirect fund unsecured rows for a single project with
    # the same date range and fund metrics.
    __table_args__ = (
        sqla.Index(
            "ix_unique_indirect_fund_unsecured",
            "project_id",
            "start_date",
            "end_date",
            "funding_source_name",
            "state",
            unique=True,
        ),
    )


class OutputData(db.Model):
    """Stores Output data for Projects."""

    __tablename__ = "output_data"

    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres
    project_id = sqla.Column(sqla.String(), sqla.ForeignKey("project_dim.id"), nullable=False)
    start_date = sqla.Column(sqla.DateTime(), nullable=False)
    end_date = sqla.Column(sqla.DateTime(), nullable=False)
    output_dim_id = sqla.Column(sqla.ForeignKey("output_dim.id"), nullable=False)
    # TODO: Should this have any extra logic, or is it totally free text?
    #  Also, should it be a field of Outputs_dim instead, or can users map different units of measurement
    #  against the same output?
    unit_of_measurement = sqla.Column(sqla.String(), nullable=False)
    state = sqla.Column(sqla.Enum(const.StateEnum, name="output_data_state"), nullable=False)
    amount = sqla.Column(sqla.Float(), nullable=False)

    output_dim = sqla.orm.relationship("OutputDim", back_populates="outputs")

    # TODO: does this unique index look right?
    # Unique index for data integrity. There can't be multiple outputs for a single project with
    # the same date range and output metrics.
    __table_args__ = (
        sqla.Index(
            "ix_unique_output",
            "project_id",
            "start_date",
            "end_date",
            "output_dim_id",
            "unit_of_measurement",
            "state",
            unique=True,
        ),
    )


# TODO: How do we propose to populate this table? As from test data examples it looks like pre-populated ref
#  data. We could
#  1) leave as it is, and seed the DB upon init - there could then be an option for users to dynamically
#     add new fileds if required
#  2) Have as pre-defined hard-coded structure, such as enum. User needs knowledge of available option
#  3) Init as empty table, must be entirely populated by spreadsheet ingest.
class OutputDim(db.Model):
    """Stores dimension reference data for Outputs."""

    __tablename__ = "output_dim"

    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres
    output_name = sqla.Column(sqla.String(), nullable=False, unique=True)

    # TODO: Are these a pre-defined finite set? Should they be enum or similar?
    output_category = sqla.Column(sqla.String(), nullable=False, unique=False)

    outputs = sqla.orm.relationship("OutputData", back_populates="output_dim")


class OutcomeData(db.Model):
    """Stores Outcome data for projects."""

    __tablename__ = "outcome_data"

    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres
    project_id = sqla.Column(sqla.String(), sqla.ForeignKey("project_dim.id"), nullable=False)
    start_date = sqla.Column(sqla.DateTime(), nullable=False)
    end_date = sqla.Column(sqla.DateTime(), nullable=False)
    outcome_dim_id = sqla.Column(sqla.ForeignKey("outcome_dim.id"), nullable=False)

    # TODO: as per comment on output
    unit_of_measurement = sqla.Column(sqla.String(), nullable=False)
    geography_indicator = sqla.Column(
        sqla.Enum(const.GeographyIndicatorEnum, name="outcome_data_geography"), nullable=False
    )
    amount = sqla.Column(sqla.Float(), nullable=False)
    state = sqla.Column(sqla.Enum(const.StateEnum, name="outcome_data_state"), nullable=False)

    outcome_dim = sqla.orm.relationship("OutcomeDim", back_populates="outcomes")

    # TODO: does this unique index look right?
    # Unique index for data integrity. There can't be multiple outcomes for a single project with
    # the same date range and outcome metrics.
    __table_args__ = (
        sqla.Index(
            "ix_unique_outcome",
            "project_id",
            "start_date",
            "end_date",
            "outcome_dim_id",
            "unit_of_measurement",
            "state",
            unique=True,
        ),
    )


# TODO: similar population question as per OutputData
class OutcomeDim(db.Model):
    """Stores dimension reference data for Outcomes."""

    __tablename__ = "outcome_dim"

    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres
    outcome_name = sqla.Column(sqla.String(), nullable=False, unique=True)

    # TODO: Are these a pre-defined finite set? Should they be enum or similar?
    outcome_category = sqla.Column(sqla.String(), nullable=False, unique=False)

    outcomes = sqla.orm.relationship("OutcomeData", back_populates="outcome_dim")


class RiskRegister(db.Model):
    """Stores Risk Register data for projects."""

    __tablename__ = "risk_register"

    id = sqla.Column(GUID(), default=uuid.uuid4, primary_key=True)  # this should be UUIDType once using Postgres

    project_id = sqla.Column(sqla.String(), sqla.ForeignKey("project_dim.id"), nullable=False)
    risk_name = sqla.Column(sqla.String(), nullable=False)

    # TODO: Should this be an enum or is just free text?
    risk_category = sqla.Column(sqla.String(), nullable=False)

    # TODO: Are any of these nullable?
    short_desc = sqla.Column(sqla.String(), nullable=False)
    full_desc = sqla.Column(sqla.String(), nullable=False)
    consequences = sqla.Column(sqla.String(), nullable=False)

    pre_mitigated_impact = sqla.Column(sqla.Enum(const.ImpactEnum, name="risk_register_pre_mitigated_impact"))
    pre_mitigated_likelihood = sqla.Column(
        sqla.Enum(const.LikelihoodEnum, name="risk_register_pre_mitigated_likelihood")
    )
    mitigations = sqla.Column(sqla.String(), nullable=False)
    post_mitigated_impact = sqla.Column(sqla.Enum(const.ImpactEnum, name="risk_register_post_mitigated_impact"))
    post_mitigated_likelihood = sqla.Column(
        sqla.Enum(const.LikelihoodEnum, name="risk_register_post_mitigated_likelihood")
    )
    proximity = sqla.Column(sqla.Enum(const.ProximityEnum, name="risk_register_proximity"))

    # TODO: Should this reference contact? Contact does not have a "role" field
    risk_owner_role = sqla.Column(sqla.String(), nullable=False)

    # TODO: does this unique index look right?
    # Unique index for data integrity.
    __table_args__ = (
        sqla.Index(
            "ix_unique_risk_register",
            "project_id",
            "risk_name",
            unique=True,
        ),
    )
