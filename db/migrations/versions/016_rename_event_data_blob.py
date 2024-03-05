"""Empty message

Revision ID: 016_rename_event_data_blob
Revises: 015_add_jsonb_to_submission
Create Date: 2024-03-05 14:35:05.518333

"""

from alembic import op

# Revision identifiers, used by Alembic.
revision = "016_rename_event_data_blob"
down_revision = "015_add_jsonb_to_submission"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("funding", schema=None) as batch_op_funding:
        batch_op_funding.alter_column("event_data_blob", new_column_name="data_blob")

    with op.batch_alter_table("funding_comment", schema=None) as batch_op_comment:
        batch_op_comment.alter_column("event_data_blob", new_column_name="data_blob")

    with op.batch_alter_table("funding_question", schema=None) as batch_op_question:
        batch_op_question.alter_column("event_data_blob", new_column_name="data_blob")

    with op.batch_alter_table("place_detail", schema=None) as batch_op_question:
        batch_op_question.alter_column("event_data_blob", new_column_name="data_blob")

    with op.batch_alter_table("private_investment", schema=None) as batch_op_question:
        batch_op_question.alter_column("event_data_blob", new_column_name="data_blob")

    with op.batch_alter_table("programme_progress", schema=None) as batch_op_question:
        batch_op_question.alter_column("event_data_blob", new_column_name="data_blob")

    with op.batch_alter_table("project_dim", schema=None) as batch_op_question:
        batch_op_question.alter_column("event_data_blob", new_column_name="data_blob")

    with op.batch_alter_table("project_progress", schema=None) as batch_op_question:
        batch_op_question.alter_column("event_data_blob", new_column_name="data_blob")

    with op.batch_alter_table("risk_register", schema=None) as batch_op_question:
        batch_op_question.alter_column("event_data_blob", new_column_name="data_blob")

    # End of the upgrade process


def downgrade():
    with op.batch_alter_table("funding", schema=None) as batch_op_funding_downgrade:
        batch_op_funding_downgrade.alter_column("data_blob", new_column_name="event_data_blob")

    with op.batch_alter_table("funding_comment", schema=None) as batch_op_comment_downgrade:
        batch_op_comment_downgrade.alter_column("data_blob", new_column_name="event_data_blob")

    with op.batch_alter_table("funding_question", schema=None) as batch_op_question_downgrade:
        batch_op_question_downgrade.alter_column("data_blob", new_column_name="event_data_blob")

    with op.batch_alter_table("place_detail", schema=None) as batch_op_question_downgrade:
        batch_op_question_downgrade.alter_column("data_blob", new_column_name="event_data_blob")

    with op.batch_alter_table("private_investment", schema=None) as batch_op_question_downgrade:
        batch_op_question_downgrade.alter_column("data_blob", new_column_name="event_data_blob")

    with op.batch_alter_table("programme_progress", schema=None) as batch_op_question_downgrade:
        batch_op_question_downgrade.alter_column("data_blob", new_column_name="event_data_blob")

    with op.batch_alter_table("project_dim", schema=None) as batch_op_question_downgrade:
        batch_op_question_downgrade.alter_column("data_blob", new_column_name="event_data_blob")

    with op.batch_alter_table("project_progress", schema=None) as batch_op_question_downgrade:
        batch_op_question_downgrade.alter_column("data_blob", new_column_name="event_data_blob")

    with op.batch_alter_table("risk_register", schema=None) as batch_op_question_downgrade:
        batch_op_question_downgrade.alter_column("data_blob", new_column_name="event_data_blob")

    # End of the downgrade process
