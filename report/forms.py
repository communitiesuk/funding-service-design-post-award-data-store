from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovCharacterCount, GovSubmitInput
from wtforms import StringField, SubmitField


class ProjectOverviewProgressSummary(FlaskForm):
    progress_summary = StringField(
        "How is your project progressing?",
        widget=GovCharacterCount(),
    )

    save_and_continue = SubmitField("Save and continue", widget=GovSubmitInput())
    save_as_draft = SubmitField("Save as draft", widget=GovSubmitInput())
