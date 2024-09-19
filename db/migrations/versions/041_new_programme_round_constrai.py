"""new programme+round constraint

Revision ID: 041_new_programme_round_constrai
Revises: 040_fix_check_constraints
Create Date: 2024-09-18 20:02:28.453496

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "041_new_programme_round_constrai"
down_revision = "040_fix_check_constraints"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("programme_junction", schema=None) as batch_op:
        batch_op.create_unique_constraint(
            "uq_programme_junction_programme_id_reporting_round_id", ["programme_id", "reporting_round_id"]
        )


def downgrade():
    with op.batch_alter_table("programme_junction", schema=None) as batch_op:
        batch_op.drop_constraint("uq_programme_junction_programme_id_reporting_round_id", type_="unique")
