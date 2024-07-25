"""empty message

Revision ID: 017_add_pfc_table
Revises: 016_rename_event_data_blob
Create Date: 2024-02-28 11:16:58.767143

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

import data_store

# revision identifiers, used by Alembic.
revision = "017_add_pfc_table"
down_revision = "016_rename_event_data_blob"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "project_finance_change",
        sa.Column("programme_junction_id", data_store.db.types.GUID(), nullable=True),
        sa.Column("data_blob", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("id", data_store.db.types.GUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["programme_junction_id"],
            ["programme_junction.id"],
            name=op.f("fk_project_finance_change_programme_junction_id_programme_junction"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_project_finance_change")),
    )
    with op.batch_alter_table("project_finance_change", schema=None) as batch_op:
        batch_op.create_index(
            "ix_project_finance_change_join_programme_junction", ["programme_junction_id"], unique=True
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("project_finance_change", schema=None) as batch_op:
        batch_op.drop_index("ix_project_finance_change_join_programme_junction")

    op.drop_table("project_finance_change")
    # ### end Alembic commands ###
