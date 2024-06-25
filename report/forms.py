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
    progress_summary = StringField(
        label="",
        widget=GovCharacterCount(),
    )


class UpcomingCommunicationsInitiate(ReportForm):
    do_you_have_any = RadioField(
        label="",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class UpcomingCommunicationTitle(ReportForm):
    title = StringField(
        label="",
        widget=GovTextInput(),
    )


class UpcomingCommunicationDetails(ReportForm):
    details = StringField(
        label="",
        widget=GovCharacterCount(),
    )


class RAGRatingOverall(ReportForm):
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
    anything_to_tell = RadioField(
        label="",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=GovRadioInput(),
    )
    additional_information = StringField(label="", widget=GovTextArea())


class ChallengesInitiate(ReportForm):
    do_you_have_any = RadioField(
        label="",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class ChallengeTitle(ReportForm):
    title = StringField(
        label="",
        widget=GovTextInput(),
    )


class ChallengeDetails(ReportForm):
    details = StringField(
        label="",
        widget=GovCharacterCount(),
    )


class RIBAReportingStage(ReportForm):
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
    do_you_have_any = RadioField(
        label="",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class IssueTitle(ReportForm):
    title = StringField(
        label="",
        widget=GovTextInput(),
    )


class IssueImpactRating(ReportForm):
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
    details = StringField(
        label="",
        widget=GovTextArea(),
    )


class Expenditure(ReportForm):
    expenditure = FileField(
        label="",
        widget=GovFileInput(),
    )


class RisksInitiate(ReportForm):
    do_you_have_any = RadioField(
        label="",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class RiskTitle(ReportForm):
    title = StringField(
        label="",
        widget=GovTextInput(),
    )


class RiskCategory(ReportForm):
    category = RadioField(
        label="",
        choices=[
            ("1", "Category 1 - Very high"),
            ("2", "Category 2 - High"),
            ("3", "Category 3 - Medium"),
            ("4", "Category 4 - Low"),
            ("5", "Category 5 - Very low"),
        ],
        widget=GovRadioInput(),
    )


class RiskMitigation(ReportForm):
    mitigation = StringField(
        label="",
        widget=GovCharacterCount(),
    )


class RiskIssueLikelihood(ReportForm):
    issue_likelihood = RadioField(
        label="",
        choices=[
            ("extremely-likely", "Extremely likely"),
            ("likely", "Likely"),
            ("possible", "Possible"),
            ("unlikely", "Unlikely"),
            ("extremely-unlikely", "Extremely unlikely"),
        ],
        widget=GovRadioInput(),
    )
