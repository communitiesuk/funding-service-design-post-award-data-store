from flask_wtf import FlaskForm
from govuk_frontend_wtf.wtforms_widgets import GovCharacterCount, GovSubmitInput
from wtforms import Field, StringField, SubmitField

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
