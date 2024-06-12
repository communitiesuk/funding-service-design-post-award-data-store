from flask_admin.form import SecureForm
from govuk_frontend_wtf.wtforms_widgets import GovTextInput
from wtforms import StringField


class ReingestAdminForm(SecureForm):
    submission_id = StringField("The submission ID to re-ingest", widget=GovTextInput())


class RetrieveSubmissionAdminForm(SecureForm):
    submission_id = StringField("The submission ID to retrieve", widget=GovTextInput())


class RetrieveFailedSubmissionAdminForm(SecureForm):
    failure_uuid = StringField(
        "The failure id corresponding to the failed submission to retrieve", widget=GovTextInput()
    )
