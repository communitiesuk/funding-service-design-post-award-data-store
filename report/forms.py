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


class ReportDataForm(FlaskForm):
    save_and_continue = SubmitField("Save and continue", widget=GovSubmitInput())
    save_as_draft = SubmitField("Save as draft", widget=GovSubmitInput())

    def get_data(self):
        return {
            field_name: field.data
            for field_name, field in self.__dict__.items()
            if isinstance(field, (Field, UnboundField))
            and not isinstance(field, SubmitField)
            and field_name != "csrf_token"
        }


class ProjectOverviewProgressSummary(ReportDataForm):
    progress_summary = StringField(
        "How is your project progressing?",
        widget=GovCharacterCount(),
    )


class UpcomingCommunicationOpportunities(ReportDataForm):
    do_you_have_any = RadioField(
        "Do you have any upcoming communications opportunities?",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class CommunicationOpportunityTitle(ReportDataForm):
    title = StringField(
        "Title of the communication opportunity",
        widget=GovTextInput(),
    )


class CommunicationOpportunityDetails(ReportDataForm):
    details = StringField(
        "Tell us in more detail about your upcoming communications",
        widget=GovCharacterCount(),
    )


class CommunicationOpportunityAddAnother(ReportDataForm):
    add_another = RadioField(
        "Do you want to add any further communications?",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class RAGRatingOverall(ReportDataForm):
    overall_rating = RadioField(
        "What is your overall RAG rating?",
        choices=(
            ("red", "Red - no progress"),
            ("amber", "Amber - partial progress"),
            ("green", "Green - good progress"),
        ),
        widget=GovRadioInput(),
    )


class RAGRatingSchedule(ReportDataForm):
    schedule_rating = RadioField(
        "What is your schedule RAG rating?",
        choices=(
            ("red", "Red - no progress"),
            ("amber", "Amber - partial progress"),
            ("green", "Green - good progress"),
        ),
        widget=GovRadioInput(),
    )


class RAGRatingBudget(ReportDataForm):
    budget_rating = RadioField(
        "What is your budget RAG rating?",
        choices=(
            ("red", "Red - no progress"),
            ("amber", "Amber - partial progress"),
            ("green", "Green - good progress"),
        ),
        widget=GovRadioInput(),
    )


class RAGRatingResourcing(ReportDataForm):
    resourcing_rating = RadioField(
        "What is your resourcing RAG rating?",
        choices=(
            ("red", "Red - no progress"),
            ("amber", "Amber - partial progress"),
            ("green", "Green - good progress"),
        ),
        widget=GovRadioInput(),
    )


class RAGRatingInformation(ReportDataForm):
    anything_to_tell = RadioField(
        "Is there anything you need to tell us about your ratings?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=GovRadioInput(),
    )
    additional_information = StringField("Provide more detail", widget=GovCharacterCount())


class ProjectChallengesDoYouHaveAnyForm(ReportDataForm):
    do_you_have_any = RadioField(
        "Do you need to add any project challenges?",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class ProjectChallengesTitle(ReportDataForm):
    title = StringField(
        "Title of the project challenge",
        widget=GovTextInput(),
    )


class ProjectChallengesDetails(ReportDataForm):
    details = StringField(
        "Tell us more about this project challenge",
        widget=GovCharacterCount(),
    )


class ProjectChallengesAddAnother(ReportDataForm):
    add_another = RadioField(
        "Do you want to add any more project challenges?",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class ProjectIssuesDoYouHaveAnyForm(ReportDataForm):
    do_you_have_any = RadioField(
        "Do you need to add any project issues?",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class ProjectIssuesTitle(ReportDataForm):
    title = StringField(
        "Title of issue",
        widget=GovTextInput(),
    )


class ProjectIssuesImpactRating(ReportDataForm):
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


class ProjectIssuesDetails(ReportDataForm):
    details = StringField(
        "Tell us in more detail about the issue",
        widget=GovTextArea(),
    )


class ProjectIssuesAddAnother(ReportDataForm):
    add_another = RadioField(
        "Do you want to add any more project challenges?",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )
