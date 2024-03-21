"""021_outcome_end_date_nullable

Revision ID: 021_outcome_end_date_nullable
Revises: 020_add_prog_junc_to_outputs
Create Date: 2024-03-12 15:57:07.389550

"""

from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "021_outcome_end_date_nullable"
down_revision = "020_add_prog_junc_to_outputs"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("outcome_data", schema=None) as batch_op:
        batch_op.alter_column("end_date", existing_type=postgresql.TIMESTAMP(), nullable=True)

    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table("outcome_data", schema=None) as batch_op:
        batch_op.alter_column("end_date", existing_type=postgresql.TIMESTAMP(), nullable=False)

    # ### end Alembic commands ###
