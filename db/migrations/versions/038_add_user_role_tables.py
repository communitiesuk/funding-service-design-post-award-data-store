"""Create user, role and user_programme_role tables

Revision ID: 038_add_user_role_tables
Revises: 037_add_raw_submission_table
Create Date: 2024-06-28 10:00:00.000000

"""

import sqlalchemy as sa
from alembic import op

import core

# revision identifiers, used by Alembic.
revision = "038_add_user_role_tables"
down_revision = "037_add_raw_submission_table"
branch_labels = None
depends_on = None

# Controlled UUIDs
USER_ID = "00000000-0000-0000-0000-000000000000"
REPORTER_ROLE_ID = "1a2b3c4d-5e6f-4a5b-6c7d-8e9f0a1b2c3d"
S151_ROLE_ID = "2b3c4d5e-6f7a-8b9c-0d1e-2f3a4b5c6d7e"


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

    # Seed user
    op.execute(f"""
    INSERT INTO "user" (id, email_address, full_name, phone_number)
    VALUES ('{USER_ID}', 'dev@communities.gov.uk', 'Dev User', '1234567890')
    """)

    # Seed roles
    op.execute(f"""
    INSERT INTO role (id, name, description)
    VALUES
        ('{REPORTER_ROLE_ID}', 'Reporter', 'User who can report on programmes'),
        ('{S151_ROLE_ID}', 'Section 151 Officer', 'User with Section 151 Officer responsibilities')
    """)


def downgrade():
    # Remove seeded data
    op.execute(f"DELETE FROM role WHERE id IN ('{REPORTER_ROLE_ID}', '{S151_ROLE_ID}')")
    op.execute(f"DELETE FROM user WHERE id = '{USER_ID}'")

    # Drop tables
    op.drop_table("user_programme_role")
    op.drop_table("role")
    op.drop_table("user")
