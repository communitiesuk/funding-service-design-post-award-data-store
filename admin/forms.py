from flask_wtf import FlaskForm
from wtforms import StringField
from wtforms.validators import DataRequired


class ReingestAdminForm(FlaskForm):
    submission_id = StringField("The submission ID to re-ingest", validators=[DataRequired()])


class RetrieveSubmissionAdminForm(FlaskForm):
    submission_id = StringField("The submission ID to retrieve", validators=[DataRequired()])


class RetrieveFailedSubmissionAdminForm(FlaskForm):
    failure_uuid = StringField(
        "The failure id corresponding to the failed submission to retrieve", validators=[DataRequired()]
    )
