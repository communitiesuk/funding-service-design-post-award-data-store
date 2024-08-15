"""Add ReportingRound entity and related changes

Revision ID: 040_add_reporting_round_id
Revises: 039_add_reporting_round
Create Date: 2024-08-15 11:18:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "040_add_reporting_round_id"
down_revision = "039_add_reporting_round"
branch_labels = None
depends_on = None


def upgrade():
    """
    This migration needs to be run after the reporting_round table has been created and populated with data, which will
    require the deployment of the PR containing the 039_add_reporting_round migration and the reporting round seeding
    logic.
    """

    # Update reporting_round_id in submission_dim
    op.execute("""
        UPDATE submission_dim AS sd
        SET reporting_round_id = rr.id
        FROM reporting_round AS rr
            JOIN programme_dim AS pd
                ON rr.fund_id = pd.fund_type_id
                    JOIN programme_junction AS pj
                        ON pd.id = pj.programme_id
                            AND rr.round_number = pj.reporting_round
        WHERE sd.id = pj.submission_id
    """)

    # Update reporting_round_id in programme_junction
    op.execute("""
        UPDATE programme_junction AS pj
        SET reporting_round_id = rr.id
        FROM reporting_round AS rr
            JOIN programme_dim AS pd
                ON rr.fund_id = pd.fund_type_id
        WHERE pj.programme_id = pd.id
        AND pj.reporting_round = rr.round_number
    """)


def downgrade():
    pass
