"""empty message

Revision ID: 026_standardise_actual_forecast
Revises: 025_rename_pg_management
Create Date: 2024-03-28 15:49:44.420890

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "026_standardise_actual_forecast"
down_revision = "025_rename_pg_management"
branch_labels = None
depends_on = None


def upgrade():
    # 'status' in Funding's data_blob to 'state'
    op.execute(
        """
        UPDATE funding
        SET data_blob = jsonb_set(data_blob, '{state}', data_blob->'status', true)
        WHERE data_blob ? 'status';

        UPDATE funding
        SET data_blob = data_blob - 'status'
        WHERE data_blob ? 'status';
        """
    )


def downgrade():
    op.execute(
        """
        UPDATE funding
        SET data_blob = jsonb_set(data_blob, '{status}', data_blob->'state', true)
        WHERE data_blob ? 'state';

        UPDATE funding
        SET data_blob = data_blob - 'state'
        WHERE data_blob ? 'state';
        """
    )
