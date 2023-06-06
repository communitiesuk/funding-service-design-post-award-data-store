import uuid  # noqa
from datetime import datetime
from typing import List

import sqlalchemy as sqla
from sqlalchemy import CheckConstraint
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped, class_mapper
from sqlalchemy.sql.operators import and_, or_

from core import const
from core.db import db
from core.db.types import GUID
from core.util import postcode_to_itl1


class BaseModel(db.Model):
    __abstract__ = True

    id: Mapped[GUID] = sqla.orm.mapped_column(
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

    projects: Mapped[List["Project"]] = sqla.orm.relationship(back_populates="submission")

    @classmethod
    def get_submissions_by_reporting_period(cls, start: datetime | None, end: datetime | None):
        """Get submissions within a specified date range.

        This class method retrieves submissions based on the provided start and end dates.
        If both start and end dates are None, it returns all submissions.
        If both start and end dates are provided, it filters submissions with reporting_period_start >= start
        and reporting_period_end <= end.
        If only the start date is provided, it filters submissions with reporting_period_start >= start.
        If only the end date is provided, it filters submissions with reporting_period_end <= end.

        :param start: The start date to filter submissions (inclusive). Can be None to exclude the start date filter.
        :param end: The end date to filter submissions (inclusive). Can be None to exclude the end date filter.
        :return: A list of submissions within the specified date range.
        """
        if not start and not end:
            submissions = cls.query.all()
        elif start and end:
            submissions = cls.query.filter(cls.reporting_period_start >= start, cls.reporting_period_end <= end).all()
        elif start:
            submissions = cls.query.filter(cls.reporting_period_start >= start).all()
        elif end:
            submissions = cls.query.filter(cls.reporting_period_end <= end).all()
        return submissions


class Organisation(BaseModel):
    """Stores organisation information."""

    __tablename__ = "organisation_dim"

    organisation_name = sqla.Column(sqla.String(), nullable=False, unique=True)

    # TODO: geography needs review, field definition may change
    geography = sqla.Column(sqla.String(), nullable=True)

    @classmethod
    def get_organisations_by_name(cls, names: list):
        """Get organisations based on a list of names.

        If no names are provided, it returns all organisations.

        :param names: A list of organisation names to filter organisations.
        :return: A list of organisations matching the provided names.
        """
        if names:
            organisations = cls.query.filter(cls.organisation_name.in_(names)).all()
        else:
            organisations = cls.query.all()
        return organisations


class Programme(BaseModel):
    """Stores Programme entities."""

    __tablename__ = "programme_dim"

    programme_id = sqla.Column(sqla.String(), nullable=False, unique=True)

    programme_name = sqla.Column(sqla.String(), nullable=False, unique=True)
    fund_type_id = sqla.Column(sqla.String(), nullable=False)
    organisation_id = sqla.Column(GUID(), sqla.ForeignKey("organisation_dim.id"), nullable=False)

    organisation: Mapped["Organisation"] = sqla.orm.relationship()
    projects: Mapped[List["Project"]] = sqla.orm.relationship()
    progress_records: Mapped[List["ProgrammeProgress"]] = sqla.orm.relationship(back_populates="programme")
    place_details: Mapped[List["PlaceDetail"]] = sqla.orm.relationship(back_populates="programme")
    funding_questions: Mapped[List["FundingQuestion"]] = sqla.orm.relationship(back_populates="programme")
    risks: Mapped[List["RiskRegister"]] = sqla.orm.relationship(back_populates="programme")

    @classmethod
    def get_programmes_by_org_and_fund_type(cls, organisation_ids: list, fund_type_ids: list) -> list["Programme"]:
        """Get programmes based on a list of organisation IDs and fund type IDs.

        If no ids are provided, it returns all programmes.

        :param organisation_ids: A list of organisation IDs to filter programmes.
        :param fund_type_ids: A list of fund type IDs to filter programmes.
        :return: A list of programmes matching the provided organisation IDs and fund type IDs.
        """
        query = cls.query

        if organisation_ids:
            query = query.filter(cls.organisation_id.in_(organisation_ids))

        if fund_type_ids:
            query = query.filter(cls.fund_type_id.in_(fund_type_ids))

        return query.all()

    @staticmethod
    def get_unique_fund_type_ids():
        return [value[0] for value in db.session.query(getattr(Programme, "fund_type_id")).distinct().all()]


class ProgrammeProgress(BaseModel):
    """Stores Programme Progress entities."""

    __tablename__ = "programme_progress"

    submission_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    programme_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("programme_dim.id"), nullable=False)

    question = sqla.Column(sqla.String(), nullable=False)
    answer = sqla.Column(sqla.String(), nullable=True)

    submission: Mapped["Submission"] = sqla.orm.relationship()
    programme: Mapped["Programme"] = sqla.orm.relationship(back_populates="progress_records")

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

    submission_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    programme_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("programme_dim.id"), nullable=False)

    question = sqla.Column(sqla.String(), nullable=False)
    answer = sqla.Column(sqla.String(), nullable=True)
    indicator = sqla.Column(sqla.String(), nullable=False)

    submission: Mapped["Submission"] = sqla.orm.relationship()
    programme: Mapped["Programme"] = sqla.orm.relationship(back_populates="place_details")

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

    submission_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    programme_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("programme_dim.id"), nullable=False)

    question = sqla.Column(sqla.String(), nullable=False)
    indicator = sqla.Column(sqla.String(), nullable=True)
    response = sqla.Column(sqla.String(), nullable=True)
    guidance_notes = sqla.Column(sqla.String(), nullable=True)

    submission: Mapped["Submission"] = sqla.orm.relationship()
    programme: Mapped["Programme"] = sqla.orm.relationship(back_populates="funding_questions")

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
    submission_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    programme_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("programme_dim.id"), nullable=True)

    project_name = sqla.Column(sqla.String(), nullable=False)
    primary_intervention_theme = sqla.Column(sqla.String(), nullable=False)
    location_multiplicity = sqla.Column(
        sqla.Enum(const.MultiplicityEnum, name="project_location_multiplicity"), nullable=False
    )
    locations = sqla.Column(sqla.String, nullable=False)
    postcodes = sqla.Column(sqla.String, nullable=True)
    gis_provided = sqla.Column(sqla.Enum(const.YesNoEnum), nullable=True)
    lat_long = sqla.Column(sqla.String, nullable=True)

    submission: Mapped["Submission"] = sqla.orm.relationship(back_populates="projects")
    progress_records: Mapped[List["ProjectProgress"]] = sqla.orm.relationship(back_populates="project")
    funding_records: Mapped[List["Funding"]] = sqla.orm.relationship(back_populates="project")
    funding_comments: Mapped[List["FundingComment"]] = sqla.orm.relationship(back_populates="project")
    private_investments: Mapped[List["PrivateInvestment"]] = sqla.orm.relationship(back_populates="project")
    outputs: Mapped[List["OutputData"]] = sqla.orm.relationship(back_populates="project")
    outcomes: Mapped[List["OutcomeData"]] = sqla.orm.relationship(back_populates="project")
    risks: Mapped[List["RiskRegister"]] = sqla.orm.relationship(back_populates="project")

    __table_args__ = (
        sqla.Index(
            "ix_unique_project_dim",
            "submission_id",
            "project_id",
            unique=True,
        ),
    )

    @hybrid_property
    def itl_regions(self):
        """Returns the set of distinct ITL regions mapped from the project's postcodes.

        :return: A set of ITL regions.
        """
        if not self.postcodes:
            return {}

        postcodes = self.postcodes.split(",")
        itl_regions = [postcode_to_itl1(postcode) for postcode in postcodes]
        distinct_regions = set(itl_regions)
        return distinct_regions

    @classmethod
    def get_project_by_programme_ids_and_submission_ids(
        cls, programme_ids: list, submission_ids: list
    ) -> list["Project"]:
        """Get projects based on a list of programme IDs and submission IDs.

        :param programme_ids: A list of programme IDs to filter projects.
        :param submission_ids: A list of submission IDs to filter projects.
        :return: A list of projects matching the provided programme IDs and submission IDs.
        """
        return cls.query.filter(and_(cls.programme_id.in_(programme_ids), cls.submission_id.in_(submission_ids))).all()


class ProjectProgress(BaseModel):
    """Stores Project Progress Entities."""

    __tablename__ = "project_progress"

    submission_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    project_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)

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

    submission: Mapped["Submission"] = sqla.orm.relationship()
    project: Mapped["Project"] = sqla.orm.relationship(back_populates="progress_records")

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

    submission_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    project_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)

    funding_source_name = sqla.Column(sqla.String(), nullable=False)
    funding_source_type = sqla.Column(sqla.String(), nullable=False)
    secured = sqla.Column(sqla.Enum(const.YesNoEnum, name="funding_secured"), nullable=True)
    start_date = sqla.Column(sqla.DateTime(), nullable=True)  # financial reporting period start
    end_date = sqla.Column(sqla.DateTime(), nullable=True)  # financial reporting period end
    spend_for_reporting_period = sqla.Column(sqla.Float(), nullable=False, default=0.0)
    status = sqla.Column(sqla.Enum(const.StateEnum, name="funding_status"), nullable=True)

    submission: Mapped["Submission"] = sqla.orm.relationship()
    project: Mapped["Project"] = sqla.orm.relationship(back_populates="funding_records")

    __table_args__ = (
        sqla.Index(
            "ix_unique_funding",
            "submission_id",
            "project_id",
            "funding_source_name",
            "funding_source_type",
            "start_date",
            "end_date",
            unique=True,
        ),
    )


class FundingComment(BaseModel):
    """Stores Funding Comment Entities."""

    __tablename__ = "funding_comment"

    submission_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    project_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)

    comment = sqla.Column(sqla.String(), nullable=False)

    submission: Mapped["Submission"] = sqla.orm.relationship()
    project: Mapped["Project"] = sqla.orm.relationship(back_populates="funding_comments")

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

    submission_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    project_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)

    total_project_value = sqla.Column(sqla.Float(), nullable=False)
    townsfund_funding = sqla.Column(sqla.Float(), nullable=False, default=0.0)
    private_sector_funding_required = sqla.Column(sqla.Float(), nullable=False, default=0.0)
    private_sector_funding_secured = sqla.Column(sqla.Float(), nullable=False, default=0.0)
    additional_comments = sqla.Column(sqla.String(), nullable=True)

    submission: Mapped["Submission"] = sqla.orm.relationship()
    project: Mapped["Project"] = sqla.orm.relationship(back_populates="private_investments")

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

    submission_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    project_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=False)
    output_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("output_dim.id"), nullable=False)

    start_date = sqla.Column(sqla.DateTime(), nullable=False)
    end_date = sqla.Column(sqla.DateTime(), nullable=True)
    unit_of_measurement = sqla.Column(sqla.String(), nullable=False)
    state = sqla.Column(sqla.Enum(const.StateEnum, name="output_data_state"), nullable=True)
    amount = sqla.Column(sqla.Float(), nullable=False, default=0.0)
    additional_information = sqla.Column(sqla.String(), nullable=True)

    submission: Mapped["Submission"] = sqla.orm.relationship()
    project: Mapped["Project"] = sqla.orm.relationship(back_populates="outputs")
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


class OutputDim(BaseModel):
    """Stores dimension reference data for Outputs."""

    __tablename__ = "output_dim"

    output_name = sqla.Column(sqla.String(), nullable=False, unique=True)

    # TODO: Are these a pre-defined finite set? Should they be enum or similar?
    output_category = sqla.Column(sqla.String(), nullable=False, unique=False)


class OutcomeData(BaseModel):
    """Stores Outcome data for projects."""

    __tablename__ = "outcome_data"

    submission_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    programme_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("programme_dim.id"), nullable=True)
    project_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=True)
    outcome_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("outcome_dim.id"), nullable=False)

    start_date = sqla.Column(sqla.DateTime(), nullable=False)
    end_date = sqla.Column(sqla.DateTime(), nullable=False)
    unit_of_measurement = sqla.Column(sqla.String(), nullable=False)
    geography_indicator = sqla.Column(
        sqla.Enum(const.GeographyIndicatorEnum, name="outcome_data_geography"), nullable=False
    )
    amount = sqla.Column(sqla.Float(), nullable=False)
    state = sqla.Column(sqla.Enum(const.StateEnum, name="outcome_data_state"), nullable=False)
    higher_frequency = sqla.Column(sqla.String(), nullable=True)

    submission: Mapped["Submission"] = sqla.orm.relationship()
    project: Mapped["Project"] = sqla.orm.relationship(back_populates="outcomes")
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

    @classmethod
    def get_outcomes_by_project_ids_and_categories(cls, project_ids: list, categories: list):
        """Get outcomes based on a list of project IDs and outcome categories.

        :param project_ids: A list of project IDs to filter outcomes.
        :param categories: A list of outcome categories to filter outcomes.
        :return: A list of outcomes matching the provided project IDs and outcome categories.
        """
        outcomes = cls.query.filter(
            cls.project_id.in_(project_ids),
            cls.outcome_dim.has(OutcomeDim.outcome_category.in_(categories) if categories else None),
        ).all()
        return outcomes


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

    submission_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("submission_dim.id"), nullable=False)
    programme_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("programme_dim.id"), nullable=True)
    project_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("project_dim.id"), nullable=True)

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

    submission: Mapped["Submission"] = sqla.orm.relationship()
    project: Mapped["Project"] = sqla.orm.relationship(back_populates="risks")
    programme: Mapped["Programme"] = sqla.orm.relationship(back_populates="risks")

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
