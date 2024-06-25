from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import (
    GovCharacterCount,
    GovFileInput,
    GovRadioInput,
    GovSubmitInput,
    GovTextArea,
    GovTextInput,
)
from wtforms import Field, FileField, RadioField, StringField, SubmitField
from wtforms.fields.core import UnboundField


class ReportForm(FlaskForm):
    save_and_continue = SubmitField("Save and continue", widget=GovSubmitInput())
    save_as_draft = SubmitField("Save as draft", widget=GovSubmitInput())

    def get_input_data(self):
        return {
            field_name: field.data
            for field_name, field in self.__dict__.items()
            if isinstance(field, (Field, UnboundField))
            and not isinstance(field, SubmitField)
            and field_name != "csrf_token"
        }


class ProgressSummary(ReportForm):
    _title = "How is your project progressing?"
    progress_summary = StringField(
        label="",
        widget=GovCharacterCount(),
    )


class UpcomingCommunicationsInitiate(ReportForm):
    _title = "Do you have any upcoming communications opportunities?"
    do_you_have_any = RadioField(
        label="",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class UpcomingCommunicationTitle(ReportForm):
    _title = "Title of the communication opportunity"
    title = StringField(
        label="",
        widget=GovTextInput(),
    )


class UpcomingCommunicationDetails(ReportForm):
    _title = "Tell us in more detail about this communication opportunity"
    details = StringField(
        label="",
        widget=GovCharacterCount(),
    )


class RAGRatingOverall(ReportForm):
    _title = "What is your overall RAG rating?"
    rating = RadioField(
        label="",
        choices=(
            ("red", "Red - no progress"),
            ("amber", "Amber - partial progress"),
            ("green", "Green - good progress"),
        ),
        widget=GovRadioInput(),
    )


class RAGRatingSchedule(ReportForm):
    _title = "What is your schedule RAG rating?"
    rating = RadioField(
        label="",
        choices=(
            ("red", "Red - no progress"),
            ("amber", "Amber - partial progress"),
            ("green", "Green - good progress"),
        ),
        widget=GovRadioInput(),
    )


class RAGRatingBudget(ReportForm):
    _title = "What is your budget RAG rating?"
    rating = RadioField(
        label="",
        choices=(
            ("red", "Red - no progress"),
            ("amber", "Amber - partial progress"),
            ("green", "Green - good progress"),
        ),
        widget=GovRadioInput(),
    )


class RAGRatingResourcing(ReportForm):
    _title = "What is your resourcing RAG rating?"
    rating = RadioField(
        label="",
        choices=(
            ("red", "Red - no progress"),
            ("amber", "Amber - partial progress"),
            ("green", "Green - good progress"),
        ),
        widget=GovRadioInput(),
    )


class RAGRatingInformation(ReportForm):
    _title = "Is there anything you need to tell us about your ratings?"
    anything_to_tell = RadioField(
        label="",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=GovRadioInput(),
    )
    additional_information = StringField(label="", widget=GovTextArea())


class ChallengesInitiate(ReportForm):
    _title = "Do you need to add any project challenges?"
    do_you_have_any = RadioField(
        label="",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class ChallengeTitle(ReportForm):
    _title = "Title of the project challenge"
    title = StringField(
        label="",
        widget=GovTextInput(),
    )


class ChallengeDetails(ReportForm):
    _title = "Tell us in more detail about the project challenge"
    details = StringField(
        label="",
        widget=GovCharacterCount(),
    )


class RIBAReportingStage(ReportForm):
    _title = "Select an option to update your RIBA reporting stage"
    stage = RadioField(
        label="",
        choices=[
            ("stage-1", "Stage 1 - Preparation and Brief"),
            ("stage-2", "Stage 2 - Concept Design"),
            ("stage-3", "Stage 3 - Spatial Coordination"),
            ("stage-4", "Stage 4 - Technical Design"),
            ("stage-5", "Stage 5 - Manufacturing and Construction"),
        ],
        widget=GovRadioInput(),
    )


class IssuesInitiate(ReportForm):
    _title = "Do you need to add any project issues?"
    do_you_have_any = RadioField(
        label="",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class IssueTitle(ReportForm):
    _title = "Title of issue"
    title = StringField(
        label="",
        widget=GovTextInput(),
    )


class IssueImpactRating(ReportForm):
    _title = "Rate the impact of the issue"
    impact_rating = RadioField(
        label="",
        choices=[
            ("insignificant", "Insignificant"),
            ("minor", "Minor"),
            ("significant", "Significant"),
            ("major", "Major"),
            ("severe", "Severe"),
        ],
        widget=GovRadioInput(),
    )


class IssueDetails(ReportForm):
    _title = "Tell us in more detail about the issue"
    details = StringField(
        label="",
        widget=GovTextArea(),
    )


class Expenditure(ReportForm):
    _title = "Project expenditure"
    expenditure = FileField(
        label="",
        widget=GovFileInput(),
    )
