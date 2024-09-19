"""fix check constraints - these were added to the python models but never present in an alembic migration

Revision ID: 040_fix_check_constraints
Revises: 039_add_reporting_round
Create Date: 2024-09-18 15:54:45.532357

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "040_fix_check_constraints"
down_revision = "039_add_reporting_round"
branch_labels = None
depends_on = None


def upgrade():
    for table in ["funding", "outcome_data", "output_data", "risk_register"]:
        op.create_check_constraint(
            "programme_junction_id_or_project_id",  # gets prefixed with `ck_{table}`
            table,
            (
                "("
                "(programme_junction_id IS NOT NULL AND project_id IS NULL) "
                "OR (programme_junction_id IS NULL AND project_id IS NOT NULL)"
                ")"
            ),
        )

    for table in ["funding"]:
        op.create_check_constraint(
            "start_or_end_date",
            table,
            "start_date IS NOT NULL OR end_date IS NOT NULL",
        )


def downgrade():
    for table in ["funding", "outcome_data", "output_data", "risk_register"]:
        op.drop_constraint(
            f"ck_{table}_programme_junction_id_or_project_id",
            table,
        )

    for table in ["funding"]:
        op.drop_constraint(
            f"ck_{table}_start_or_end_date",
            table,
        )
