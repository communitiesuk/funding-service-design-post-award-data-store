"""empty message

Revision ID: 009_postcode_as_array
Revises: 008_add_new_round_4_cols
Create Date: 2023-11-16 17:22:58.496260

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "009_postcode_as_array"
down_revision = "008_add_new_round_4_cols"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("project_dim", schema=None) as batch_op:
        batch_op.add_column(sa.Column("postcode_list", sa.ARRAY(sa.VARCHAR()), nullable=True))
    op.execute("UPDATE project_dim SET postcode_list = STRING_TO_ARRAY(postcodes, ',')")

    with op.batch_alter_table("project_dim", schema=None) as batch_op:
        batch_op.drop_column("postcodes")
        batch_op.alter_column("postcode_list", new_column_name="postcodes")


def downgrade():
    with op.batch_alter_table("project_dim", schema=None) as batch_op:
        batch_op.add_column(sa.Column("postcodes_str", sa.ARRAY(sa.VARCHAR()), nullable=True))
    op.execute("UPDATE project_dim SET postcode_str = ARRAY_TO_STRING(postcodes, ',')")

    with op.batch_alter_table("project_dim", schema=None) as batch_op:
        batch_op.drop_column("postcodes")
        batch_op.alter_column("postcode_str", new_column_name="postcodes")
