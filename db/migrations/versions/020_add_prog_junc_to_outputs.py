"""020_add_prog_junc_to_outputs

Revision ID: 020_add_prog_junc_to_outputs
Revises: 019_outputs_outcomes_jsonb
Create Date: 2024-03-12 08:48:35.948533

"""

import sqlalchemy as sa
from alembic import op

import data_store

# revision identifiers, used by Alembic.
revision = "020_add_prog_junc_to_outputs"
down_revision = "019_outputs_outcomes_jsonb"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("output_data", schema=None) as batch_op:
        batch_op.add_column(sa.Column("programme_junction_id", data_store.db.types.GUID(), nullable=True))
        batch_op.alter_column("project_id", existing_type=sa.UUID(), nullable=True)
        batch_op.create_index("ix_output_join_programme_junction", ["programme_junction_id"], unique=False)
        batch_op.create_foreign_key(
            batch_op.f("fk_output_data_programme_junction_id_programme_junction"),
            "programme_junction",
            ["programme_junction_id"],
            ["id"],
            ondelete="CASCADE",
        )

    # ### end Alembic commands ###


def downgrade():
    with op.batch_alter_table("output_data", schema=None) as batch_op:
        batch_op.drop_constraint(
            batch_op.f("fk_output_data_programme_junction_id_programme_junction"), type_="foreignkey"
        )
        batch_op.drop_index("ix_output_join_programme_junction")
        batch_op.alter_column("project_id", existing_type=sa.UUID(), nullable=False)
        batch_op.drop_column("programme_junction_id")

    # ### end Alembic commands ###
