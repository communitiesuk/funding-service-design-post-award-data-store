"""geospatial_itl1_region_name

Revision ID: 034_geospatial_itl1_region_name
Revises: 033_project_geospatial_data
Create Date: 2024-05-14 15:29:16.434871

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "034_geospatial_itl1_region_name"
down_revision = "033_project_geospatial_data"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("geospatial_dim", schema=None) as batch_op:
        batch_op.add_column(sa.Column("itl1_region_name", sa.String(), nullable=True))
        batch_op.alter_column("data_blob", existing_type=postgresql.JSONB(astext_type=sa.Text()), nullable=True)

    op.execute(
        """
            UPDATE geospatial_dim
            SET
                itl1_region_name = (data_blob ->> 'itl1_region_name')::VARCHAR
        """
    )

    op.execute(
        """
            UPDATE geospatial_dim
            SET itl1_region_name = 'Yorkshire and The Humber'
            WHERE itl1_region_name = 'Yorkshire';
        """
    )

    with op.batch_alter_table("geospatial_dim", schema=None) as batch_op:
        batch_op.alter_column("itl1_region_name", nullable=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("geospatial_dim", schema=None) as batch_op:
        batch_op.drop_column("itl1_region_name")

    # ### end Alembic commands ###
