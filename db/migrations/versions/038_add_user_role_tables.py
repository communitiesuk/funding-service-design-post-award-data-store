"""Create user, role and user_programme_role tables

Revision ID: 038_add_user_role_tables
Revises: 037_add_pending_submission_table
Create Date: 2024-06-28 10:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

import core

# revision identifiers, used by Alembic.
revision = "038_add_user_role_tables"
down_revision = "037_add_pending_submission_table"
branch_labels = None
depends_on = None


def upgrade():
    # Create user table
    op.create_table(
        "user",
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.Column("email_address", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("phone_number", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user")),
        sa.UniqueConstraint("email_address", name=op.f("uq_user_email")),
    )

    # Create role table
    op.create_table(
        "role",
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_role")),
        sa.UniqueConstraint("name", name=op.f("uq_role_name")),
    )

    # Create user_programme_role table
    op.create_table(
        "user_programme_role",
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.Column("user_id", core.db.types.GUID(), nullable=False),
        sa.Column("programme_id", core.db.types.GUID(), nullable=False),
        sa.Column("role_id", core.db.types.GUID(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_programme_role")),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], name=op.f("fk_user_programme_role_user_id_user")),
        sa.ForeignKeyConstraint(
            ["programme_id"], ["programme_dim.id"], name=op.f("fk_user_programme_role_programme_id_programme")
        ),
        sa.ForeignKeyConstraint(["role_id"], ["role.id"], name=op.f("fk_user_programme_role_role_id_role")),
    )


def downgrade():
    op.drop_table("user_programme_role")
    op.drop_table("role")
    op.drop_table("user")
