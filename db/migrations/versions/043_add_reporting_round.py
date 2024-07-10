"""add reporting round and update related tables

Revision ID: 043_add_reporting_round
Revises: 042_add_slug_fields
Create Date: 2024-07-09 14:00:00.000000

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects.postgresql import UUID

# revision identifiers, used by Alembic.
revision = "043_add_reporting_round"
down_revision = "042_add_slug_fields"
branch_labels = None
depends_on = None


def upgrade():
    # Create reporting_round table
    op.create_table(
        "reporting_round",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("fund_id", UUID(as_uuid=True), sa.ForeignKey("fund_dim.id"), nullable=False),
        sa.Column("observation_period_start", sa.DateTime(), nullable=False),
        sa.Column("observation_period_end", sa.DateTime(), nullable=False),
        sa.Column("submission_window_start", sa.DateTime(), nullable=False),
        sa.Column("submission_window_end", sa.DateTime(), nullable=False),
        sa.UniqueConstraint("fund_id", "round_number", name="uq_fund_round_number"),
        sa.CheckConstraint(
            "(observation_period_start <= observation_period_end) AND "
            "(observation_period_end <= submission_window_start) AND "
            "(submission_window_start <= submission_window_end)",
            name="dates_chronological_order",
        ),
    )

    # Update submission_dim table
    with op.batch_alter_table("submission_dim") as batch_op:
        batch_op.add_column(
            sa.Column("reporting_round_id", UUID(as_uuid=True), sa.ForeignKey("reporting_round.id"), nullable=True)
        )

    # Update programme_junction table
    with op.batch_alter_table("programme_junction") as batch_op:
        batch_op.add_column(
            sa.Column("reporting_round_id", UUID(as_uuid=True), sa.ForeignKey("reporting_round.id"), nullable=True)
        )
        batch_op.drop_constraint("uq_programme_junction_unique_submission_per_round", type_="unique")
        batch_op.create_unique_constraint(
            "uq_programme_junction_unique_submission_per_round", ["programme_id", "reporting_round_id"]
        )
        batch_op.drop_column("reporting_round")

    # Update raw_submission table
    with op.batch_alter_table("raw_submission") as batch_op:
        batch_op.add_column(
            sa.Column("reporting_round_id", UUID(as_uuid=True), sa.ForeignKey("reporting_round.id"), nullable=True)
        )
        batch_op.drop_constraint("uq_raw_submission_programme_round", type_="unique")
        batch_op.create_unique_constraint("uq_raw_submission_programme_round", ["programme_id", "reporting_round_id"])
        batch_op.drop_column("reporting_round")

    # Make reporting_round_id non-nullable after data migration
    op.execute(
        """
            UPDATE submission_dim
            SET reporting_round_id = (
                SELECT id
                FROM reporting_round
                WHERE observation_period_start = submission_dim.reporting_period_start
                LIMIT 1
            )
        """
    )

    # Update submission_dim table again
    with op.batch_alter_table("submission_dim") as batch_op:
        batch_op.drop_column("reporting_period_start")
        batch_op.drop_column("reporting_period_end")
        batch_op.drop_column("reporting_round")

    with op.batch_alter_table("submission_dim") as batch_op:
        batch_op.alter_column("reporting_round_id", nullable=False)

    with op.batch_alter_table("programme_junction") as batch_op:
        batch_op.alter_column("reporting_round_id", nullable=False)

    with op.batch_alter_table("raw_submission") as batch_op:
        batch_op.alter_column("reporting_round_id", nullable=False)


def downgrade():
    # Remove the seeded data from reporting_round table
    op.execute("""
    DELETE FROM reporting_round
    WHERE observation_period_start = '2023-02-01 00:00:00'::timestamp
      AND observation_period_end = '2023-02-12 00:00:00'::timestamp
    """)

    # Revert changes to raw_submission table
    with op.batch_alter_table("raw_submission") as batch_op:
        batch_op.add_column(sa.Column("reporting_round", sa.Integer(), nullable=True))
        batch_op.drop_constraint("uq_raw_submission_programme_round", type_="unique")
        batch_op.create_unique_constraint("uq_raw_submission_programme_round", ["programme_id", "reporting_round"])
        batch_op.drop_column("reporting_round_id")

    # Revert changes to programme_junction table
    with op.batch_alter_table("programme_junction") as batch_op:
        batch_op.add_column(sa.Column("reporting_round", sa.Integer(), nullable=True))
        batch_op.drop_constraint("uq_programme_junction_unique_submission_per_round", type_="unique")
        batch_op.create_unique_constraint(
            "uq_programme_junction_unique_submission_per_round", ["programme_id", "reporting_round"]
        )
        batch_op.drop_column("reporting_round_id")

    # Revert changes to submission_dim table
    with op.batch_alter_table("submission_dim") as batch_op:
        batch_op.add_column(sa.Column("reporting_period_start", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("reporting_period_end", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("reporting_round", sa.Integer(), nullable=True))
        batch_op.create_check_constraint("start_before_end", "reporting_period_end >= reporting_period_start")
        batch_op.create_index("ix_submission_filter_start_date", ["reporting_period_start"])
        batch_op.create_index("ix_submission_filter_end_date", ["reporting_period_end"])
        batch_op.drop_column("reporting_round_id")

    # Drop reporting_round table
    op.drop_table("reporting_round")
