"""programme junction reporting round

Revision ID: 030_programme_junction_reporting
Revises: 029_add_account_id_and_email
Create Date: 2024-05-08 08:13:55.775613

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "030_programme_junction_reporting"
down_revision = "029_add_account_id_and_email"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("programme_junction", schema=None) as batch_op:
        batch_op.add_column(sa.Column("reporting_round", sa.Integer(), nullable=True))
        batch_op.create_unique_constraint(
            batch_op.f("uq_programme_junction_unique_submission_per_round"),
            ["programme_id", "reporting_round"],
        )


def downgrade():
    with op.batch_alter_table("programme_junction", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("uq_programme_junction_unique_submission_per_round"), type_="unique")
        batch_op.drop_column("reporting_round")
