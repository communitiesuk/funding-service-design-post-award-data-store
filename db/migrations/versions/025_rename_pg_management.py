"""empty message

Revision ID: 025_rename_pg_management
Revises: 024_jsonb_nullabilities
Create Date: 2024-03-25 12:08:34.011516

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "025_rename_pg_management"
down_revision = "024_jsonb_nullabilities"
branch_labels = None
depends_on = None


def upgrade():
    conn = op.get_bind()
    existing_metadata = sa.schema.MetaData()

    # Rename table.
    new_name = "programme_funding_management"
    op.rename_table("programme_management", new_name)

    # rename FK (by dropping and rebuilding)
    existing_table = sa.Table(new_name, existing_metadata, autoload_with=conn)
    for c in existing_table.foreign_key_constraints:
        op.drop_constraint(c.name, new_name)

    with op.batch_alter_table("programme_funding_management", schema=None) as batch_op:
        batch_op.create_foreign_key(
            batch_op.f("fk_programme_funding_management_programme_junction_id_programme_junction"),
            "programme_junction",
            ["programme_junction_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # rename indexes (including PK)
    op.execute("ALTER INDEX pk_programme_management RENAME TO pk_programme_funding_management")
    op.execute(
        (
            "ALTER INDEX ix_programme_management_join_programme_junction "
            "RENAME TO ix_programme_funding_management_join_programme_junction"
        )
    )


def downgrade():
    # Rename table.
    new_name = "programme_management"
    op.rename_table("programme_funding_management", new_name)

    with op.batch_alter_table("programme_management", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_programme_funding_management_programme_junction_id_programme_junction"), type_="foreignkey"
        )
        batch_op.create_foreign_key(
            "fk_programme_management_programme_junction_id", "programme_junction", ["programme_junction_id"], ["id"]
        )

    op.execute("ALTER INDEX pk_programme_funding_management RENAME TO pk_programme_management")
    op.execute(
        (
            "ALTER INDEX ix_programme_funding_management_join_programme_junction "
            "RENAME TO ix_programme_management_join_programme_junction"
        )
    )
