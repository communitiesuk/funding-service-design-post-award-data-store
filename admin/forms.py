from flask_admin.form import SecureForm
from wtforms import StringField


class ReingestAdminForm(SecureForm):
    submission_id = StringField("The submission ID to re-ingest")
