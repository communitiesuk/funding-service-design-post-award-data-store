"""nullable output data and outcome data start date

Revision ID: 045_nullable_output_outcome_star
Revises: 044_remove_old_rr_cols
Create Date: 2024-09-26 11:02:00.000000

"""

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "045_nullable_output_outcome_star"
down_revision = "044_remove_old_rr_cols"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("output_data", schema=None) as batch_op:
        batch_op.alter_column("start_date", existing_type=postgresql.TIMESTAMP(), nullable=True)
        batch_op.drop_constraint("start_before_end", type_="check")
        batch_op.create_check_constraint(
            "start_before_end",
            "((start_date IS NULL) OR (end_date IS NULL) OR (start_date <= end_date))",
        )

    with op.batch_alter_table("outcome_data", schema=None) as batch_op:
        batch_op.alter_column("start_date", existing_type=postgresql.TIMESTAMP(), nullable=True)
        batch_op.drop_constraint("start_before_end", type_="check")
        batch_op.create_check_constraint(
            "start_before_end",
            "((start_date IS NULL) OR (end_date IS NULL) OR (start_date <= end_date))",
        )


def downgrade():
    with op.batch_alter_table("output_data", schema=None) as batch_op:
        batch_op.alter_column("start_date", existing_type=postgresql.TIMESTAMP(), nullable=False)
        batch_op.drop_constraint("start_before_end", type_="check")
        batch_op.create_check_constraint(
            "start_before_end",
            "(start_date <= end_date)",
        )

    with op.batch_alter_table("outcome_data", schema=None) as batch_op:
        batch_op.alter_column("start_date", existing_type=postgresql.TIMESTAMP(), nullable=False)
        batch_op.drop_constraint("start_before_end", type_="check")
        batch_op.create_check_constraint(
            "start_before_end",
            "(start_date <= end_date)",
        )
