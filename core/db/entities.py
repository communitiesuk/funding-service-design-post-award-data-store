import uuid  # noqa
from datetime import datetime
from typing import List

import sqlalchemy as sqla
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.operators import and_, or_

from core.db import db
from core.db.types import GUID
from core.util import get_itl_regions_from_postcodes


class BaseModel(db.Model):
    __abstract__ = True

    id: Mapped[GUID] = sqla.orm.mapped_column(GUID(), default=uuid.uuid4, primary_key=True)


class Submission(BaseModel):
    """Stores Submission information."""

    __tablename__ = "submission_dim"

    submission_id = sqla.Column(sqla.String(), nullable=False, unique=True)

    submission_date = sqla.Column(sqla.DateTime(), nullable=True)
    ingest_date = sqla.Column(sqla.DateTime(), nullable=False, default=datetime.now())
    reporting_period_start = sqla.Column(sqla.DateTime(), nullable=False)
    reporting_period_end = sqla.Column(sqla.DateTime(), nullable=False)
    reporting_round = sqla.Column(sqla.Integer(), nullable=False)
    submission_file = sqla.Column(sqla.LargeBinary(), nullable=True)
    submission_filename = sqla.Column(sqla.String(), nullable=True)

    programme_junction: Mapped["ProgrammeJunction"] = sqla.orm.relationship(back_populates="submission")

    __table_args__ = (
        sqla.Index(
            "ix_submission_filter_start_date",
            "reporting_period_start",
        ),
        sqla.Index(
            "ix_submission_filter_end_date",
            "reporting_period_end",
        ),
    )

    @hybrid_property
    def submission_number(self) -> int:
        """Extracts the submission number from the submission ID.

        SubmissionIDs are in the format "S-RXX-X" where the final section is the submission number.

        :return: submission number
        """
        return int(self.submission_id.split("-")[2])


class Organisation(BaseModel):
    """Stores organisation information."""

    __tablename__ = "organisation_dim"

    organisation_name = sqla.Column(sqla.String(), nullable=False, unique=True)
    # TODO: geography needs review, field definition may change
    geography = sqla.Column(sqla.String(), nullable=True)

    programmes: Mapped[List["Programme"]] = sqla.orm.relationship(back_populates="organisation")


class Programme(BaseModel):
    """Stores Programme entities."""

    __tablename__ = "programme_dim"

    programme_id = sqla.Column(sqla.String(), nullable=False, unique=True)

    programme_name = sqla.Column(sqla.String(), nullable=False)
    fund_type_id = sqla.Column(sqla.String(), nullable=False)
    organisation_id = sqla.Column(GUID(), sqla.ForeignKey("organisation_dim.id"), nullable=False)

    organisation: Mapped["Organisation"] = sqla.orm.relationship(back_populates="programmes")
    in_round_programmes: Mapped["ProgrammeJunction"] = sqla.orm.relationship(back_populates="programme_ref")

    __table_args__ = (
        sqla.Index(
            "ix_unique_programme_name_per_fund",
            "programme_name",
            "fund_type_id",
            unique=True,
        ),
        sqla.Index(
            "ix_programme_filter_fund_type",
            "fund_type_id",
        ),
        sqla.Index(
            "ix_programme_join_organisation",
            "organisation_id",
        ),
    )


class ProgrammeJunction(BaseModel):
    """
    Representation of a "programme" entity within a unique returns round/fund combination.

    Links persisted Programme data to in-round reference data for Projects, and Programme level "event" data.
    """

    __tablename__ = "programme_junction"

    submission_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("submission_dim.id", ondelete="CASCADE"), nullable=False
    )
    programme_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("programme_dim.id"), nullable=False)

    # parent relationships
    submission: Mapped["Submission"] = sqla.orm.relationship(back_populates="programme_junction", single_parent=True)
    programme_ref: Mapped["Programme"] = sqla.orm.relationship(back_populates="in_round_programmes")

    # child relationships
    projects: Mapped[List["Project"]] = sqla.orm.relationship(back_populates="programme_junction")
    progress_records: Mapped[List["ProgrammeProgress"]] = sqla.orm.relationship(back_populates="programme_junction")
    place_details: Mapped[List["PlaceDetail"]] = sqla.orm.relationship(back_populates="programme_junction")
    funding_questions: Mapped[List["FundingQuestion"]] = sqla.orm.relationship(back_populates="programme_junction")
    outcomes: Mapped[List["OutcomeData"]] = sqla.orm.relationship(back_populates="programme_junction")
    risks: Mapped[List["RiskRegister"]] = sqla.orm.relationship(back_populates="programme_junction")

    __table_args__ = (
        sqla.UniqueConstraint("submission_id"),  # unique index to ensure mapping cardinality is 1:1
        sqla.Index(  # TODO: Check if we need this separately from unique constraint above
            "ix_programme_junction_join_submission",
            "submission_id",
        ),
        sqla.Index(
            "ix_programme_junction_join_programme",
            "programme_id",
        ),
    )


class ProgrammeProgress(BaseModel):
    """Stores Programme Progress entities."""

    __tablename__ = "programme_progress"

    programme_junction_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("programme_junction.id", ondelete="CASCADE"), nullable=False
    )

    question = sqla.Column(sqla.String(), nullable=False)
    answer = sqla.Column(sqla.String(), nullable=True)

    programme_junction: Mapped["ProgrammeJunction"] = sqla.orm.relationship(back_populates="progress_records")

    __table_args__ = (
        sqla.Index(
            "ix_unique_programme_progress_per_submission",
            "programme_junction_id",
            "question",
            unique=True,
        ),
        sqla.Index(
            "ix_programme_progress_join_programme_junction",
            "programme_junction_id",
        ),
    )


class PlaceDetail(BaseModel):
    """Stores Place Detail entities."""

    __tablename__ = "place_detail"

    programme_junction_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("programme_junction.id", ondelete="CASCADE"), nullable=False
    )

    question = sqla.Column(sqla.String(), nullable=False)
    answer = sqla.Column(sqla.String(), nullable=True)
    indicator = sqla.Column(sqla.String(), nullable=False)

    programme_junction: Mapped["ProgrammeJunction"] = sqla.orm.relationship(back_populates="place_details")

    __table_args__ = (
        sqla.Index(
            "ix_unique_place_detail_per_submission",
            "programme_junction_id",
            "question",
            "indicator",
            unique=True,
        ),
        sqla.Index(
            "ix_place_detail_join_programme_junction",
            "programme_junction_id",
        ),
    )


class FundingQuestion(BaseModel):
    """Stores Funding Question entities."""

    __tablename__ = "funding_question"

    programme_junction_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("programme_junction.id", ondelete="CASCADE"), nullable=False
    )

    question = sqla.Column(sqla.String(), nullable=False)
    indicator = sqla.Column(sqla.String(), nullable=True)
    response = sqla.Column(sqla.String(), nullable=True)
    guidance_notes = sqla.Column(sqla.String(), nullable=True)

    programme_junction: Mapped["ProgrammeJunction"] = sqla.orm.relationship(back_populates="funding_questions")

    __table_args__ = (
        sqla.Index(
            "ix_unique_funding_question_per_submission",
            "programme_junction_id",
            "question",
            "indicator",
            unique=True,
        ),
        sqla.Index(
            "ix_funding_question_join_programme_junction",
            "programme_junction_id",
        ),
    )


class Project(BaseModel):
    """Stores Project Entities."""

    __tablename__ = "project_dim"

    programme_junction_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("programme_junction.id", ondelete="CASCADE"), nullable=False
    )

    project_id = sqla.Column(sqla.String(), nullable=False, unique=False)
    project_name = sqla.Column(sqla.String(), nullable=False)
    primary_intervention_theme = sqla.Column(sqla.String(), nullable=False)
    location_multiplicity = sqla.Column(sqla.String, nullable=True)
    locations = sqla.Column(sqla.String, nullable=False)
    postcodes = sqla.Column(sqla.ARRAY(sqla.String), nullable=True)
    gis_provided = sqla.Column(sqla.String, nullable=True)
    lat_long = sqla.Column(sqla.String, nullable=True)

    progress_records: Mapped[List["ProjectProgress"]] = sqla.orm.relationship(back_populates="project")
    funding_records: Mapped[List["Funding"]] = sqla.orm.relationship(back_populates="project")
    funding_comments: Mapped[List["FundingComment"]] = sqla.orm.relationship(back_populates="project")
    private_investments: Mapped[List["PrivateInvestment"]] = sqla.orm.relationship(back_populates="project")
    outputs: Mapped[List["OutputData"]] = sqla.orm.relationship(back_populates="project")
    outcomes: Mapped[List["OutcomeData"]] = sqla.orm.relationship(back_populates="project")
    risks: Mapped[List["RiskRegister"]] = sqla.orm.relationship(back_populates="project")
    programme_junction: Mapped["ProgrammeJunction"] = sqla.orm.relationship(back_populates="projects")

    __table_args__ = (
        sqla.Index(
            "ix_unique_project_per_return_dim",
            "programme_junction_id",
            "project_id",
            unique=True,
        ),
        sqla.Index(
            "ix_project_join_programme_junction",
            "programme_junction_id",
        ),
    )

    @hybrid_property
    def itl_regions(self) -> set[str]:
        """Returns the set of distinct ITL regions mapped from the project's postcodes.

        :return: A set of ITL regions.
        """
        itl_regions = get_itl_regions_from_postcodes(self.postcodes)
        return itl_regions


class ProjectProgress(BaseModel):
    """Stores Project Progress Entities."""

    __tablename__ = "project_progress"

    project_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("project_dim.id", ondelete="CASCADE"), nullable=False
    )

    start_date = sqla.Column(sqla.DateTime(), nullable=True)
    end_date = sqla.Column(sqla.DateTime(), nullable=True)
    delivery_stage = sqla.Column(sqla.String(), nullable=True)
    leading_factor_of_delay = sqla.Column(sqla.String(), nullable=True)
    adjustment_request_status = sqla.Column(sqla.String(), nullable=True)
    delivery_status = sqla.Column(sqla.String, nullable=True)
    delivery_rag = sqla.Column(sqla.String, nullable=True)
    spend_rag = sqla.Column(sqla.String, nullable=True)
    risk_rag = sqla.Column(sqla.String, nullable=True)
    commentary = sqla.Column(sqla.String(), nullable=True)
    important_milestone = sqla.Column(sqla.String(), nullable=True)
    date_of_important_milestone = sqla.Column(sqla.DateTime(), nullable=True)

    project: Mapped["Project"] = sqla.orm.relationship(back_populates="progress_records")

    __table_args__ = (
        sqla.Index(
            "ix_project_progress_join_project",
            "project_id",
        ),
    )


class Funding(BaseModel):
    """Stores Funding Entities."""

    __tablename__ = "funding"

    project_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("project_dim.id", ondelete="CASCADE"), nullable=False
    )

    funding_source_name = sqla.Column(sqla.String(), nullable=False)
    funding_source_type = sqla.Column(sqla.String(), nullable=False)
    secured = sqla.Column(sqla.String, nullable=True)
    start_date = sqla.Column(sqla.DateTime(), nullable=True)  # financial reporting period start
    end_date = sqla.Column(sqla.DateTime(), nullable=True)  # financial reporting period end
    spend_for_reporting_period = sqla.Column(sqla.Float(), nullable=True)
    status = sqla.Column(sqla.String, nullable=True)

    project: Mapped["Project"] = sqla.orm.relationship(back_populates="funding_records")

    __table_args__ = (
        # check that both start and end dates are not null at the same time
        sqla.CheckConstraint(
            or_(start_date.isnot(None), end_date.isnot(None)),
            name="ck_funding_start_or_end_date",
        ),
        sqla.Index(
            "ix_funding_join_project",
            "project_id",
        ),
    )


class FundingComment(BaseModel):
    """Stores Funding Comment Entities."""

    __tablename__ = "funding_comment"

    project_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("project_dim.id", ondelete="CASCADE"), nullable=False
    )

    comment = sqla.Column(sqla.String(), nullable=True)

    project: Mapped["Project"] = sqla.orm.relationship(back_populates="funding_comments")

    __table_args__ = (
        sqla.Index(
            "ix_funding_comment_join_project",
            "project_id",
        ),
    )


class PrivateInvestment(BaseModel):
    """Stores Private Investment Entities."""

    __tablename__ = "private_investment"

    project_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("project_dim.id", ondelete="CASCADE"), nullable=False
    )

    total_project_value = sqla.Column(sqla.Float(), nullable=False)
    townsfund_funding = sqla.Column(sqla.Float(), nullable=False)
    private_sector_funding_required = sqla.Column(sqla.Float(), nullable=True)
    private_sector_funding_secured = sqla.Column(sqla.Float(), nullable=True)
    additional_comments = sqla.Column(sqla.String(), nullable=True)

    project: Mapped["Project"] = sqla.orm.relationship(back_populates="private_investments")

    # Unique index for data integrity. Assumption inferred from ingest form that project should be unique per submission
    __table_args__ = (
        sqla.Index(
            "ix_private_investment_join_project",
            "project_id",
        ),
    )


class OutputData(BaseModel):
    """Stores Output data for Projects."""

    __tablename__ = "output_data"

    project_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("project_dim.id", ondelete="CASCADE"), nullable=False
    )
    output_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("output_dim.id"), nullable=False)

    start_date = sqla.Column(sqla.DateTime(), nullable=False)  # financial reporting period start
    end_date = sqla.Column(sqla.DateTime(), nullable=True)  # financial reporting period end
    unit_of_measurement = sqla.Column(sqla.String(), nullable=False)
    state = sqla.Column(sqla.String, nullable=True)
    amount = sqla.Column(sqla.Float(), nullable=True)
    additional_information = sqla.Column(sqla.String(), nullable=True)

    project: Mapped["Project"] = sqla.orm.relationship(back_populates="outputs")
    output_dim: Mapped["OutputDim"] = sqla.orm.relationship(back_populates="outputs")

    __table_args__ = (
        sqla.Index(
            "ix_output_join_project",
            "project_id",
        ),
        sqla.Index(
            "ix_output_join_output_dim",
            "output_id",
        ),
    )


class OutputDim(BaseModel):
    """Stores dimension reference data for Outputs."""

    __tablename__ = "output_dim"

    output_name = sqla.Column(sqla.String(), nullable=False, unique=True)
    output_category = sqla.Column(sqla.String(), nullable=False, unique=False)

    outputs: Mapped[list["OutputData"]] = sqla.orm.relationship(back_populates="output_dim")


class OutcomeData(BaseModel):
    """Stores Outcome data for projects."""

    __tablename__ = "outcome_data"

    project_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("project_dim.id", ondelete="CASCADE"), nullable=True
    )
    programme_junction_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("programme_junction.id", ondelete="CASCADE"), nullable=True
    )
    outcome_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("outcome_dim.id"), nullable=False)

    start_date = sqla.Column(sqla.DateTime(), nullable=False)  # financial reporting period start
    end_date = sqla.Column(sqla.DateTime(), nullable=False)  # financial reporting period end
    unit_of_measurement = sqla.Column(sqla.String(), nullable=False)
    geography_indicator = sqla.Column(sqla.String(), nullable=True)
    amount = sqla.Column(sqla.Float(), nullable=True)
    state = sqla.Column(sqla.String, nullable=True)
    higher_frequency = sqla.Column(sqla.String(), nullable=True)

    project: Mapped["Project"] = sqla.orm.relationship(back_populates="outcomes")
    outcome_dim: Mapped["OutcomeDim"] = sqla.orm.relationship(back_populates="outcomes")
    programme_junction: Mapped["ProgrammeJunction"] = sqla.orm.relationship(back_populates="outcomes")

    __table_args__ = (
        # check that either programme or project id exists but not both
        sqla.CheckConstraint(
            or_(
                and_(programme_junction_id.isnot(None), project_id.is_(None)),
                and_(programme_junction_id.is_(None), project_id.isnot(None)),
            ),
            name="ck_outcome_data_programme_junction_id_or_project_id",
        ),
        sqla.Index(
            "ix_outcome_join_programme_junction",
            "programme_junction_id",
        ),
        sqla.Index(
            "ix_outcome_join_project",
            "project_id",
        ),
        sqla.Index(
            "ix_outcome_join_outcome_dim",
            "outcome_id",
        ),
    )


class OutcomeDim(BaseModel):
    """Stores dimension reference data for Outcomes."""

    __tablename__ = "outcome_dim"

    outcome_name = sqla.Column(sqla.String(), nullable=False, unique=True)
    outcome_category = sqla.Column(sqla.String(), nullable=False, unique=False)

    outcomes: Mapped[list["OutcomeData"]] = sqla.orm.relationship(back_populates="outcome_dim")

    __table_args__ = (
        sqla.Index(
            "ix_outcome_dim_filter_outcome",
            "outcome_category",
        ),
    )


class RiskRegister(BaseModel):
    """Stores Risk Register data for projects."""

    __tablename__ = "risk_register"

    project_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("project_dim.id", ondelete="CASCADE"), nullable=True
    )
    programme_junction_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("programme_junction.id", ondelete="CASCADE"), nullable=True
    )

    risk_name = sqla.Column(sqla.String(), nullable=False)
    risk_category = sqla.Column(sqla.String(), nullable=True)
    short_desc = sqla.Column(sqla.String(), nullable=True)
    full_desc = sqla.Column(sqla.String(), nullable=True)
    consequences = sqla.Column(sqla.String(), nullable=True)
    pre_mitigated_impact = sqla.Column(
        sqla.String(),
        nullable=True,
    )
    pre_mitigated_likelihood = sqla.Column(sqla.String, nullable=True)
    mitigations = sqla.Column(sqla.String(), nullable=True)
    post_mitigated_impact = sqla.Column(
        sqla.String(),
        nullable=True,
    )
    post_mitigated_likelihood = sqla.Column(sqla.String, nullable=True)
    proximity = sqla.Column(sqla.String, nullable=True)
    risk_owner_role = sqla.Column(sqla.String(), nullable=True)

    project: Mapped["Project"] = sqla.orm.relationship(back_populates="risks")
    programme_junction: Mapped["ProgrammeJunction"] = sqla.orm.relationship(back_populates="risks")

    __table_args__ = (
        # check that either programme or project id exists but not both
        sqla.CheckConstraint(
            or_(
                and_(programme_junction_id.isnot(None), project_id.is_(None)),
                and_(programme_junction_id.is_(None), project_id.isnot(None)),
            ),
            name="ck_risk_register_programme_junction_id_or_project_id",
        ),
        sqla.Index(
            "ix_risk_register_join_project",
            "project_id",
        ),
        sqla.Index(
            "ix_risk_register_join_programme_junction",
            "programme_junction_id",
        ),
    )
