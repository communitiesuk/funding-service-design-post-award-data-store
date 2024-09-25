"""remove old rr cols

Revision ID: 044_remove_old_rr_cols
Revises: 043_non_nullable_reporting_round
Create Date: 2024-09-24 17:44:36.150473

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "044_remove_old_rr_cols"
down_revision = "043_non_nullable_reporting_round"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("programme_junction", schema=None) as batch_op:
        batch_op.drop_constraint("uq_programme_junction_programme_id_reporting_round_id", type_="unique")
        batch_op.drop_constraint("uq_programme_junction_unique_submission_per_round", type_="unique")
        batch_op.drop_column("reporting_round")

    with op.batch_alter_table("submission_dim", schema=None) as batch_op:
        batch_op.drop_index("ix_submission_filter_end_date")
        batch_op.drop_index("ix_submission_filter_start_date")
        batch_op.drop_column("reporting_period_start")
        batch_op.drop_column("reporting_period_end")


def downgrade():
    with op.batch_alter_table("submission_dim", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("reporting_period_end", postgresql.TIMESTAMP(), autoincrement=False, nullable=True)
        )
        batch_op.add_column(
            sa.Column("reporting_period_start", postgresql.TIMESTAMP(), autoincrement=False, nullable=True)
        )
        batch_op.create_index("ix_submission_filter_start_date", ["reporting_period_start"], unique=False)
        batch_op.create_index("ix_submission_filter_end_date", ["reporting_period_end"], unique=False)

    with op.batch_alter_table("programme_junction", schema=None) as batch_op:
        batch_op.add_column(sa.Column("reporting_round", sa.INTEGER(), autoincrement=False, nullable=True))
        batch_op.create_unique_constraint(
            "uq_programme_junction_unique_submission_per_round", ["programme_id", "reporting_round"]
        )
        batch_op.create_unique_constraint(
            "uq_programme_junction_programme_id_reporting_round_id", ["programme_id", "reporting_round_id"]
        )
