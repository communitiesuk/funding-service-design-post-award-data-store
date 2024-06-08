from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovCharacterCount, GovRadioInput, GovSubmitInput, GovTextInput
from wtforms import Field, RadioField, StringField, SubmitField
from wtforms.fields.core import UnboundField


class SubmissionDataForm(FlaskForm):
    save_and_continue = SubmitField("Save and continue", widget=GovSubmitInput())
    save_as_draft = SubmitField("Save as draft", widget=GovSubmitInput())

    @property
    def submission_data(self):
        return {
            field_name: field.data
            for field_name, field in self.__dict__.items()
            if isinstance(field, (Field, UnboundField))
            and not isinstance(field, SubmitField)
            and field_name != "csrf_token"
        }

    @classmethod
    def get_submission_data(cls):
        return {
            field_name: None
            for field_name, field in cls.__dict__.items()
            if isinstance(field, (Field, UnboundField))
            and not isinstance(field, SubmitField)
            and field_name != "csrf_token"
        }


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
