"""add names to funds

Revision ID: 040_add_names_to_funds
Revises: 039_add_project_ref_table
Create Date: 2024-06-10 12:03:38.726236

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "040_add_names_to_funds"
down_revision = "039_add_project_ref_table"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("fund_dim", schema=None) as batch_op:
        batch_op.add_column(sa.Column("fund_name", sa.String(), nullable=True))

    op.execute("UPDATE fund_dim SET fund_name = fund_code")

    with op.batch_alter_table("fund_dim", schema=None) as batch_op:
        batch_op.alter_column("fund_name", existing_type=sa.String(), nullable=False)
        batch_op.create_unique_constraint(batch_op.f("uq_fund_dim_fund_name"), ["fund_name"])


def downgrade():
    with op.batch_alter_table("fund_dim", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("uq_fund_dim_fund_name"), type_="unique")
        batch_op.drop_column("fund_name")
