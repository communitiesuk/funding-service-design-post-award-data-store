"""nullable reporting_round

Revision ID: 036_nullable_reporting_round
Revises: 035_drop_geospatial_data_blob
Create Date: 2024-05-14 09:01:17.945873

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "036_nullable_reporting_round"
down_revision = "035_drop_geospatial_data_blob"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("submission_dim", schema=None) as batch_op:
        batch_op.alter_column("reporting_round", existing_type=sa.INTEGER(), nullable=True)


def downgrade():
    with op.batch_alter_table("submission_dim", schema=None) as batch_op:
        batch_op.alter_column("reporting_round", existing_type=sa.INTEGER(), nullable=False)
