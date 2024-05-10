"""programme junction reporting round

Revision ID: 031_programme_junction_2
Revises: 030_programme_junction_reporting
Create Date: 2024-05-08 08:13:55.775613

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "031_programme_junction_2"
down_revision = "030_programme_junction_reporting"
branch_labels = None
depends_on = None


def upgrade():
    op.execute(
        """
        UPDATE programme_junction pj
        SET reporting_round = sd.reporting_round
        FROM submission_dim sd
        WHERE pj.submission_id = sd.id AND pj.reporting_round IS NULL;
        """
    )

    with op.batch_alter_table("programme_junction", schema=None) as batch_op:
        batch_op.alter_column("reporting_round", existing_type=sa.INTEGER(), nullable=False)


def downgrade():
    with op.batch_alter_table("programme_junction", schema=None) as batch_op:
        batch_op.alter_column("reporting_round", existing_type=sa.INTEGER(), nullable=True)
