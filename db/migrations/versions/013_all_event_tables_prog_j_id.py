"""empty message

Revision ID: 013_all_event_tables_prog_j_id
Revises: 012_event_data_to_jsonb
Create Date: 2024-02-26 10:29:11.913211

"""

import sqlalchemy as sa
from alembic import op

import core

# revision identifiers, used by Alembic.
revision = "013_all_event_tables_prog_j_id"
down_revision = "012_event_data_to_jsonb"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("funding", schema=None) as batch_op:
        batch_op.add_column(sa.Column("programme_junction_id", core.db.types.GUID(), nullable=True))
        batch_op.alter_column("project_id", existing_type=sa.UUID(), nullable=True)
        batch_op.create_index("ix_funding_join_programme_junction", ["programme_junction_id"], unique=False)
        batch_op.create_foreign_key(
            batch_op.f("fk_funding_programme_junction_id_programme_junction"),
            "programme_junction",
            ["programme_junction_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table("funding", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("fk_funding_programme_junction_id_programme_junction"), type_="foreignkey")
        batch_op.drop_index("ix_funding_join_programme_junction")
        # NOTE: as of 27/02/2024 there are no rows in Funding with a null project_id
        # future funds may contain such data, and will downgrade will fail
        batch_op.alter_column("project_id", existing_type=sa.UUID(), nullable=False)
        batch_op.drop_column("programme_junction_id")

    # ### end Alembic commands ###
