import uuid  # noqa
from typing import List

import sqlalchemy as sqla
from sqlalchemy.orm import Mapped, class_mapper

from core import const
from core.db import db
from core.db.types import GUID


class BaseModel(db.Model):
    __abstract__ = True

    id: Mapped[int] = sqla.orm.mapped_column(
        GUID(), default=uuid.uuid4, primary_key=True
    )  # this should be UUIDType once using Postgres

    def to_dict(self):
        """Return a dictionary representation of the SQLAlchemy model object."""
        serialized = {}
        for key in self.__mapper__.c.keys():
            if key == "id" or key.endswith("_id"):
                continue
            serialized[key] = getattr(self, key)
        for rel in class_mapper(self.__class__).relationships:
            if rel.uselist:
                serialized[rel.key] = [obj.to_dict() for obj in getattr(self, rel.key)]
            else:
                serialized[rel.key] = getattr(self, rel.key).to_dict()
        return serialized


class Organisation(BaseModel):
    """Stores organisation information."""

    __tablename__ = "organisation_dim"

    organisation_name = sqla.Column(sqla.String(), nullable=False, unique=True)

    # TODO: geography needs review, field definition may change
    geography = sqla.Column(sqla.String(), nullable=True)


class Contact(BaseModel):
    """Stores contact information."""

    __tablename__ = "contact_dim"

    email_address = sqla.Column(sqla.String(), nullable=False, unique=True)
    contact_name = sqla.Column(sqla.String(), nullable=True)
    organisation_id = sqla.Column(GUID(), sqla.ForeignKey("organisation_dim.id"), nullable=False)
    telephone = sqla.Column(sqla.String(), nullable=True)

    organisation = sqla.orm.relationship("Organisation")


class Package(BaseModel):
    """Stores Package entities."""

    __tablename__ = "package_dim"

    package_id = sqla.Column(sqla.String(), nullable=False, unique=True)
    package_name = sqla.Column(sqla.String(), nullable=False, unique=True)

    # TODO: should we limit string length here, for example?
    fund_type_id = sqla.Column(sqla.String(), nullable=False)

    # TODO: Check that we need organisation directly referenced from Package SEPARATELY from the organisation
    #  lookups via each contact fk.
    organisation_id = sqla.Column(GUID(), sqla.ForeignKey("organisation_dim.id"), nullable=False)
    organisation = sqla.orm.relationship("Organisation")

    # TODO: Generic name definition in model, should we be more specific?
    name_contact_id = sqla.orm.mapped_column(GUID(), sqla.ForeignKey("contact_dim.id"), nullable=False)
    name_contact = sqla.orm.relationship("Contact", foreign_keys=[name_contact_id])

    project_sro_contact_id = sqla.orm.mapped_column(GUID(), sqla.ForeignKey("contact_dim.id"), nullable=False)
    project_sro_contact = sqla.orm.relationship(
        "Contact",
        foreign_keys=[project_sro_contact_id],
    )

    cfo_contact_id = sqla.orm.mapped_column(GUID(), sqla.ForeignKey("contact_dim.id"), nullable=False)
    cfo_contact = sqla.orm.relationship("Contact", foreign_keys=[cfo_contact_id])

    m_and_e_contact_id = sqla.orm.mapped_column(GUID(), sqla.ForeignKey("contact_dim.id"), nullable=False)
    m_and_e_contact = sqla.orm.relationship(
        "Contact",
        foreign_keys=[m_and_e_contact_id],
    )

    projects: Mapped[List["Project"]] = sqla.orm.relationship()
    progress: Mapped[List["ProjectProgress"]] = sqla.orm.relationship()


class Project(BaseModel):
    """Stores Project Entities."""

    __tablename__ = "project_dim"

    project_id = sqla.Column(sqla.String(), nullable=False, unique=True)

    # TODO: should this be unique?
    project_name = sqla.Column(sqla.String(), nullable=False)
    package_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("package_dim.id"), nullable=True)

    # TODO: Should we change this field to "Postcode" from "Address" to match example data.
    #  Should we also have both as separate fields, or assume some front-end process combines them to be
    #  stored here?
    #  Also, should it be nullable?
    address = sqla.Column(sqla.String(), nullable=False)

    # TODO: should this be a fk to organisation?
    secondary_organisation = sqla.Column(sqla.String(), nullable=True)

    project_delivery_plans: Mapped[List["ProjectDeliveryPlan"]] = sqla.orm.relationship()
    procurement_contracts: Mapped[List["Procurement"]] = sqla.orm.relationship()
    direct_funds: Mapped[List["DirectFund"]] = sqla.orm.relationship()
    capital: Mapped[List["Capital"]] = sqla.orm.relationship()
    indirect_funds_secured: Mapped[List["IndirectFundSecured"]] = sqla.orm.relationship()
    indirect_funds_unsecured: Mapped[List["IndirectFundUnsecured"]] = sqla.orm.relationship()
    outputs: Mapped[List["OutputData"]] = sqla.orm.relationship()
    outcomes: Mapped[List["OutcomeData"]] = sqla.orm.relationship()
    risks: Mapped[List["RiskRegister"]] = sqla.orm.relationship()


class ProjectDeliveryPlan(BaseModel):
    """Stores Project Delivery Plan data for projects."""

    __tablename__ = "project_delivery_plan"

    milestone = sqla.Column(sqla.String(), nullable=False)
    project_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)
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


class Procurement(BaseModel):
    """Stores Procurement data for projects."""

    __tablename__ = "procurement"

    construction_contract = sqla.Column(sqla.String(), nullable=False)
    project_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)
    start_date = sqla.Column(sqla.DateTime(), nullable=False)
    end_date = sqla.Column(sqla.DateTime(), nullable=False)
    status = sqla.Column(sqla.Enum(const.StatusEnum, name="status"), nullable=False)
    procurement_status = sqla.Column(sqla.Enum(const.ProcurementStatusEnum, name="procurement_status"), nullable=False)

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


class ProjectProgress(BaseModel):
    """Stores Project Progress answers."""

    __tablename__ = "project_progress"

    package_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("package_dim.id"), nullable=False)

    answer_1 = sqla.Column(sqla.String(), nullable=True)
    answer_2 = sqla.Column(sqla.String(), nullable=True)
    answer_3 = sqla.Column(sqla.String(), nullable=True)
    answer_4 = sqla.Column(sqla.String(), nullable=True)
    answer_5 = sqla.Column(sqla.String(), nullable=True)
    answer_6 = sqla.Column(sqla.String(), nullable=True)


class DirectFund(BaseModel):
    """Stores Direct Fund Data for projects."""

    __tablename__ = "direct_fund_data"

    project_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)
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


class Capital(BaseModel):
    """Stores Capital data for projects"""

    __tablename__ = "capital_data"

    project_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)
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


class IndirectFundSecured(BaseModel):
    """Stores Indirect Fund Secured Data for Projects."""

    __tablename__ = "indirect_fund_secured_data"

    project_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)
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


class IndirectFundUnsecured(BaseModel):
    """Stores Indirect Fund Unsecured Data for Projects."""

    __tablename__ = "indirect_fund_unsecured_data"

    project_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)
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


class OutputData(BaseModel):
    """Stores Output data for Projects."""

    __tablename__ = "output_data"

    project_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)
    start_date = sqla.Column(sqla.DateTime(), nullable=False)
    end_date = sqla.Column(sqla.DateTime(), nullable=False)

    # TODO: Should this have any extra logic, or is it totally free text?
    #  Also, should it be a field of Outputs_dim instead, or can users map different units of measurement
    #  against the same output?
    unit_of_measurement = sqla.Column(sqla.String(), nullable=False)
    state = sqla.Column(sqla.Enum(const.StateEnum, name="output_data_state"), nullable=False)
    amount = sqla.Column(sqla.Float(), nullable=False)

    output_dim_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("output_dim.id"))
    output_dim: Mapped["OutputDim"] = sqla.orm.relationship()

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
class OutputDim(BaseModel):
    """Stores dimension reference data for Outputs."""

    __tablename__ = "output_dim"

    output_name = sqla.Column(sqla.String(), nullable=False, unique=True)

    # TODO: Are these a pre-defined finite set? Should they be enum or similar?
    output_category = sqla.Column(sqla.String(), nullable=False, unique=False)


class OutcomeData(BaseModel):
    """Stores Outcome data for projects."""

    __tablename__ = "outcome_data"

    project_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)
    start_date = sqla.Column(sqla.DateTime(), nullable=False)
    end_date = sqla.Column(sqla.DateTime(), nullable=False)

    # TODO: as per comment on output
    unit_of_measurement = sqla.Column(sqla.String(), nullable=False)
    geography_indicator = sqla.Column(
        sqla.Enum(const.GeographyIndicatorEnum, name="outcome_data_geography"), nullable=False
    )
    amount = sqla.Column(sqla.Float(), nullable=False)
    state = sqla.Column(sqla.Enum(const.StateEnum, name="outcome_data_state"), nullable=False)

    outcome_dim_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("outcome_dim.id"))
    outcome_dim: Mapped["OutcomeDim"] = sqla.orm.relationship()

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
class OutcomeDim(BaseModel):
    """Stores dimension reference data for Outcomes."""

    __tablename__ = "outcome_dim"

    outcome_name = sqla.Column(sqla.String(), nullable=False, unique=True)

    # TODO: Are these a pre-defined finite set? Should they be enum or similar?
    outcome_category = sqla.Column(sqla.String(), nullable=False, unique=False)


class RiskRegister(BaseModel):
    """Stores Risk Register data for projects."""

    __tablename__ = "risk_register"

    project_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)
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
