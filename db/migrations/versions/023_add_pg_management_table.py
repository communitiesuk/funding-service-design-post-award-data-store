"""empty message

Revision ID: 023_add_pg_management_table
Revises: 022_add_geospatial_dim_table
Create Date: 2024-03-20 11:35:48.714492

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

import data_store

# revision identifiers, used by Alembic.
revision = "023_add_pg_management_table"
down_revision = "022_add_geospatial_dim_table"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "programme_management",
        sa.Column("programme_junction_id", data_store.db.types.GUID(), nullable=False),
        sa.Column("data_blob", postgresql.JSONB(astext_type=sa.Text()), nullable=False),
        sa.Column("id", data_store.db.types.GUID(), nullable=False),
        sa.Column("start_date", sa.DateTime(), nullable=True),
        sa.Column("end_date", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["programme_junction_id"],
            ["programme_junction.id"],
            name=op.f("fk_programme_management_programme_junction_id_programme_junction"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_programme_management")),
    )
    with op.batch_alter_table("programme_management", schema=None) as batch_op:
        batch_op.create_index(
            "ix_programme_management_join_programme_junction", ["programme_junction_id"], unique=False
        )

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("programme_management", schema=None) as batch_op:
        batch_op.drop_index("ix_programme_management_join_programme_junction")

    op.drop_table("programme_management")
    # ### end Alembic commands ###
