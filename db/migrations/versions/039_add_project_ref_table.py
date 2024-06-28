"""users and projects

Revision ID: 039_add_project_ref_table
Revises: 038_add_user_role_tables
Create Date: 2024-06-06 19:55:09.899505

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

import core

# revision identifiers, used by Alembic.
revision = "039_add_project_ref_table"
down_revision = "038_add_user_role_tables"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "project_ref",
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.Column("programme_id", core.db.types.GUID(), nullable=False),
        sa.Column("project_code", sa.String(), nullable=False),
        sa.Column("project_name", sa.String(), nullable=False),
        sa.Column("state", sa.Enum("ACTIVE", "CANCELLED", "COMPLETED", name="projectstatusenum"), nullable=False),
        sa.Column("data_blob", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_ref")),
        sa.ForeignKeyConstraint(
            ["programme_id"], ["programme_dim.id"], name=op.f("fk_project_ref_programme_id_programme")
        ),
        sa.UniqueConstraint("project_code", name=op.f("uq_project_ref_project_code")),
    )


def downgrade():
    op.drop_table("project_ref")
