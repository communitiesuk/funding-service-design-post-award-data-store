from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovTextInput
from wtforms import StringField
from wtforms.validators import DataRequired


class ReingestAdminForm(FlaskForm):
    submission_id = StringField("The submission ID to re-ingest", widget=GovTextInput(), validators=[DataRequired()])


class RetrieveSubmissionAdminForm(FlaskForm):
    submission_id = StringField("The submission ID to retrieve", widget=GovTextInput(), validators=[DataRequired()])


class RetrieveFailedSubmissionAdminForm(FlaskForm):
    failure_uuid = StringField(
        "The failure id corresponding to the failed submission to retrieve",
        widget=GovTextInput(),
        validators=[DataRequired()],
    )
