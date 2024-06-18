"""empty message

Revision ID: 028_normalise_fund_ref_data
Revises: 027_start_date_before_end
Create Date: 2024-04-23 09:41:50.279834

"""

import sqlalchemy as sa
from alembic import op

import core

# revision identifiers, used by Alembic.
revision = "028_normalise_fund_ref_data"
down_revision = "027_start_date_before_end"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "fund_dim",
        sa.Column("fund_code", sa.String(), nullable=False),
        sa.Column("id", core.db.types.GUID(), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_fund_dim")),
        sa.UniqueConstraint("fund_code", name=op.f("uq_fund_dim_fund_code")),
    )

    # The SQL insert statement below has been commented out to remove the data insert from this migration
    # script. It is already present in deployed environments, and in the case of new deployments can be seeded
    # via flask CLI commands. Flask CLI commands will also be used to seed new db containers in local development,
    # and we should not use alembic migrations to insert data again.

    # This insert statement should not be commented back in to the migration.

    # op.execute(
    #     """
    #     INSERT INTO fund_dim (id, fund_code)
    #     VALUES
    #     ('4a6e9f7d-fc9d-4c12-b1b6-89e784c310e1', 'HS'),
    #     ('9fde58b2-8a89-4b2c-af7d-1f968b03c7b9', 'TD'),
    #     ('e8c7c1c8-90d3-4b2d-aa50-4a2d4091d4f3', 'PF');
    #     """
    # )

    op.add_column("programme_dim", sa.Column("temp", core.db.types.GUID(), nullable=True))

    op.execute(
        """
        UPDATE programme_dim AS p
        SET temp = f.id
        FROM fund_dim AS f
        WHERE p.fund_type_id = f.fund_code;
        """
    )

    with op.batch_alter_table("programme_dim", schema=None) as batch_op:
        batch_op.drop_index("ix_programme_filter_fund_type")
        batch_op.drop_column("fund_type_id")
        batch_op.alter_column("temp", new_column_name="fund_type_id", nullable=False)
        batch_op.create_foreign_key(
            batch_op.f("fk_programme_dim_fund_type_id_fund_dim"), "fund_dim", ["fund_type_id"], ["id"]
        )
        batch_op.create_index("ix_programme_join_fund_type", ["fund_type_id"], unique=False)
        batch_op.create_index("ix_unique_programme_name_per_fund", ["programme_name", "fund_type_id"], unique=True)

    # ### end Alembic commands ###


def downgrade():
    op.add_column("programme_dim", sa.Column("temp", sa.String(), nullable=True))

    op.execute(
        """
        UPDATE programme_dim AS p
        SET temp = f.fund_code
        FROM fund_dim AS f
        WHERE p.fund_type_id = f.id;
        """
    )

    with op.batch_alter_table("programme_dim", schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f("fk_programme_dim_fund_type_id_fund_dim"), type_="foreignkey")
        batch_op.drop_index("ix_programme_join_fund_type")
        batch_op.drop_index("ix_unique_programme_name_per_fund")
        batch_op.drop_column("fund_type_id")
        batch_op.alter_column("temp", new_column_name="fund_type_id", nullable=False)
        batch_op.create_index("ix_programme_filter_fund_type", ["fund_type_id"], unique=False)

    op.drop_table("fund_dim")
    # ### end Alembic commands ###
