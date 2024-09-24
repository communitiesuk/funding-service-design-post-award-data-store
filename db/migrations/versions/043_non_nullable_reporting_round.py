"""non nullable reporting round

Revision ID: 043_non_nullable_reporting_round
Revises: 042_nullable_reporting_round_col
Create Date: 2024-09-24 10:24:50.745276

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "043_non_nullable_reporting_round"
down_revision = "042_nullable_reporting_round_col"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("programme_junction", schema=None) as batch_op:
        batch_op.alter_column("reporting_round_id", existing_type=sa.UUID(), nullable=False)

    with op.batch_alter_table("submission_dim", schema=None) as batch_op:
        batch_op.alter_column("reporting_round_id", existing_type=sa.UUID(), nullable=False)


def downgrade():
    with op.batch_alter_table("submission_dim", schema=None) as batch_op:
        batch_op.alter_column("reporting_round_id", existing_type=sa.UUID(), nullable=True)

    with op.batch_alter_table("programme_junction", schema=None) as batch_op:
        batch_op.alter_column("reporting_round_id", existing_type=sa.UUID(), nullable=True)
