"""empty message

Revision ID: d9eca05d26a1
Revises:
Create Date: 2023-06-12 14:54:52.280685

"""

import sqlalchemy as sa
from alembic import op

import core

# revision identifiers, used by Alembic.
revision = "d9eca05d26a1"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "organisation_dim",
        sa.Column("organisation_name", sa.String(), nullable=False),
        sa.Column("geography", sa.String(), nullable=True),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_organisation_dim")),
        sa.UniqueConstraint("organisation_name", name=op.f("uq_organisation_dim_organisation_name")),
    )
    op.create_table(
        "outcome_dim",
        sa.Column("outcome_name", sa.String(), nullable=False),
        sa.Column("outcome_category", sa.String(), nullable=False),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_outcome_dim")),
        sa.UniqueConstraint("outcome_name", name=op.f("uq_outcome_dim_outcome_name")),
    )
    op.create_table(
        "output_dim",
        sa.Column("output_name", sa.String(), nullable=False),
        sa.Column("output_category", sa.String(), nullable=False),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_output_dim")),
        sa.UniqueConstraint("output_name", name=op.f("uq_output_dim_output_name")),
    )
    op.create_table(
        "submission_dim",
        sa.Column("submission_id", sa.String(), nullable=False),
        sa.Column("submission_date", sa.DateTime(), nullable=True),
        sa.Column("ingest_date", sa.DateTime(), nullable=False),
        sa.Column("reporting_period_start", sa.DateTime(), nullable=False),
        sa.Column("reporting_period_end", sa.DateTime(), nullable=False),
        sa.Column("reporting_round", sa.Integer(), nullable=False),
        sa.Column("submission_file", sa.LargeBinary(), nullable=True),
        sa.Column("submission_filename", sa.String(), nullable=True),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_submission_dim")),
        sa.UniqueConstraint("submission_id", name=op.f("uq_submission_dim_submission_id")),
    )
    op.create_table(
        "programme_dim",
        sa.Column("programme_id", sa.String(), nullable=False),
        sa.Column("programme_name", sa.String(), nullable=False),
        sa.Column("fund_type_id", sa.String(), nullable=False),
        sa.Column("organisation_id", core.db.types.GUID(), nullable=False),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["organisation_id"], ["organisation_dim.id"], name=op.f("fk_programme_dim_organisation_id_organisation_dim")
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_programme_dim")),
        sa.UniqueConstraint("programme_id", name=op.f("uq_programme_dim_programme_id")),
        sa.UniqueConstraint("programme_name", name=op.f("uq_programme_dim_programme_name")),
    )
    op.create_table(
        "funding_question",
        sa.Column("submission_id", core.db.types.GUID(), nullable=False),
        sa.Column("programme_id", core.db.types.GUID(), nullable=False),
        sa.Column("question", sa.String(), nullable=False),
        sa.Column("indicator", sa.String(), nullable=True),
        sa.Column("response", sa.String(), nullable=True),
        sa.Column("guidance_notes", sa.String(), nullable=True),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["programme_id"], ["programme_dim.id"], name=op.f("fk_funding_question_programme_id_programme_dim")
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["submission_dim.id"],
            name=op.f("fk_funding_question_submission_id_submission_dim"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_funding_question")),
    )
    with op.batch_alter_table("funding_question", schema=None) as batch_op:
        batch_op.create_index(
            "ix_unique_funding_question", ["submission_id", "programme_id", "question", "indicator"], unique=True
        )

    op.create_table(
        "place_detail",
        sa.Column("submission_id", core.db.types.GUID(), nullable=False),
        sa.Column("programme_id", core.db.types.GUID(), nullable=False),
        sa.Column("question", sa.String(), nullable=False),
        sa.Column("answer", sa.String(), nullable=True),
        sa.Column("indicator", sa.String(), nullable=False),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["programme_id"], ["programme_dim.id"], name=op.f("fk_place_detail_programme_id_programme_dim")
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["submission_dim.id"],
            name=op.f("fk_place_detail_submission_id_submission_dim"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_place_detail")),
    )
    with op.batch_alter_table("place_detail", schema=None) as batch_op:
        batch_op.create_index(
            "ix_unique_place_detail", ["submission_id", "programme_id", "question", "indicator"], unique=True
        )

    op.create_table(
        "programme_progress",
        sa.Column("submission_id", core.db.types.GUID(), nullable=False),
        sa.Column("programme_id", core.db.types.GUID(), nullable=False),
        sa.Column("question", sa.String(), nullable=False),
        sa.Column("answer", sa.String(), nullable=True),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["programme_id"], ["programme_dim.id"], name=op.f("fk_programme_progress_programme_id_programme_dim")
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["submission_dim.id"],
            name=op.f("fk_programme_progress_submission_id_submission_dim"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_programme_progress")),
    )
    with op.batch_alter_table("programme_progress", schema=None) as batch_op:
        batch_op.create_index("ix_unique_programme_progress", ["submission_id", "question"], unique=True)

    op.create_table(
        "project_dim",
        sa.Column("project_id", sa.String(), nullable=False),
        sa.Column("submission_id", core.db.types.GUID(), nullable=False),
        sa.Column("programme_id", core.db.types.GUID(), nullable=False),
        sa.Column("project_name", sa.String(), nullable=False),
        sa.Column("primary_intervention_theme", sa.String(), nullable=False),
        sa.Column(
            "location_multiplicity", sa.Enum("SINGLE", "MULTIPLE", name="project_location_multiplicity"), nullable=False
        ),
        sa.Column("locations", sa.String(), nullable=False),
        sa.Column("postcodes", sa.String(), nullable=True),
        sa.Column("gis_provided", sa.Enum("YES", "NO", name="yesnoenum"), nullable=True),
        sa.Column("lat_long", sa.String(), nullable=True),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["programme_id"], ["programme_dim.id"], name=op.f("fk_project_dim_programme_id_programme_dim")
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["submission_dim.id"],
            name=op.f("fk_project_dim_submission_id_submission_dim"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_dim")),
    )
    with op.batch_alter_table("project_dim", schema=None) as batch_op:
        batch_op.create_index("ix_unique_project_dim", ["submission_id", "project_id"], unique=True)

    op.create_table(
        "funding",
        sa.Column("submission_id", core.db.types.GUID(), nullable=False),
        sa.Column("project_id", core.db.types.GUID(), nullable=False),
        sa.Column("funding_source_name", sa.String(), nullable=False),
        sa.Column("funding_source_type", sa.String(), nullable=False),
        sa.Column("secured", sa.Enum("YES", "NO", name="funding_secured"), nullable=True),
        sa.Column("start_date", sa.DateTime(), nullable=True),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("spend_for_reporting_period", sa.Float(), nullable=True),
        sa.Column("status", sa.Enum("ACTUAL", "FORECAST", name="funding_status"), nullable=True),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.ForeignKeyConstraint(["project_id"], ["project_dim.id"], name=op.f("fk_funding_project_id_project_dim")),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["submission_dim.id"],
            name=op.f("fk_funding_submission_id_submission_dim"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_funding")),
    )
    with op.batch_alter_table("funding", schema=None) as batch_op:
        batch_op.create_index(
            "ix_unique_funding",
            ["submission_id", "project_id", "funding_source_name", "funding_source_type", "start_date", "end_date"],
            unique=True,
        )

    op.create_table(
        "funding_comment",
        sa.Column("submission_id", core.db.types.GUID(), nullable=False),
        sa.Column("project_id", core.db.types.GUID(), nullable=False),
        sa.Column("comment", sa.String(), nullable=False),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"], ["project_dim.id"], name=op.f("fk_funding_comment_project_id_project_dim")
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["submission_dim.id"],
            name=op.f("fk_funding_comment_submission_id_submission_dim"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_funding_comment")),
    )
    with op.batch_alter_table("funding_comment", schema=None) as batch_op:
        batch_op.create_index("ix_unique_funding_comment", ["submission_id", "project_id"], unique=True)

    op.create_table(
        "outcome_data",
        sa.Column("submission_id", core.db.types.GUID(), nullable=False),
        sa.Column("programme_id", core.db.types.GUID(), nullable=True),
        sa.Column("project_id", core.db.types.GUID(), nullable=True),
        sa.Column("outcome_id", core.db.types.GUID(), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=False),
        sa.Column("unit_of_measurement", sa.String(), nullable=False),
        sa.Column("geography_indicator", sa.String(), nullable=True),
        sa.Column("amount", sa.Float(), nullable=True),
        sa.Column("state", sa.Enum("ACTUAL", "FORECAST", name="outcome_data_state"), nullable=False),
        sa.Column("higher_frequency", sa.String(), nullable=True),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.CheckConstraint(
            "programme_id IS NOT NULL AND project_id IS NULL OR programme_id IS NULL AND project_id IS NOT NULL",
            name=op.f("ck_outcome_data_ck_outcome_data_programme_or_project_id"),
        ),
        sa.ForeignKeyConstraint(
            ["outcome_id"], ["outcome_dim.id"], name=op.f("fk_outcome_data_outcome_id_outcome_dim")
        ),
        sa.ForeignKeyConstraint(
            ["programme_id"], ["programme_dim.id"], name=op.f("fk_outcome_data_programme_id_programme_dim")
        ),
        sa.ForeignKeyConstraint(
            ["project_id"], ["project_dim.id"], name=op.f("fk_outcome_data_project_id_project_dim")
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["submission_dim.id"],
            name=op.f("fk_outcome_data_submission_id_submission_dim"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_outcome_data")),
    )
    with op.batch_alter_table("outcome_data", schema=None) as batch_op:
        batch_op.create_index(
            "ix_unique_outcome",
            ["submission_id", "project_id", "outcome_id", "start_date", "end_date", "geography_indicator"],
            unique=True,
        )

    op.create_table(
        "output_data",
        sa.Column("submission_id", core.db.types.GUID(), nullable=False),
        sa.Column("project_id", core.db.types.GUID(), nullable=False),
        sa.Column("output_id", core.db.types.GUID(), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.Column("unit_of_measurement", sa.String(), nullable=False),
        sa.Column("state", sa.Enum("ACTUAL", "FORECAST", name="output_data_state"), nullable=True),
        sa.Column("amount", sa.Float(), nullable=True),
        sa.Column("additional_information", sa.String(), nullable=True),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.ForeignKeyConstraint(["output_id"], ["output_dim.id"], name=op.f("fk_output_data_output_id_output_dim")),
        sa.ForeignKeyConstraint(["project_id"], ["project_dim.id"], name=op.f("fk_output_data_project_id_project_dim")),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["submission_dim.id"],
            name=op.f("fk_output_data_submission_id_submission_dim"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_output_data")),
    )
    with op.batch_alter_table("output_data", schema=None) as batch_op:
        batch_op.create_index(
            "ix_unique_output",
            ["submission_id", "project_id", "output_id", "start_date", "end_date", "unit_of_measurement", "state"],
            unique=True,
        )

    op.create_table(
        "private_investment",
        sa.Column("submission_id", core.db.types.GUID(), nullable=False),
        sa.Column("project_id", core.db.types.GUID(), nullable=False),
        sa.Column("total_project_value", sa.Float(), nullable=False),
        sa.Column("townsfund_funding", sa.Float(), nullable=False),
        sa.Column("private_sector_funding_required", sa.Float(), nullable=True),
        sa.Column("private_sector_funding_secured", sa.Float(), nullable=True),
        sa.Column("additional_comments", sa.String(), nullable=True),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"], ["project_dim.id"], name=op.f("fk_private_investment_project_id_project_dim")
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["submission_dim.id"],
            name=op.f("fk_private_investment_submission_id_submission_dim"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_private_investment")),
    )
    with op.batch_alter_table("private_investment", schema=None) as batch_op:
        batch_op.create_index("ix_unique_private_investment", ["submission_id", "project_id"], unique=True)

    op.create_table(
        "project_progress",
        sa.Column("submission_id", core.db.types.GUID(), nullable=False),
        sa.Column("project_id", core.db.types.GUID(), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=False),
        sa.Column("end_date", sa.DateTime(), nullable=False),
        sa.Column("adjustment_request_status", sa.String(), nullable=False),
        sa.Column(
            "delivery_status",
            sa.Enum(
                "NOT_YET_STARTED",
                "ONGOING_ON_TRACK",
                "ONGOING_DELAYED",
                "COMPLETED",
                "OTHER",
                name="project_progress_delivery_status",
            ),
            nullable=False,
        ),
        sa.Column(
            "delivery_rag",
            sa.Enum("ONE", "TWO", "THREE", "FOUR", "FIVE", name="project_progress_delivery_rag"),
            nullable=False,
        ),
        sa.Column(
            "spend_rag",
            sa.Enum("ONE", "TWO", "THREE", "FOUR", "FIVE", name="project_progress_spend_rag"),
            nullable=False,
        ),
        sa.Column(
            "risk_rag", sa.Enum("ONE", "TWO", "THREE", "FOUR", "FIVE", name="project_progress_risk_rag"), nullable=False
        ),
        sa.Column("commentary", sa.String(), nullable=True),
        sa.Column("important_milestone", sa.String(), nullable=True),
        sa.Column("date_of_important_milestone", sa.DateTime(), nullable=True),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["project_id"], ["project_dim.id"], name=op.f("fk_project_progress_project_id_project_dim")
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["submission_dim.id"],
            name=op.f("fk_project_progress_submission_id_submission_dim"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_progress")),
    )
    with op.batch_alter_table("project_progress", schema=None) as batch_op:
        batch_op.create_index("ix_unique_project_progress", ["submission_id", "project_id"], unique=True)

    op.create_table(
        "risk_register",
        sa.Column("submission_id", core.db.types.GUID(), nullable=False),
        sa.Column("programme_id", core.db.types.GUID(), nullable=True),
        sa.Column("project_id", core.db.types.GUID(), nullable=True),
        sa.Column("risk_name", sa.String(), nullable=False),
        sa.Column("risk_category", sa.String(), nullable=True),
        sa.Column("short_desc", sa.String(), nullable=True),
        sa.Column("full_desc", sa.String(), nullable=True),
        sa.Column("consequences", sa.String(), nullable=True),
        sa.Column("pre_mitigated_impact", sa.String(), nullable=True),
        sa.Column(
            "pre_mitigated_likelihood",
            sa.Enum("LOW", "MEDIUM", "HIGH", "ALMOST_CERTAIN", name="risk_register_pre_mitigated_likelihood"),
            nullable=True,
        ),
        sa.Column("mitigations", sa.String(), nullable=True),
        sa.Column("post_mitigated_impact", sa.String(), nullable=True),
        sa.Column(
            "post_mitigated_likelihood",
            sa.Enum("LOW", "MEDIUM", "HIGH", "ALMOST_CERTAIN", name="risk_register_post_mitigated_likelihood"),
            nullable=True,
        ),
        sa.Column(
            "proximity",
            sa.Enum("REMOTE", "DISTANT", "APPROACHING", "CLOSE", "IMMINENT", name="risk_register_proximity"),
            nullable=True,
        ),
        sa.Column("risk_owner_role", sa.String(), nullable=True),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.CheckConstraint(
            "programme_id IS NOT NULL AND project_id IS NULL OR programme_id IS NULL AND project_id IS NOT NULL",
            name=op.f("ck_risk_register_ck_risk_register_programme_or_project_id"),
        ),
        sa.ForeignKeyConstraint(
            ["programme_id"], ["programme_dim.id"], name=op.f("fk_risk_register_programme_id_programme_dim")
        ),
        sa.ForeignKeyConstraint(
            ["project_id"], ["project_dim.id"], name=op.f("fk_risk_register_project_id_project_dim")
        ),
        sa.ForeignKeyConstraint(
            ["submission_id"],
            ["submission_dim.id"],
            name=op.f("fk_risk_register_submission_id_submission_dim"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_risk_register")),
    )
    with op.batch_alter_table("risk_register", schema=None) as batch_op:
        batch_op.create_index(
            "ix_unique_risk_register", ["submission_id", "programme_id", "project_id", "risk_name"], unique=True
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("risk_register", schema=None) as batch_op:
        batch_op.drop_index("ix_unique_risk_register")

    op.drop_table("risk_register")
    with op.batch_alter_table("project_progress", schema=None) as batch_op:
        batch_op.drop_index("ix_unique_project_progress")

    op.drop_table("project_progress")
    with op.batch_alter_table("private_investment", schema=None) as batch_op:
        batch_op.drop_index("ix_unique_private_investment")

    op.drop_table("private_investment")
    with op.batch_alter_table("output_data", schema=None) as batch_op:
        batch_op.drop_index("ix_unique_output")

    op.drop_table("output_data")
    with op.batch_alter_table("outcome_data", schema=None) as batch_op:
        batch_op.drop_index("ix_unique_outcome")

    op.drop_table("outcome_data")
    with op.batch_alter_table("funding_comment", schema=None) as batch_op:
        batch_op.drop_index("ix_unique_funding_comment")

    op.drop_table("funding_comment")
    with op.batch_alter_table("funding", schema=None) as batch_op:
        batch_op.drop_index("ix_unique_funding")

    op.drop_table("funding")
    with op.batch_alter_table("project_dim", schema=None) as batch_op:
        batch_op.drop_index("ix_unique_project_dim")

    op.drop_table("project_dim")
    with op.batch_alter_table("programme_progress", schema=None) as batch_op:
        batch_op.drop_index("ix_unique_programme_progress")

    op.drop_table("programme_progress")
    with op.batch_alter_table("place_detail", schema=None) as batch_op:
        batch_op.drop_index("ix_unique_place_detail")

    op.drop_table("place_detail")
    with op.batch_alter_table("funding_question", schema=None) as batch_op:
        batch_op.drop_index("ix_unique_funding_question")

    op.drop_table("funding_question")
    op.drop_table("programme_dim")
    op.drop_table("submission_dim")
    op.drop_table("output_dim")
    op.drop_table("outcome_dim")
    op.drop_table("organisation_dim")
    # ### end Alembic commands ###
