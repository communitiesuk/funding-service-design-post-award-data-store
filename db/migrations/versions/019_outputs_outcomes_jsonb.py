"""empty message

Revision ID: 019_outputs_outcomes_jsonb
Revises: 018_fix_pfc_table
Create Date: 2024-02-27 15:49:44.420890

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "019_outputs_outcomes_jsonb"
down_revision = "018_fix_pfc_table"
branch_labels = None
depends_on = None


def upgrade():
    # OUTPUT_DATA #
    with op.batch_alter_table("output_data", schema=None) as batch_op:
        batch_op.add_column(sa.Column("data_blob", postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    op.execute(
        """
            UPDATE output_data
            SET data_blob = jsonb_build_object(
                'unit_of_measurement', unit_of_measurement,
                'state', state,
                'amount', amount,
                'additional_information', additional_information
            )
        """
    )

    with op.batch_alter_table("output_data", schema=None) as batch_op:
        batch_op.drop_column("unit_of_measurement")
        batch_op.drop_column("state")
        batch_op.drop_column("amount")
        batch_op.drop_column("additional_information")

    # OUTCOME_DATA #
    with op.batch_alter_table("outcome_data", schema=None) as batch_op:
        batch_op.add_column(sa.Column("data_blob", postgresql.JSONB(astext_type=sa.Text()), nullable=True))

    op.execute(
        """
            UPDATE outcome_data
            SET data_blob = jsonb_build_object(
                'unit_of_measurement', unit_of_measurement,
                'geography_indicator', geography_indicator,
                'amount', amount,
                'state', state,
                'higher_frequency', higher_frequency
            )
        """
    )

    with op.batch_alter_table("outcome_data", schema=None) as batch_op:
        batch_op.drop_column("unit_of_measurement")
        batch_op.drop_column("state")
        batch_op.drop_column("amount")
        batch_op.drop_column("geography_indicator")
        batch_op.drop_column("higher_frequency")

    # ### end Alembic commands ###


def downgrade():
    # OUTPUT_DATA #
    with op.batch_alter_table("output_data", schema=None) as batch_op:
        batch_op.add_column(sa.Column("unit_of_measurement", sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column("state", sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column("amount", sa.FLOAT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column("additional_information", sa.VARCHAR(), autoincrement=False, nullable=True))

    op.execute(
        """
            UPDATE output_data
            SET
                unit_of_measurement = (data_blob ->> 'unit_of_measurement')::VARCHAR,
                state = (data_blob ->> 'state')::VARCHAR,
                amount = (data_blob ->> 'amount')::FLOAT,
                additional_information = (data_blob ->> 'additional_information')::VARCHAR
        """
    )

    with op.batch_alter_table("output_data", schema=None) as batch_op:
        batch_op.alter_column("unit_of_measurement", nullable=False)

    with op.batch_alter_table("output_data", schema=None) as batch_op:
        batch_op.drop_column("data_blob")

    # OUTCOME_DATA #
    with op.batch_alter_table("outcome_data", schema=None) as batch_op:
        batch_op.add_column(sa.Column("unit_of_measurement", sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column("geography_indicator", sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column("amount", sa.FLOAT(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column("state", sa.VARCHAR(), autoincrement=False, nullable=True))
        batch_op.add_column(sa.Column("higher_frequency", sa.VARCHAR(), autoincrement=False, nullable=True))

    op.execute(
        """
            UPDATE outcome_data
            SET
                unit_of_measurement = (data_blob ->> 'unit_of_measurement')::VARCHAR,
                state = (data_blob ->> 'state')::VARCHAR,
                amount = (data_blob ->> 'amount')::FLOAT,
                geography_indicator = (data_blob ->> 'geography_indicator')::VARCHAR,
                higher_frequency = (data_blob ->> 'higher_frequency')::VARCHAR
        """
    )

    with op.batch_alter_table("outcome_data", schema=None) as batch_op:
        batch_op.alter_column("unit_of_measurement", nullable=False)

    with op.batch_alter_table("outcome_data", schema=None) as batch_op:
        batch_op.drop_column("data_blob")

    # ### end Alembic commands ###
