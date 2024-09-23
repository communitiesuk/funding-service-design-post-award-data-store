"""make old reporting round fields nullable

Revision ID: 042_nullable_reporting_round_col
Revises: 041_new_programme_round_constrai
Create Date: 2024-09-20 09:50:08.475062

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "042_nullable_reporting_round_col"
down_revision = "041_new_programme_round_constrai"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("programme_junction", schema=None) as batch_op:
        batch_op.alter_column("reporting_round", existing_type=sa.INTEGER(), nullable=True)

    with op.batch_alter_table("submission_dim", schema=None) as batch_op:
        batch_op.alter_column("reporting_period_start", existing_type=postgresql.TIMESTAMP(), nullable=True)
        batch_op.alter_column("reporting_period_end", existing_type=postgresql.TIMESTAMP(), nullable=True)


def downgrade():
    with op.batch_alter_table("submission_dim", schema=None) as batch_op:
        batch_op.alter_column("reporting_period_end", existing_type=postgresql.TIMESTAMP(), nullable=False)
        batch_op.alter_column("reporting_period_start", existing_type=postgresql.TIMESTAMP(), nullable=False)

    with op.batch_alter_table("programme_junction", schema=None) as batch_op:
        batch_op.alter_column("reporting_round", existing_type=sa.INTEGER(), nullable=False)
