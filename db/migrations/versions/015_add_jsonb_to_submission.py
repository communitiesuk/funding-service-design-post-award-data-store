"""empty message

Revision ID: 015_add_jsonb_to_submission
Revises: 014_project_table_to_jsonb
Create Date: 2024-03-05 10:39:28.273690

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "015_add_jsonb_to_submission"
down_revision = "014_project_table_to_jsonb"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("submission_dim", schema=None) as batch_op:
        batch_op.add_column(sa.Column("data_blob", postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("submission_dim", schema=None) as batch_op:
        batch_op.drop_column("data_blob")

    # ### end Alembic commands ###
