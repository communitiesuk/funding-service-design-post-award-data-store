from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import (
    GovCharacterCount,
    GovRadioInput,
    GovSubmitInput,
    GovTextArea,
    GovTextInput,
)
from wtforms import Field, RadioField, StringField, SubmitField
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


class ProjectOverviewProgressSummary(ReportForm):
    _title = "How is your project progressing?"
    progress_summary = StringField(
        label="",
        widget=GovCharacterCount(),
    )


class UpcomingCommunicationOpportunities(ReportForm):
    _title = "Do you have any upcoming communications opportunities?"
    do_you_have_any = RadioField(
        label="",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class CommunicationOpportunityTitle(ReportForm):
    _title = "Title of the communication opportunity"
    title = StringField(
        label="",
        widget=GovTextInput(),
    )


class CommunicationOpportunityDetails(ReportForm):
    _title = "Tell us in more detail about this communication opportunity"
    details = StringField(
        label="",
        widget=GovCharacterCount(),
    )


class CommunicationOpportunityAddAnother(ReportForm):
    add_another = RadioField(
        "Do you want to add any further communications?",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class RAGRatingOverall(ReportForm):
    overall_rating = RadioField(
        "What is your overall RAG rating?",
        choices=(
            ("red", "Red - no progress"),
            ("amber", "Amber - partial progress"),
            ("green", "Green - good progress"),
        ),
        widget=GovRadioInput(),
    )


class RAGRatingSchedule(ReportForm):
    schedule_rating = RadioField(
        "What is your schedule RAG rating?",
        choices=(
            ("red", "Red - no progress"),
            ("amber", "Amber - partial progress"),
            ("green", "Green - good progress"),
        ),
        widget=GovRadioInput(),
    )


class RAGRatingBudget(ReportForm):
    budget_rating = RadioField(
        "What is your budget RAG rating?",
        choices=(
            ("red", "Red - no progress"),
            ("amber", "Amber - partial progress"),
            ("green", "Green - good progress"),
        ),
        widget=GovRadioInput(),
    )


class RAGRatingResourcing(ReportForm):
    resourcing_rating = RadioField(
        "What is your resourcing RAG rating?",
        choices=(
            ("red", "Red - no progress"),
            ("amber", "Amber - partial progress"),
            ("green", "Green - good progress"),
        ),
        widget=GovRadioInput(),
    )


class RAGRatingInformation(ReportForm):
    anything_to_tell = RadioField(
        "Is there anything you need to tell us about your ratings?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=GovRadioInput(),
    )
    additional_information = StringField("Provide more detail", widget=GovCharacterCount())


class ProjectChallengesDoYouHaveAnyForm(ReportForm):
    do_you_have_any = RadioField(
        "Do you need to add any project challenges?",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class ProjectChallengesTitle(ReportForm):
    title = StringField(
        "Title of the project challenge",
        widget=GovTextInput(),
    )


class ProjectChallengesDetails(ReportForm):
    details = StringField(
        "Tell us more about this project challenge",
        widget=GovCharacterCount(),
    )


class ProjectChallengesAddAnother(ReportForm):
    add_another = RadioField(
        "Do you want to add any more project challenges?",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class RibaReportingSelectAnOption(ReportForm):
    select_an_option = RadioField(
        "Select an option to update your RIBA reporting stage",
        choices=[
            ("stage-1", "Stage 1 - Preparation and Brief"),
            ("stage-2", "Stage 2 - Concept Design"),
            ("stage-3", "Stage 3 - Spatial Coordination"),
            ("stage-4", "Stage 4 - Technical Design"),
            ("stage-5", "Stage 5 - Manufacturing and Construction"),
        ],
        widget=GovRadioInput(),
    )


class ProjectIssuesDoYouHaveAnyForm(ReportForm):
    do_you_have_any = RadioField(
        "Do you need to add any project issues?",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class ProjectIssuesTitle(ReportForm):
    title = StringField(
        "Title of issue",
        widget=GovTextInput(),
    )


class ProjectIssuesImpactRating(ReportForm):
    impact_rating = RadioField(
        "Rate the impact of the issue",
        choices=[
            ("insignificant", "Insignificant"),
            ("minor", "Minor"),
            ("significant", "Significant"),
            ("major", "Major"),
            ("severe", "Severe"),
        ],
        widget=GovRadioInput(),
    )


class ProjectIssuesDetails(ReportForm):
    details = StringField(
        "Tell us in more detail about the issue",
        widget=GovTextArea(),
    )


class ProjectIssuesAddAnother(ReportForm):
    add_another = RadioField(
        "Do you want to add any more project challenges?",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )
