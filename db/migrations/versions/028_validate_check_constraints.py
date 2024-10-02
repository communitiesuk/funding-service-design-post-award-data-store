"""validate check constraints

Revision ID: 045_validate_check_constraints
Revises: 044_remove_old_rr_cols
Create Date: 2024-04-05 08:03:43.847606

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "045_validate_check_constraints"
down_revision = "044_remove_old_rr_cols"
branch_labels = None
depends_on = None


def upgrade():
    for table in [
        "funding",
        "programme_funding_management",
        "project_progress",
        "outcome_data",
        "output_data",
    ]:
        op.execute(f"ALTER TABLE {table} VALIDATE CONSTRAINT ck_{table}_start_before_end")


def downgrade():
    pass
