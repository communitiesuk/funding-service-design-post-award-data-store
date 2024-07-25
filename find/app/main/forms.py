from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovRadioInput, GovSubmitInput
from wtforms.fields import RadioField, SelectField, SubmitField
from wtforms.validators import InputRequired


class CookiesForm(FlaskForm):
    functional = RadioField(
        "Do you want to accept functional cookies?",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Select yes if you want to accept functional cookies")],
        choices=[("no", "No"), ("yes", "Yes")],
        default="no",
    )
    analytics = RadioField(
        "Do you want to accept analytics cookies?",
        widget=GovRadioInput(),
        validators=[InputRequired(message="Select yes if you want to accept analytics cookies")],
        choices=[("no", "No"), ("yes", "Yes")],
        default="no",
    )
    save = SubmitField("Save cookie settings", widget=GovSubmitInput())


class DownloadForm(FlaskForm):
    file_format = SelectField(
        "Which format do you need?",
        widget=GovRadioInput(),
        choices=[
            ("xlsx", "XLSX (Microsoft Excel)"),
            ("json", "JSON"),
        ],
        default=None,
    )
    download = SubmitField("Confirm and request data", widget=GovSubmitInput())


class RetrieveForm(FlaskForm):
    download = SubmitField("Download your data", widget=GovSubmitInput())
