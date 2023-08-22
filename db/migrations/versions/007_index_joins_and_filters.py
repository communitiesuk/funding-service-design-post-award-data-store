"""add indexes for columns that are filtered on

Revision ID: 007_index_joins_and_filters
Revises: 006_replace_enums_with_strings
Create Date: 2023-08-22 14:55:31.044950

"""
from alembic import op

# revision identifiers, used by Alembic.
revision = "007_index_joins_and_filters"
down_revision = "006_replace_enums_with_strings"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("funding", schema=None) as batch_op:
        batch_op.create_index("ix_funding_join_project", ["project_id"], unique=False)
        batch_op.create_index("ix_funding_join_submission", ["submission_id"], unique=False)

    with op.batch_alter_table("funding_comment", schema=None) as batch_op:
        batch_op.create_index("ix_funding_comment_join_project", ["project_id"], unique=False)
        batch_op.create_index("ix_funding_comment_join_submission", ["submission_id"], unique=False)

    with op.batch_alter_table("funding_question", schema=None) as batch_op:
        batch_op.create_index("ix_funding_question_join_programme", ["programme_id"], unique=False)
        batch_op.create_index("ix_funding_question_join_submission", ["submission_id"], unique=False)

    with op.batch_alter_table("outcome_data", schema=None) as batch_op:
        batch_op.create_index("ix_outcome_join_outcome_dim", ["outcome_id"], unique=False)
        batch_op.create_index("ix_outcome_join_programme", ["programme_id"], unique=False)
        batch_op.create_index("ix_outcome_join_project", ["project_id"], unique=False)
        batch_op.create_index("ix_outcome_join_submission", ["submission_id"], unique=False)

    with op.batch_alter_table("outcome_dim", schema=None) as batch_op:
        batch_op.create_index("ix_outcome_dim_filter_outcome", ["outcome_category"], unique=False)

    with op.batch_alter_table("output_data", schema=None) as batch_op:
        batch_op.create_index("ix_output_join_output_dim", ["output_id"], unique=False)
        batch_op.create_index("ix_output_join_project", ["project_id"], unique=False)
        batch_op.create_index("ix_output_join_submission", ["submission_id"], unique=False)

    with op.batch_alter_table("place_detail", schema=None) as batch_op:
        batch_op.create_index("ix_place_detail_join_programme", ["programme_id"], unique=False)
        batch_op.create_index("ix_place_detail_join_submission", ["submission_id"], unique=False)

    with op.batch_alter_table("private_investment", schema=None) as batch_op:
        batch_op.create_index("ix_private_investment_join_project", ["project_id"], unique=False)
        batch_op.create_index("ix_private_investment_join_submission", ["submission_id"], unique=False)

    with op.batch_alter_table("programme_dim", schema=None) as batch_op:
        batch_op.create_index("ix_programme_filter_fund_type", ["fund_type_id"], unique=False)
        batch_op.create_index("ix_programme_join_organisation", ["organisation_id"], unique=False)

    with op.batch_alter_table("programme_progress", schema=None) as batch_op:
        batch_op.create_index("ix_programme_progress_join_programme", ["programme_id"], unique=False)
        batch_op.create_index("ix_programme_progress_join_submission", ["submission_id"], unique=False)

    with op.batch_alter_table("project_dim", schema=None) as batch_op:
        batch_op.create_index("ix_project_join_programme", ["programme_id"], unique=False)
        batch_op.create_index("ix_project_join_submission", ["submission_id"], unique=False)

    with op.batch_alter_table("project_progress", schema=None) as batch_op:
        batch_op.create_index("ix_project_progress_join_project", ["project_id"], unique=False)
        batch_op.create_index("ix_project_progress_join_submission", ["submission_id"], unique=False)

    with op.batch_alter_table("risk_register", schema=None) as batch_op:
        batch_op.create_index("ix_risk_register_join_programme", ["programme_id"], unique=False)
        batch_op.create_index("ix_risk_register_join_project", ["project_id"], unique=False)
        batch_op.create_index("ix_risk_register_join_submission", ["submission_id"], unique=False)

    with op.batch_alter_table("submission_dim", schema=None) as batch_op:
        batch_op.create_index("ix_submission_filter_end_date", ["reporting_period_end"], unique=False)
        batch_op.create_index("ix_submission_filter_start_date", ["reporting_period_start"], unique=False)

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("submission_dim", schema=None) as batch_op:
        batch_op.drop_index("ix_submission_filter_start_date")
        batch_op.drop_index("ix_submission_filter_end_date")

    with op.batch_alter_table("risk_register", schema=None) as batch_op:
        batch_op.drop_index("ix_risk_register_join_submission")
        batch_op.drop_index("ix_risk_register_join_project")
        batch_op.drop_index("ix_risk_register_join_programme")

    with op.batch_alter_table("project_progress", schema=None) as batch_op:
        batch_op.drop_index("ix_project_progress_join_submission")
        batch_op.drop_index("ix_project_progress_join_project")

    with op.batch_alter_table("project_dim", schema=None) as batch_op:
        batch_op.drop_index("ix_project_join_submission")
        batch_op.drop_index("ix_project_join_programme")

    with op.batch_alter_table("programme_progress", schema=None) as batch_op:
        batch_op.drop_index("ix_programme_progress_join_submission")
        batch_op.drop_index("ix_programme_progress_join_programme")

    with op.batch_alter_table("programme_dim", schema=None) as batch_op:
        batch_op.drop_index("ix_programme_join_organisation")
        batch_op.drop_index("ix_programme_filter_fund_type")

    with op.batch_alter_table("private_investment", schema=None) as batch_op:
        batch_op.drop_index("ix_private_investment_join_submission")
        batch_op.drop_index("ix_private_investment_join_project")

    with op.batch_alter_table("place_detail", schema=None) as batch_op:
        batch_op.drop_index("ix_place_detail_join_submission")
        batch_op.drop_index("ix_place_detail_join_programme")

    with op.batch_alter_table("output_data", schema=None) as batch_op:
        batch_op.drop_index("ix_output_join_submission")
        batch_op.drop_index("ix_output_join_project")
        batch_op.drop_index("ix_output_join_output_dim")

    with op.batch_alter_table("outcome_dim", schema=None) as batch_op:
        batch_op.drop_index("ix_outcome_dim_filter_outcome")

    with op.batch_alter_table("outcome_data", schema=None) as batch_op:
        batch_op.drop_index("ix_outcome_join_submission")
        batch_op.drop_index("ix_outcome_join_project")
        batch_op.drop_index("ix_outcome_join_programme")
        batch_op.drop_index("ix_outcome_join_outcome_dim")

    with op.batch_alter_table("funding_question", schema=None) as batch_op:
        batch_op.drop_index("ix_funding_question_join_submission")
        batch_op.drop_index("ix_funding_question_join_programme")

    with op.batch_alter_table("funding_comment", schema=None) as batch_op:
        batch_op.drop_index("ix_funding_comment_join_submission")
        batch_op.drop_index("ix_funding_comment_join_project")

    with op.batch_alter_table("funding", schema=None) as batch_op:
        batch_op.drop_index("ix_funding_join_submission")
        batch_op.drop_index("ix_funding_join_project")

    # ### end Alembic commands ###
