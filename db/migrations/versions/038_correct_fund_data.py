"""migrate funding data to new format

Revision ID: 038_correct_fund_data
Revises: 037_drop_submission_reporting_ro
Create Date: 2024-04-23 09:41:50.279834

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "038_correct_fund_data"
down_revision = "037_drop_submission_reporting_ro"
branch_labels = None
depends_on = None


def upgrade():
    # Pathfinders sometimes has no funding_source_name if so set default
    op.execute("""
        UPDATE funding
        SET data_blob = jsonb_set(
            data_blob,
            '{funding_source_name}',
            '"Pathfinders"'
        )
        WHERE data_blob IS NULL OR NOT (data_blob ? 'funding_source_name')
        AND project_id IS NULL;
    """)

    # Update rows where funding_source_type is not 'Towns Fund'
    op.execute("""
        UPDATE funding
        SET data_blob = jsonb_set(
            jsonb_set(
                data_blob,
                '{funding_source}',
                to_jsonb(data_blob ->> 'funding_source_name'),
                true
            ),
            '{spend_type}',
            to_jsonb(data_blob ->> 'funding_source_type'),
            true
        )
        WHERE data_blob ->> 'funding_source_type' != 'Towns Fund';
    """)

    # Update rows where funding_source_type is 'Towns Fund'
    op.execute("""
        UPDATE funding
        SET data_blob = jsonb_set(
            jsonb_set(
                data_blob,
                '{funding_source}',
                to_jsonb(data_blob ->> 'funding_source_type'),
                true
            ),
            '{spend_type}',
            to_jsonb(data_blob ->> 'funding_source_name'),
            true
        )
        WHERE data_blob ->> 'funding_source_type' = 'Towns Fund';
    """)

    # Remove 'funding_source_name' and 'funding_source_type' keys from data_blob
    op.execute("""
        UPDATE funding
        SET data_blob = data_blob - 'funding_source_name' - 'funding_source_type';
    """)


def downgrade():
    # Update rows where funding_source is not 'Towns Fund'
    op.execute("""
        UPDATE funding
        SET data_blob = jsonb_set(
            jsonb_set(
                data_blob,
                '{funding_source_name}',
                to_jsonb(data_blob ->> 'funding_source'),
                true
            ),
            '{funding_source_type}',
            to_jsonb(data_blob ->> 'spend_type'),
            true
        )
        WHERE data_blob ->> 'funding_source' != 'Towns Fund';
    """)

    # Update rows where funding_source is 'Towns Fund'
    op.execute("""
        UPDATE funding
        SET data_blob = jsonb_set(
            jsonb_set(
                data_blob,
                '{funding_source_type}',
                to_jsonb(data_blob ->> 'funding_source'),
                true
            ),
            '{funding_source_name}',
            to_jsonb(data_blob ->> 'spend_type'),
            true
        )
        WHERE data_blob ->> 'funding_source' = 'Towns Fund';
    """)

    # Pathfinders sometimes has no funding_source_name if so set default
    op.execute("""
        UPDATE funding
        SET data_blob = data_blob - 'funding_source_name'
        WHERE data_blob ->> 'funding_source_name' = 'Pathfinders'
        AND project_id IS NULL;
    """)

    # Remove 'funding_source' and 'spend_type' keys from data_blob
    op.execute("""
        UPDATE funding
        SET data_blob = data_blob - 'funding_source' - 'spend_type';
    """)
