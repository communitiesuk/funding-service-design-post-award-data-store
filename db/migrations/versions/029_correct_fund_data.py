"""empty message

Revision ID: 029_correct_fund_data
Revises: 028_normalise_fund_ref_data
Create Date: 2024-04-23 09:41:50.279834

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "029_correct_fund_data"
down_revision = "028_normalise_fund_ref_data"
branch_labels = None
depends_on = None


def upgrade():
    # Update rows where funding_source_type is not 'Towns Fund'
    op.alter_column("funding", "data_blob", nullable=True)

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

    op.execute("""
        UPDATE funding
        SET data_blob = data_blob - '{funding_source_name, funding_source_type}';
    """)

    op.alter_column("funding", "data_blob", nullable=False)


def downgrade():
    # Update rows where funding_source is not 'Towns Fund'
    op.alter_column("funding", "data_blob", nullable=True)

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

    # Remove 'funding_source' and 'spend_type' keys from data_blob
    op.execute("""
        UPDATE funding
        SET data_blob = data_blob - '{funding_source, spend_type}';
    """)

    op.alter_column("funding", "data_blob", nullable=False)
