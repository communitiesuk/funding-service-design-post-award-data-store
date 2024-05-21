"""drop submission reporting round

Revision ID: 037_drop_submission_reporting_ro
Revises: 036_nullable_reporting_round
Create Date: 2024-05-21 16:58:51.214292

"""

import sqlalchemy as sa
from alembic import op

revision = "037_drop_submission_reporting_ro"
down_revision = "036_nullable_reporting_round"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("submission_dim", schema=None) as batch_op:
        batch_op.drop_column("reporting_round")


def downgrade():
    with op.batch_alter_table("submission_dim", schema=None) as batch_op:
        batch_op.add_column(sa.Column("reporting_round", sa.INTEGER(), autoincrement=False, nullable=True))
