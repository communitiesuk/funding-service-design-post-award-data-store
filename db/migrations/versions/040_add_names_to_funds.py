"""add names to funds

Revision ID: 040_add_names_to_funds
Revises: 039_add_permissions_table
Create Date: 2024-06-10 12:03:38.726236

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "040_add_names_to_funds"
down_revision = "039_add_permissions_table"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("fund_dim", schema=None) as batch_op:
        batch_op.add_column(sa.Column("fund_name", sa.String(), nullable=True))

    op.execute("UPDATE fund_dim SET fund_name = fund_code")

    with op.batch_alter_table("fund_dim", schema=None) as batch_op:
        batch_op.alter_column("fund_name", existing_type=sa.String(), nullable=False)
        batch_op.create_unique_constraint(batch_op.f("uq_fund_dim_fund_name"), ["fund_name"])

    with op.batch_alter_table("user_permission_junction_table", schema=None) as batch_op:
        batch_op.drop_index("ix_user_and_org")
        batch_op.create_index(
            "ix_user_and_org",
            ["user_id", "organisation_id"],
            unique=True,
            postgresql_where=sa.text("programme_id IS NOT NULL"),
        )


def downgrade():
    with op.batch_alter_table("user_permission_junction_table", schema=None) as batch_op:
        batch_op.drop_index("ix_user_and_org", postgresql_where=sa.text("programme_id IS NOT NULL"))
        batch_op.create_index("ix_user_and_org", ["user_id", "programme_id"], unique=False)

    with op.batch_alter_table("fund_dim", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("uq_fund_dim_fund_name"), type_="unique")
        batch_op.drop_column("fund_name")
