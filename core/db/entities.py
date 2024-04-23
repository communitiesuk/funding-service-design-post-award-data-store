import uuid  # noqa
from datetime import datetime
from typing import List

import sqlalchemy as sqla
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.ext.hybrid import hybrid_property
from sqlalchemy.orm import Mapped
from sqlalchemy.sql.operators import and_, or_

from core.db import db
from core.db.types import GUID
from core.util import get_itl_regions_from_postcodes


class BaseModel(db.Model):
    __abstract__ = True

    id: Mapped[GUID] = sqla.orm.mapped_column(GUID(), default=uuid.uuid4, primary_key=True)


class Fund(BaseModel):
    """Stores Fund Entities."""

    __tablename__ = "fund_dim"

    fund_code = sqla.Column(sqla.String(), nullable=False, unique=True)

    programmes: Mapped[List["Programme"]] = sqla.orm.relationship(back_populates="fund")


class Funding(BaseModel):
    """Stores Funding Entities."""

    __tablename__ = "funding"

    project_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("project_dim.id", ondelete="CASCADE"), nullable=True
    )
    programme_junction_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("programme_junction.id", ondelete="CASCADE"), nullable=True
    )

    data_blob = sqla.Column(JSONB, nullable=False)
    start_date = sqla.Column(sqla.DateTime(), nullable=True)  # financial reporting period start
    end_date = sqla.Column(sqla.DateTime(), nullable=True)  # financial reporting period end

    project: Mapped["Project"] = sqla.orm.relationship(back_populates="funding_records")

    __table_args__ = (
        sqla.CheckConstraint(
            or_(
                and_(programme_junction_id.isnot(None), project_id.is_(None)),
                and_(programme_junction_id.is_(None), project_id.isnot(None)),
            ),
            name="ck_risk_register_programme_junction_id_or_project_id",
        ),
        # check that both start and end dates are not null at the same time
        sqla.CheckConstraint(
            or_(start_date.isnot(None), end_date.isnot(None)),
            name="ck_funding_start_or_end_date",
        ),
        sqla.CheckConstraint(
            "start_date IS NULL OR end_date IS NULL OR (start_date <= end_date)",
            name="start_before_end",  # gets prefixed with `ck_{table}`
        ),
        sqla.Index(
            "ix_funding_join_project",
            "project_id",
        ),
        sqla.Index(
            "ix_funding_join_programme_junction",
            "programme_junction_id",
        ),
    )


class FundingComment(BaseModel):
    """Stores Funding Comment Entities."""

    __tablename__ = "funding_comment"

    project_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("project_dim.id", ondelete="CASCADE"), nullable=False
    )

    data_blob = sqla.Column(JSONB, nullable=False)

    project: Mapped["Project"] = sqla.orm.relationship(back_populates="funding_comments")

    __table_args__ = (
        sqla.Index(
            "ix_funding_comment_join_project",
            "project_id",
        ),
    )


class FundingQuestion(BaseModel):
    """Stores Funding Question entities."""

    __tablename__ = "funding_question"

    programme_junction_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("programme_junction.id", ondelete="CASCADE"), nullable=False
    )

    data_blob = sqla.Column(JSONB, nullable=False)

    programme_junction: Mapped["ProgrammeJunction"] = sqla.orm.relationship(back_populates="funding_questions")

    __table_args__ = (
        sqla.Index(
            "ix_funding_question_join_programme_junction",
            "programme_junction_id",
        ),
    )


project_geospatial_association = db.Table(
    "project_geospatial_association",
    db.Column(
        "project_id", GUID(), db.ForeignKey("project_dim.id", ondelete="CASCADE"), nullable=False, primary_key=True
    ),
    db.Column(
        "geospatial_id",
        GUID(),
        db.ForeignKey("geospatial_dim.id", ondelete="RESTRICT"),
        nullable=False,
        primary_key=True,
    ),
)


class GeospatialDim(BaseModel):
    """Stores Geospatial information mapped to postcodes."""

    __tablename__ = "geospatial_dim"

    postcode_prefix = sqla.Column(sqla.String(length=4), nullable=False, unique=True)
    itl1_region_code = sqla.Column(sqla.String(), nullable=False, unique=False)
    data_blob = sqla.Column(JSONB, nullable=True)

    projects: Mapped[List["Project"]] = sqla.orm.relationship(
        back_populates="geospatial_dims", secondary=project_geospatial_association
    )

    __table_args__ = (
        sqla.Index(
            "ix_geospatial_dim_filter_region",
            "itl1_region_code",
        ),
    )


class Organisation(BaseModel):
    """Stores organisation information."""

    __tablename__ = "organisation_dim"

    organisation_name = sqla.Column(sqla.String(), nullable=False, unique=True)
    # TODO: geography needs review, field definition may change
    geography = sqla.Column(sqla.String(), nullable=True)

    programmes: Mapped[List["Programme"]] = sqla.orm.relationship(back_populates="organisation")


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
    end_date = sqla.Column(sqla.DateTime(), nullable=True)  # financial reporting period end
    data_blob = sqla.Column(JSONB, nullable=False)

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
        sqla.CheckConstraint(
            "(start_date <= end_date)",
            name="start_before_end",  # gets prefixed with `ck_{table}`
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


class OutputData(BaseModel):
    """Stores Output data for Projects."""

    __tablename__ = "output_data"

    project_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("project_dim.id", ondelete="CASCADE"), nullable=True
    )
    programme_junction_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("programme_junction.id", ondelete="CASCADE"), nullable=True
    )
    output_id: Mapped[GUID] = sqla.orm.mapped_column(sqla.ForeignKey("output_dim.id"), nullable=False)

    start_date = sqla.Column(sqla.DateTime(), nullable=False)  # financial reporting period start
    end_date = sqla.Column(sqla.DateTime(), nullable=True)  # financial reporting period end
    data_blob = sqla.Column(JSONB, nullable=False)

    project: Mapped["Project"] = sqla.orm.relationship(back_populates="outputs")
    output_dim: Mapped["OutputDim"] = sqla.orm.relationship(back_populates="outputs")
    programme_junction: Mapped["ProgrammeJunction"] = sqla.orm.relationship(back_populates="outputs")

    __table_args__ = (
        sqla.CheckConstraint(
            or_(
                and_(programme_junction_id.isnot(None), project_id.is_(None)),
                and_(programme_junction_id.is_(None), project_id.isnot(None)),
            ),
            name="ck_output_data_programme_junction_id_or_project_id",
        ),
        sqla.CheckConstraint(
            "(start_date <= end_date)",
            name="start_before_end",  # gets prefixed with `ck_{table}`
        ),
        sqla.Index(
            "ix_output_join_programme_junction",
            "programme_junction_id",
        ),
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


class PlaceDetail(BaseModel):
    """Stores Place Detail entities."""

    __tablename__ = "place_detail"

    programme_junction_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("programme_junction.id", ondelete="CASCADE"), nullable=False
    )

    data_blob = sqla.Column(JSONB, nullable=False)

    programme_junction: Mapped["ProgrammeJunction"] = sqla.orm.relationship(back_populates="place_details")

    __table_args__ = (
        sqla.Index(
            "ix_place_detail_join_programme_junction",
            "programme_junction_id",
        ),
    )


class PrivateInvestment(BaseModel):
    """Stores Private Investment Entities."""

    __tablename__ = "private_investment"

    project_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("project_dim.id", ondelete="CASCADE"), nullable=False
    )

    data_blob = sqla.Column(JSONB, nullable=False)

    project: Mapped["Project"] = sqla.orm.relationship(back_populates="private_investments")

    # Unique index for data integrity. Assumption inferred from ingest form that project should be unique per submission
    __table_args__ = (
        sqla.Index(
            "ix_private_investment_join_project",
            "project_id",
        ),
    )


class Programme(BaseModel):
    """Stores Programme entities."""

    __tablename__ = "programme_dim"

    programme_id = sqla.Column(sqla.String(), nullable=False, unique=True)

    programme_name = sqla.Column(sqla.String(), nullable=False)
    organisation_id = sqla.Column(GUID(), sqla.ForeignKey("organisation_dim.id"), nullable=False)
    fund_type_id = sqla.Column(GUID(), sqla.ForeignKey("fund_dim.id"), nullable=False)

    organisation: Mapped["Organisation"] = sqla.orm.relationship(back_populates="programmes")
    in_round_programmes: Mapped[List["ProgrammeJunction"]] = sqla.orm.relationship(back_populates="programme_ref")
    fund: Mapped["Fund"] = sqla.orm.relationship(back_populates="programmes")

    __table_args__ = (
        sqla.Index(
            "ix_unique_programme_name_per_fund",
            "programme_name",
            "fund_type_id",
            unique=True,
        ),
        sqla.Index(
            "ix_programme_join_fund_type",
            "fund_type_id",
        ),
        sqla.Index(
            "ix_programme_join_organisation",
            "organisation_id",
        ),
    )


class ProgrammeFundingManagement(BaseModel):
    """Stores Towns Fund Programme Management funding info."""

    __tablename__ = "programme_funding_management"

    programme_junction_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("programme_junction.id", ondelete="CASCADE"), nullable=False
    )

    data_blob = sqla.Column(JSONB, nullable=False)
    start_date = sqla.Column(sqla.DateTime(), nullable=True)  # financial reporting period start
    end_date = sqla.Column(sqla.DateTime(), nullable=True)  # financial reporting period end

    programme_junction: Mapped["ProgrammeJunction"] = sqla.orm.relationship(
        back_populates="programme_funding_management_records"
    )

    __table_args__ = (
        sqla.Index(
            "ix_programme_funding_management_join_programme_junction",
            "programme_junction_id",
        ),
        sqla.CheckConstraint(
            "start_date IS NULL OR end_date IS NULL OR (start_date <= end_date)",
            name="start_before_end",  # gets prefixed with `ck_{table}`
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
    reporting_round = sqla.Column(sqla.Integer, nullable=False)

    # parent relationships
    submission: Mapped["Submission"] = sqla.orm.relationship(back_populates="programme_junction", single_parent=True)
    programme_ref: Mapped["Programme"] = sqla.orm.relationship(back_populates="in_round_programmes")

    # child relationships
    projects: Mapped[List["Project"]] = sqla.orm.relationship(back_populates="programme_junction")
    progress_records: Mapped[List["ProgrammeProgress"]] = sqla.orm.relationship(back_populates="programme_junction")
    place_details: Mapped[List["PlaceDetail"]] = sqla.orm.relationship(back_populates="programme_junction")
    funding_questions: Mapped[List["FundingQuestion"]] = sqla.orm.relationship(back_populates="programme_junction")
    outputs: Mapped[List["OutputData"]] = sqla.orm.relationship(back_populates="programme_junction")
    outcomes: Mapped[List["OutcomeData"]] = sqla.orm.relationship(back_populates="programme_junction")
    risks: Mapped[List["RiskRegister"]] = sqla.orm.relationship(back_populates="programme_junction")
    project_finance_changes: Mapped[List["ProjectFinanceChange"]] = sqla.orm.relationship(
        back_populates="programme_junction"
    )
    programme_funding_management_records: Mapped[List["ProgrammeFundingManagement"]] = sqla.orm.relationship(
        back_populates="programme_junction"
    )

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
        sqla.UniqueConstraint(
            "programme_id",
            "reporting_round",
            name="uq_programme_junction_unique_submission_per_round",
        ),
    )


class ProgrammeProgress(BaseModel):
    """Stores Programme Progress entities."""

    __tablename__ = "programme_progress"

    programme_junction_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("programme_junction.id", ondelete="CASCADE"), nullable=False
    )

    data_blob = sqla.Column(JSONB, nullable=False)

    programme_junction: Mapped["ProgrammeJunction"] = sqla.orm.relationship(back_populates="progress_records")

    __table_args__ = (
        sqla.Index(
            "ix_programme_progress_join_programme_junction",
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
    postcodes = sqla.Column(sqla.ARRAY(sqla.String), nullable=True)
    data_blob = sqla.Column(JSONB, nullable=True)

    progress_records: Mapped[List["ProjectProgress"]] = sqla.orm.relationship(back_populates="project")
    funding_records: Mapped[List["Funding"]] = sqla.orm.relationship(back_populates="project")
    funding_comments: Mapped[List["FundingComment"]] = sqla.orm.relationship(back_populates="project")
    private_investments: Mapped[List["PrivateInvestment"]] = sqla.orm.relationship(back_populates="project")
    outputs: Mapped[List["OutputData"]] = sqla.orm.relationship(back_populates="project")
    outcomes: Mapped[List["OutcomeData"]] = sqla.orm.relationship(back_populates="project")
    risks: Mapped[List["RiskRegister"]] = sqla.orm.relationship(back_populates="project")
    programme_junction: Mapped["ProgrammeJunction"] = sqla.orm.relationship(back_populates="projects")
    geospatial_dims: Mapped[List["GeospatialDim"]] = sqla.orm.relationship(
        back_populates="projects", secondary=project_geospatial_association
    )

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


class ProjectFinanceChange(BaseModel):
    """Stores Project Finance Change data for projects."""

    __tablename__ = "project_finance_change"

    programme_junction_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("programme_junction.id", ondelete="CASCADE"), nullable=False
    )
    data_blob = sqla.Column(JSONB, nullable=False)

    programme_junction: Mapped["ProgrammeJunction"] = sqla.orm.relationship(back_populates="project_finance_changes")

    __table_args__ = (
        sqla.Index(
            "ix_project_finance_change_join_programme_junction",
            "programme_junction_id",
        ),
    )


class ProjectProgress(BaseModel):
    """Stores Project Progress Entities."""

    __tablename__ = "project_progress"

    project_id: Mapped[GUID] = sqla.orm.mapped_column(
        sqla.ForeignKey("project_dim.id", ondelete="CASCADE"), nullable=False
    )

    start_date = sqla.Column(sqla.DateTime(), nullable=True)
    end_date = sqla.Column(sqla.DateTime(), nullable=True)
    data_blob = sqla.Column(JSONB, nullable=False)
    date_of_important_milestone = sqla.Column(sqla.DateTime(), nullable=True)

    project: Mapped["Project"] = sqla.orm.relationship(back_populates="progress_records")

    __table_args__ = (
        sqla.Index(
            "ix_project_progress_join_project",
            "project_id",
        ),
        sqla.CheckConstraint(
            "start_date IS NULL OR end_date IS NULL OR (start_date <= end_date)",
            name="start_before_end",  # gets prefixed with `ck_{table}`
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

    data_blob = sqla.Column(JSONB, nullable=False)

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


class Submission(BaseModel):
    """Stores Submission information."""

    __tablename__ = "submission_dim"

    submission_id = sqla.Column(sqla.String(), nullable=False, unique=True)

    submission_date = sqla.Column(sqla.DateTime(), nullable=True)
    ingest_date = sqla.Column(sqla.DateTime(), nullable=False, default=datetime.now())
    reporting_period_start = sqla.Column(sqla.DateTime(), nullable=False)
    reporting_period_end = sqla.Column(sqla.DateTime(), nullable=False)
    reporting_round = sqla.Column(sqla.Integer(), nullable=False)
    submission_filename = sqla.Column(sqla.String(), nullable=True)
    data_blob = sqla.Column(JSONB, nullable=True)
    submitting_account_id = sqla.Column(sqla.String())
    submitting_user_email = sqla.Column(sqla.String())

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
        sqla.CheckConstraint(
            "(reporting_period_start <= reporting_period_end)",
            name="start_before_end",  # gets prefixed with `ck_{table}`
        ),
    )

    @hybrid_property
    def submission_number(self) -> int:
        """Extracts the submission number from the submission ID.

        SubmissionIDs are in the format "S-RXX-X" where the final section is the submission number.

        :return: submission number
        """
        return int(self.submission_id.split("-")[-1])
