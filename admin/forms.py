from flask_wtf import FlaskForm
from flask_wtf.file import FileAllowed, FileField
from govuk_frontend_wtf.wtforms_widgets import GovFileInput, GovTextInput
from wtforms import StringField
from wtforms.validators import DataRequired, InputRequired


class ReingestFromS3AdminForm(FlaskForm):
    submission_id = StringField("The submission ID to re-ingest", widget=GovTextInput(), validators=[DataRequired()])


class ReingestFromFileAdminForm(FlaskForm):
    submission_id = StringField("The submission ID to retrieve", widget=GovTextInput(), validators=[DataRequired()])
    excel_file = FileField(
        "Excel spreadsheet to reingest",
        widget=GovFileInput(),
        validators=[InputRequired(), FileAllowed(["xlsx"])],
    )


class RetrieveSubmissionAdminForm(FlaskForm):
    submission_id = StringField("The submission ID to retrieve", widget=GovTextInput(), validators=[DataRequired()])


class RetrieveFailedSubmissionAdminForm(FlaskForm):
    failure_uuid = StringField(
        "The failure id corresponding to the failed submission to retrieve",
        widget=GovTextInput(),
        validators=[DataRequired()],
    )
