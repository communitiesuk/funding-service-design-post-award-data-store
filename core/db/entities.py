import uuid  # noqa
from datetime import datetime
from typing import List

import sqlalchemy as sqla
from sqlalchemy import CheckConstraint
from sqlalchemy.orm import Mapped, class_mapper
from sqlalchemy.sql.operators import and_, or_

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
        for relation in class_mapper(self.__class__).relationships:
            if relation.uselist:
                serialized[relation.key] = [obj.to_dict() for obj in getattr(self, relation.key)]
            else:
                serialized[relation.key] = getattr(self, relation.key).to_dict()
        return serialized


class Submission(BaseModel):
    """Stores Submission information."""

    __tablename__ = "submission_dim"

    submission_id = sqla.Column(sqla.String(), nullable=False, unique=True)

    submission_date = sqla.Column(sqla.DateTime(), nullable=True)
    ingest_date = sqla.Column(sqla.DateTime(), nullable=False, default=datetime.now())
    reporting_period_start = sqla.Column(sqla.DateTime(), nullable=False)
    reporting_period_end = sqla.Column(sqla.DateTime(), nullable=False)
    reporting_round = sqla.Column(sqla.Integer(), nullable=False)
    submission_file = sqla.Column(sqla.LargeBinary(), nullable=True)  # not implemented yet
    submission_filename = sqla.Column(sqla.String(), nullable=True)  # not implemented yet

    projects: Mapped[List["Project"]] = sqla.orm.relationship()


class Organisation(BaseModel):
    """Stores organisation information."""

    __tablename__ = "organisation_dim"

    organisation_name = sqla.Column(sqla.String(), nullable=False, unique=True)

    # TODO: geography needs review, field definition may change
    geography = sqla.Column(sqla.String(), nullable=True)


class Programme(BaseModel):
    """Stores Programme entities."""

    __tablename__ = "programme_dim"

    programme_id = sqla.Column(sqla.String(), nullable=False, unique=True)

    programme_name = sqla.Column(sqla.String(), nullable=False, unique=True)
    fund_type_id = sqla.Column(sqla.String(), nullable=False)
    organisation_id = sqla.Column(GUID(), sqla.ForeignKey("organisation_dim.id"), nullable=False)

    organisation: Mapped["Organisation"] = sqla.orm.relationship()
    projects: Mapped[List["Project"]] = sqla.orm.relationship()
    progress_records: Mapped[List["ProgrammeProgress"]] = sqla.orm.relationship()
    place_details: Mapped[List["PlaceDetail"]] = sqla.orm.relationship()
    funding_questions: Mapped[List["FundingQuestion"]] = sqla.orm.relationship()


class ProgrammeProgress(BaseModel):
    """Stores Programme Progress entities."""

    __tablename__ = "programme_progress"

    submission_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    programme_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("programme_dim.id"), nullable=False)

    question = sqla.Column(sqla.String(), nullable=False)
    answer = sqla.Column(sqla.String(), nullable=True)

    __table_args__ = (
        sqla.Index(
            "ix_unique_programme_progress",
            "submission_id",
            "question",
            unique=True,
        ),
    )


class PlaceDetail(BaseModel):
    """Stores Place Detail entities."""

    __tablename__ = "place_detail"

    submission_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    programme_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("programme_dim.id"), nullable=False)

    question = sqla.Column(sqla.String(), nullable=False)
    answer = sqla.Column(sqla.String(), nullable=True)
    indicator = sqla.Column(sqla.String(), nullable=False)

    __table_args__ = (
        sqla.Index(
            "ix_unique_place_detail",
            "submission_id",
            "programme_id",
            "question",
            "indicator",
            unique=True,
        ),
    )


class FundingQuestion(BaseModel):
    """Stores Funding Question entities."""

    __tablename__ = "funding_question"

    submission_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    programme_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("programme_dim.id"), nullable=False)

    question = sqla.Column(sqla.String(), nullable=False)
    indicator = sqla.Column(sqla.String(), nullable=True)
    response = sqla.Column(sqla.String(), nullable=True)
    guidance_notes = sqla.Column(sqla.String(), nullable=True)

    __table_args__ = (
        sqla.Index(
            "ix_unique_funding_question",
            "submission_id",
            "programme_id",
            "question",
            "indicator",
            unique=True,
        ),
    )


class Project(BaseModel):
    """Stores Project Entities."""

    __tablename__ = "project_dim"

    project_id = sqla.Column(sqla.String(), nullable=False, unique=False)
    submission_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    programme_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("programme_dim.id"), nullable=True)

    project_name = sqla.Column(sqla.String(), nullable=False)
    primary_intervention_theme = sqla.Column(sqla.String(), nullable=False)
    location_multiplicity = sqla.Column(
        sqla.Enum(const.MultiplicityEnum, name="project_location_multiplicity"), nullable=False
    )
    locations = sqla.Column(sqla.String, nullable=False)
    gis_provided = sqla.Column(sqla.Enum(const.YesNoEnum), nullable=True)
    lat_long = sqla.Column(sqla.String, nullable=True)

    progress_records: Mapped[List["ProjectProgress"]] = sqla.orm.relationship()
    funding: Mapped[List["Funding"]] = sqla.orm.relationship()
    funding_comments: Mapped[List["FundingComment"]] = sqla.orm.relationship()
    private_investments: Mapped[List["PrivateInvestment"]] = sqla.orm.relationship()
    outputs: Mapped[List["OutputData"]] = sqla.orm.relationship()
    outcomes: Mapped[List["OutcomeData"]] = sqla.orm.relationship()
    risks: Mapped[List["RiskRegister"]] = sqla.orm.relationship()

    __table_args__ = (
        sqla.Index(
            "ix_unique_project_dim",
            "submission_id",
            "project_id",
            unique=True,
        ),
    )


class ProjectProgress(BaseModel):
    """Stores Project Progress Entities."""

    __tablename__ = "project_progress"

    submission_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    project_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)

    start_date = sqla.Column(sqla.DateTime(), nullable=False)
    end_date = sqla.Column(sqla.DateTime(), nullable=False)
    adjustment_request_status = sqla.Column(sqla.String(), nullable=False)
    delivery_status = sqla.Column(sqla.Enum(const.StatusEnum, name="project_progress_delivery_status"), nullable=False)
    delivery_rag = sqla.Column(sqla.Enum(const.RagEnum, name="project_progress_delivery_rag"), nullable=False)
    spend_rag = sqla.Column(sqla.Enum(const.RagEnum, name="project_progress_spend_rag"), nullable=False)
    risk_rag = sqla.Column(sqla.Enum(const.RagEnum, name="project_progress_risk_rag"), nullable=False)
    commentary = sqla.Column(sqla.String(), nullable=True)
    important_milestone = sqla.Column(sqla.String(), nullable=True)
    date_of_important_milestone = sqla.Column(sqla.DateTime(), nullable=True)

    __table_args__ = (
        sqla.Index(
            "ix_unique_project_progress",
            "submission_id",
            "project_id",
            unique=True,
        ),
    )


class Funding(BaseModel):
    """Stores Funding Entities."""

    __tablename__ = "funding"

    submission_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    project_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)

    funding_source_name = sqla.Column(sqla.String(), nullable=False)
    funding_source_type = sqla.Column(sqla.String(), nullable=False)
    secured = sqla.Column(sqla.Enum(const.YesNoEnum, name="funding_secured"), nullable=True)
    reporting_period = sqla.Column(sqla.String(), nullable=False)
    spend_for_reporting_period = sqla.Column(sqla.Float(), nullable=False, default=0.0)
    status = sqla.Column(sqla.Enum(const.StateEnum, name="funding_status"), nullable=True)

    __table_args__ = (
        sqla.Index(
            "ix_unique_funding",
            "submission_id",
            "project_id",
            "funding_source_name",
            "funding_source_type",
            "reporting_period",
            unique=True,
        ),
    )


class FundingComment(BaseModel):
    """Stores Funding Comment Entities."""

    __tablename__ = "funding_comment"

    submission_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    project_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)

    comment = sqla.Column(sqla.String(), nullable=False)

    __table_args__ = (
        sqla.Index(
            "ix_unique_funding_comment",
            "submission_id",
            "project_id",
            unique=True,
        ),
    )


class PrivateInvestment(BaseModel):
    """Stores Private Investment Entities."""

    __tablename__ = "private_investment"

    submission_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    project_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)

    total_project_value = sqla.Column(sqla.Float(), nullable=False)
    townsfund_funding = sqla.Column(sqla.Float(), nullable=False, default=0.0)
    private_sector_funding_required = sqla.Column(sqla.Float(), nullable=False, default=0.0)
    private_sector_funding_secured = sqla.Column(sqla.Float(), nullable=False, default=0.0)
    additional_comments = sqla.Column(sqla.String(), nullable=True)

    # Unique index for data integrity. Assumption inferred from ingest form that project should be unique per submission
    __table_args__ = (
        sqla.Index(
            "ix_unique_private_investment",
            "submission_id",
            "project_id",
            unique=True,
        ),
    )


class OutputData(BaseModel):
    """Stores Output data for Projects."""

    __tablename__ = "output_data"

    submission_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    project_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)
    output_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("output_dim.id"), nullable=False)

    start_date = sqla.Column(sqla.DateTime(), nullable=False)
    end_date = sqla.Column(sqla.DateTime(), nullable=False)
    unit_of_measurement = sqla.Column(sqla.String(), nullable=False)
    state = sqla.Column(sqla.Enum(const.StateEnum, name="output_data_state"), nullable=False)
    amount = sqla.Column(sqla.Float(), nullable=False)
    additional_information = sqla.Column(sqla.String(), nullable=True)

    output_dim: Mapped["OutputDim"] = sqla.orm.relationship()

    __table_args__ = (
        sqla.Index(
            "ix_unique_output",
            "submission_id",
            "project_id",
            "output_id",
            "start_date",
            "end_date",
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

    submission_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    programme_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("programme_dim.id"), nullable=True)
    project_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=True)
    outcome_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("outcome_dim.id"), nullable=False)

    start_date = sqla.Column(sqla.DateTime(), nullable=False)
    end_date = sqla.Column(sqla.DateTime(), nullable=False)
    unit_of_measurement = sqla.Column(sqla.String(), nullable=False)
    geography_indicator = sqla.Column(
        sqla.Enum(const.GeographyIndicatorEnum, name="outcome_data_geography"), nullable=False
    )
    amount = sqla.Column(sqla.Float(), nullable=False)
    state = sqla.Column(sqla.Enum(const.StateEnum, name="outcome_data_state"), nullable=False)
    higher_frequency = sqla.Column(sqla.String(), nullable=True)

    outcome_dim: Mapped["OutcomeDim"] = sqla.orm.relationship()

    __table_args__ = (
        # check that either programme or project id exists but not both
        CheckConstraint(
            or_(
                and_(programme_id.isnot(None), project_id.is_(None)),
                and_(programme_id.is_(None), project_id.isnot(None)),
            ),
            name="ck_outcome_data_programme_or_project_id",
        ),
        sqla.Index(
            "ix_unique_outcome",
            "submission_id",
            "project_id",
            "outcome_id",
            "start_date",
            "end_date",
            "geography_indicator",
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

    submission_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    programme_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("programme_dim.id"), nullable=True)
    project_id: Mapped[int] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=True)

    risk_name = sqla.Column(sqla.String(), nullable=False)
    risk_category = sqla.Column(sqla.String(), nullable=True)
    short_desc = sqla.Column(sqla.String(), nullable=True)
    full_desc = sqla.Column(sqla.String(), nullable=True)
    consequences = sqla.Column(sqla.String(), nullable=True)

    pre_mitigated_impact = sqla.Column(
        sqla.Enum(const.ImpactEnum, name="risk_register_pre_mitigated_impact"),
        nullable=True,
    )
    pre_mitigated_likelihood = sqla.Column(
        sqla.Enum(const.LikelihoodEnum, name="risk_register_pre_mitigated_likelihood"),
        nullable=True,
    )
    mitigations = sqla.Column(sqla.String(), nullable=True)
    post_mitigated_impact = sqla.Column(
        sqla.Enum(const.ImpactEnum, name="risk_register_post_mitigated_impact"),
        nullable=True,
    )
    post_mitigated_likelihood = sqla.Column(
        sqla.Enum(const.LikelihoodEnum, name="risk_register_post_mitigated_likelihood"), nullable=True
    )
    proximity = sqla.Column(sqla.Enum(const.ProximityEnum, name="risk_register_proximity"), nullable=True)

    risk_owner_role = sqla.Column(sqla.String(), nullable=True)
    __table_args__ = (
        # check that either programme or project id exists but not both
        CheckConstraint(
            or_(
                and_(programme_id.isnot(None), project_id.is_(None)),
                and_(programme_id.is_(None), project_id.isnot(None)),
            ),
            name="ck_risk_register_programme_or_project_id",
        ),
        sqla.Index(
            "ix_unique_risk_register",
            "submission_id",
            "programme_id",
            "project_id",
            "risk_name",
            unique=True,
        ),
    )
