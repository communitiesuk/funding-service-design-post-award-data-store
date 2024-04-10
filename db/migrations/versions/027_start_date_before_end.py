"""require start_dates to be before end_dates, if both fields are present in a row

Revision ID: 027_start_date_before_end
Revises: 026_standardise_actual_forecast
Create Date: 2024-04-04 13:59:15.747254

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "027_start_date_before_end"
down_revision = "026_standardise_actual_forecast"
branch_labels = None
depends_on = None


def upgrade():
    for table in ["funding", "programme_funding_management", "project_progress"]:
        op.create_check_constraint(
            "start_before_end",  # gets prefixed with `ck_{table}`
            table,
            "start_date IS NULL OR end_date IS NULL OR (start_date <= end_date)",
            postgresql_not_valid=True,
        )

    for table in ["outcome_data", "output_data"]:
        op.create_check_constraint(
            "start_before_end",  # gets prefixed with `ck_{table}`
            table,
            "(start_date <= end_date)",
            postgresql_not_valid=True,
        )

    for table in ["submission_dim"]:
        op.create_check_constraint(
            "start_before_end",  # gets prefixed with `ck_{table}`
            table,
            "(reporting_period_start <= reporting_period_end)",
            postgresql_not_valid=True,
        )


def downgrade():
    for table in [
        "funding",
        "programme_funding_management",
        "project_progress",
        "outcome_data",
        "output_data",
        "submission_dim",
    ]:
        op.drop_constraint(
            f"ck_{table}_start_before_end",
            table,
        )
