from flask_admin.form import SecureForm
from govuk_frontend_wtf.wtforms_widgets import GovTextInput
from wtforms import StringField


class ReingestAdminForm(SecureForm):
    submission_id = StringField("The submission ID to re-ingest", widget=GovTextInput())
