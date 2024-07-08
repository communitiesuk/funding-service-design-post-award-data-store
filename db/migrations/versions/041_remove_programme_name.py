"""remove programme name and add unique constraint on organisation_id

Revision ID: 041_remove_programme_name
Revises: 040_add_names_to_funds
Create Date: 2024-07-08 12:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "041_remove_programme_name"
down_revision = "040_add_names_to_funds"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("programme_dim", schema=None) as batch_op:
        # Drop the existing composite index
        batch_op.drop_index("ix_unique_programme_name_per_fund")

        # Remove programme_name column
        batch_op.drop_column("programme_name")

        # Add unique constraint on organisation_id
        batch_op.create_unique_constraint(batch_op.f("uq_programme_dim_organisation_id"), ["organisation_id"])


def downgrade():
    with op.batch_alter_table("programme_dim", schema=None) as batch_op:
        # Remove unique constraint on organisation_id
        batch_op.drop_constraint(batch_op.f("uq_programme_dim_organisation_id"), type_="unique")

        # Add programme_name column back
        batch_op.add_column(sa.Column("programme_name", sa.String(), nullable=True))

        # Recreate the composite index
        batch_op.create_index("ix_unique_programme_name_per_fund", ["programme_name", "fund_type_id"], unique=True)

    # Note: This downgrade doesn't restore the data for programme_name.
    # If you need to restore the data, you'll need to handle that separately.
