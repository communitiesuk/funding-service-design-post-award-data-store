"""Add ReportingRound entity and related changes

Revision ID: 039_add_reporting_round
Revises: 038_correct_fund_data
Create Date: 2024-07-19 15:55:00.000000

"""

import sqlalchemy as sa
from alembic import op

import data_store

# revision identifiers, used by Alembic.
revision = "039_add_reporting_round"
down_revision = "038_correct_fund_data"
branch_labels = None
depends_on = None


def upgrade():
    # Create reporting_round table
    op.create_table(
        "reporting_round",
        sa.Column("id", data_store.db.types.GUID(), nullable=False),
        sa.Column("round_number", sa.Integer(), nullable=False),
        sa.Column("fund_id", data_store.db.types.GUID(), nullable=False),
        sa.Column("observation_period_start", sa.DateTime(), nullable=False),
        sa.Column("observation_period_end", sa.DateTime(), nullable=False),
        sa.Column("submission_period_start", sa.DateTime(), nullable=True),
        sa.Column("submission_period_end", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["fund_id"],
            ["fund_dim.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fund_id", "round_number", name="uq_fund_round_number"),
    )

    # Add check constraint for chronological order of dates
    op.create_check_constraint(
        "dates_chronological_order",
        "reporting_round",
        "(observation_period_start <= observation_period_end) AND "
        "(observation_period_end <= submission_period_start) AND "
        "(submission_period_start <= submission_period_end)",
    )

    # Add reporting_round_id to programme_junction
    op.add_column("programme_junction", sa.Column("reporting_round_id", data_store.db.types.GUID(), nullable=True))
    op.create_foreign_key(None, "programme_junction", "reporting_round", ["reporting_round_id"], ["id"])

    # Add reporting_round_id to submission_dim
    op.add_column("submission_dim", sa.Column("reporting_round_id", data_store.db.types.GUID(), nullable=True))
    op.create_foreign_key(None, "submission_dim", "reporting_round", ["reporting_round_id"], ["id"])

    # Populate reporting_round with existing table data
    op.execute("""
    INSERT INTO reporting_round(
        id, round_number, fund_id, observation_period_start, observation_period_end, submission_period_start,
        submission_period_end
    )
    SELECT
		gen_random_uuid() AS id,
		pj.reporting_round AS round_number,
		fd.id AS fund_id,
		sd.reporting_period_start AS observation_period_start,
		date_trunc('day', sd.reporting_period_end) + INTERVAL '1 day' - INTERVAL '1 second' AS observation_period_end,
		NULL AS submission_period_start,
		NULL AS submission_period_end
    FROM public.submission_dim AS sd
        JOIN public.programme_junction AS pj ON sd.id = pj.submission_id
        JOIN public.programme_dim AS pd ON pj.programme_id = pd.id
        JOIN public.fund_dim AS fd ON pd.fund_type_id = fd.id
    GROUP BY
        pj.reporting_round,
        fund_id,
        observation_period_start,
        observation_period_end
    """)

    # Update submission_period_end based on previous hard-coded dates from `fund.py` in what was the `submit` repo
    op.execute("""
        UPDATE reporting_round AS rr
        SET submission_period_end =
            CASE
                WHEN fd.fund_code IN ('HS', 'TD') AND rr.round_number = 4 THEN '2023-12-04 23:59:59'::timestamp
                WHEN fd.fund_code IN ('HS', 'TD') AND rr.round_number = 5 THEN '2024-05-28 23:59:59'::timestamp
                WHEN fd.fund_code = 'PF' AND rr.round_number = 1 THEN '2024-04-30 23:59:59'::timestamp
                ELSE NULL
            END
        FROM fund_dim AS fd
        WHERE rr.fund_id = fd.id;
    """)

    # Update reporting_round_id in submission_dim
    op.execute("""
        UPDATE submission_dim AS sd
        SET reporting_round_id = rr.id
        FROM reporting_round AS rr
            JOIN programme_junction AS pj ON sd.id = pj.submission_id
            JOIN programme_dim AS pd ON pj.programme_id = pd.id
            JOIN fund_dim AS fd ON pd.fund_type_id = fd.id
        WHERE rr.fund_id = fd.id
            AND rr.round_number = pj.reporting_round
            AND rr.observation_period_start = sd.reporting_period_start
            AND rr.observation_period_end = sd.reporting_period_end
    """)

    # Update reporting_round_id in programme_junction
    op.execute("""
        UPDATE programme_junction AS pj
        SET reporting_round_id = rr.id
        FROM reporting_round AS rr
            JOIN programme_dim AS pd ON pj.programme_id = pd.id
            JOIN fund_dim AS fd ON pd.fund_type_id = fd.id
        WHERE rr.fund_id = fd.id
            AND rr.round_number = pj.reporting_round
    """)


def downgrade():
    # Remove reporting_round_id from submission_dim
    op.drop_constraint(None, "submission_dim", type_="foreignkey")
    op.drop_column("submission_dim", "reporting_round_id")

    # Remove reporting_round_id from programme_junction
    op.drop_constraint(None, "programme_junction", type_="foreignkey")
    op.drop_column("programme_junction", "reporting_round_id")

    # Drop reporting_round table
    op.drop_table("reporting_round")
