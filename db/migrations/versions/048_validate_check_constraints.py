"""validate check constraints

Revision ID: 048_validate_check_constraints
Revises: 047_drop_geography
Create Date: 2024-04-05 08:03:43.847606

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "048_validate_check_constraints"
down_revision = "047_drop_geography"
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
