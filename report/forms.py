from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovCharacterCount, GovRadioInput, GovSubmitInput, GovTextInput
from wtforms import Field, RadioField, StringField, SubmitField

from core.controllers.partial_submissions import (
    get_programme_question_data,
    get_project_question_data,
    set_project_question_data,
)
from core.db.entities import Programme, Project


class SubmissionDataForm(FlaskForm):
    save_and_continue = SubmitField("Save and continue", widget=GovSubmitInput())
    save_as_draft = SubmitField("Save as draft", widget=GovSubmitInput())

    @classmethod
    def create_and_populate(cls, programme: Programme, project: Project | None = None, **kwargs):
        if project:
            existing_data = get_project_question_data(programme, project, cls.__name__)
        else:
            existing_data = get_programme_question_data(programme, cls.__name__)

        return cls(data=existing_data, **kwargs)

    @property
    def submission_data(self):
        return {
            k: v.data
            for k, v in self.__dict__.items()
            if isinstance(v, Field) and not isinstance(v, SubmitField) and k != "csrf_token"
        }

    def save_submission_data(self, programme: Programme, project: Project):
        set_project_question_data(programme, project, self.__class__.__name__, self.submission_data)


class ProjectOverviewProgressSummary(SubmissionDataForm):
    progress_summary = StringField(
        "How is your project progressing?",
        widget=GovCharacterCount(),
    )


class UpcomingCommunicationOpportunities(SubmissionDataForm):
    do_you_have_any = RadioField(
        "Do you have any upcoming communications opportunities?",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class CommunicationOpportunityTitle(SubmissionDataForm):
    title = StringField(
        "Title of the communication opportunity",
        widget=GovTextInput(),
    )


class CommunicationOpportunityDetails(SubmissionDataForm):
    details = StringField(
        "Tell us in more detail about your upcoming communications",
        widget=GovCharacterCount(),
    )


class CommunicationOpportunityAddAnother(SubmissionDataForm):
    add_another = RadioField(
        "Do you want to add any further communications?",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class RAGRatingOverall(SubmissionDataForm):
    rating = RadioField(
        "What is your overall RAG rating?",
        choices=(
            ("red", "Red - no progress"),
            ("amber", "Amber - partial progress"),
            ("green", "Green - good progress"),
        ),
        widget=GovRadioInput(),
    )


class RAGRatingSchedule(SubmissionDataForm):
    rating = RadioField(
        "What is your schedule RAG rating?",
        choices=(
            ("red", "Red - no progress"),
            ("amber", "Amber - partial progress"),
            ("green", "Green - good progress"),
        ),
        widget=GovRadioInput(),
    )


class RAGRatingBudget(SubmissionDataForm):
    rating = RadioField(
        "What is your budget RAG rating?",
        choices=(
            ("red", "Red - no progress"),
            ("amber", "Amber - partial progress"),
            ("green", "Green - good progress"),
        ),
        widget=GovRadioInput(),
    )


class RAGRatingResourcing(SubmissionDataForm):
    rating = RadioField(
        "What is your resourcing RAG rating?",
        choices=(
            ("red", "Red - no progress"),
            ("amber", "Amber - partial progress"),
            ("green", "Green - good progress"),
        ),
        widget=GovRadioInput(),
    )


class RAGRatingInformation(SubmissionDataForm):
    anything_to_tell = RadioField(
        "Is there anything you need to tell us about your ratings?",
        choices=[("yes", "Yes"), ("no", "No")],
        widget=GovRadioInput(),
    )
    additional_information = StringField("Provide more detail", widget=GovCharacterCount())


class ProjectChallengesDoYouHaveAnyForm(SubmissionDataForm):
    do_you_have_any = RadioField(
        "Do you need to add any project challenges?",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )


class ProjectChallengesTitle(SubmissionDataForm):
    title = StringField(
        "Title of the project challenge",
        widget=GovTextInput(),
    )


class ProjectChallengesDetails(SubmissionDataForm):
    details = StringField(
        "Tell us more about this project challenge",
        widget=GovCharacterCount(),
    )


class ProjectChallengesAddAnother(SubmissionDataForm):
    add_another = RadioField(
        "Do you want to add any more project challenges?",
        choices=(("yes", "Yes"), ("no", "No")),
        widget=GovRadioInput(),
    )
