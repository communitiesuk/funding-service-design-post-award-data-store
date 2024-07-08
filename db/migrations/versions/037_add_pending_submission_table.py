"""add pending submission table

Revision ID: 037_add_pending_submission_table
Revises: 036_nullable_reporting_round
Create Date: 2024-06-05 19:22:29.955409

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

import core

# revision identifiers, used by Alembic.
revision = "037_add_pending_submission_table"
down_revision = "036_nullable_reporting_round"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "pending_submission",
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.Column("programme_id", core.db.types.GUID(), nullable=False),
        sa.Column("reporting_round", sa.Integer(), nullable=False),
        sa.Column("data_blob", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_pending_submission")),
        sa.ForeignKeyConstraint(
            ["programme_id"], ["programme_dim.id"], name=op.f("fk_pending_submission_programme_id_programme")
        ),
        sa.UniqueConstraint("programme_id", "reporting_round", name=op.f("uq_pending_submission_programme_round")),
    )


def downgrade():
    op.drop_table("pending_submission")
