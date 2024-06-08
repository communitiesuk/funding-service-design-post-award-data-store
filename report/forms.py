import dataclasses
from typing import Callable, Type

from flask import url_for
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


@dataclasses.dataclass
class SubmissionForm:
    path_fragment: str
    form_class: Type[FlaskForm]
    template: str


@dataclasses.dataclass
class RepeatableSubmissionForm:
    do_you_need_form: SubmissionForm | None
    details_forms: list[SubmissionForm]
    add_another_form: SubmissionForm

    go_to_details_if: Callable
    add_another_if: Callable

    max_repetitions: int = 5

    def get_redirect_url_on_submit(self, form):
        pass


@dataclasses.dataclass
class SubmissionSubsection:
    name: str
    path_fragment: str
    forms: list[SubmissionForm | RepeatableSubmissionForm]

    def find_form(self, path_fragment, number: int | None) -> SubmissionForm:
        """Find a form by its URL path fragment."""
        try:
            for form in self.forms:
                if isinstance(form, SubmissionForm) and number is None and form.path_fragment == path_fragment:
                    return form

                elif isinstance(form, RepeatableSubmissionForm):
                    if form.do_you_need_form and form.do_you_need_form.path_fragment == path_fragment:
                        return form.do_you_need_form

                    if number is None:
                        continue

                    if number > form.max_repetitions:
                        raise KeyError(f"Cannot reach repetition {number} on {form=} - {form.max_repetitions=}")

                    if form.add_another_form.path_fragment == path_fragment:
                        return form.add_another_form

                    for submission_form in form.details_forms:
                        if submission_form.path_fragment == path_fragment:
                            return submission_form

            raise RuntimeError(f"unknown {type(form)=} and {number=} combination")

        except StopIteration as e:
            raise KeyError(f"no form found with {path_fragment=}") from e

    def get_first_submission_form(self) -> SubmissionForm:
        if len(self.forms) < 1:
            raise ValueError(f"no forms added to {self=}")

        if isinstance(self.forms[0], RepeatableSubmissionForm):
            if self.forms[0].do_you_need_form:
                return self.forms[0].do_you_need_form

            return self.forms[0].details_forms[0]

        if isinstance(self.forms[0], SubmissionForm):
            return self.forms[0]

        raise ValueError(f"unknown form type: {type(self.forms[0])=}")

    def get_next_form(self, flask_form, form_number) -> tuple[SubmissionForm, int | None] | tuple[None, None]:  # noqa: C901
        """OK GROSS NEED TO COME UP WITH A CLEANER INTERFACE HERE

        All this does is find the next SubmissionForm instance based on a FlaskForm and a form number (in the case of
        a RepeatableSubmissionForm"""
        # TODO: fix this whole shit
        return_form_from_next_loop = False

        if flask_form.save_as_draft.data:
            return None, None

        for form in self.forms:
            if return_form_from_next_loop:
                if isinstance(form, SubmissionForm):
                    return form, None
                elif isinstance(form, RepeatableSubmissionForm):
                    if form.do_you_need_form:
                        return form.do_you_need_form, None

                    return form.details_forms[0], 1

                raise RuntimeError("did not expect to get here")

            if isinstance(form, SubmissionForm) and form_number is None and isinstance(flask_form, form.form_class):
                return_form_from_next_loop = True
                continue

            elif isinstance(form, RepeatableSubmissionForm):
                if (
                    form.do_you_need_form
                    and isinstance(flask_form, form.do_you_need_form.form_class)
                    and form.go_to_details_if(flask_form)
                ):
                    return form.details_forms[0], 1

                if form_number is None:
                    continue

                if form_number > form.max_repetitions:
                    raise KeyError(f"Cannot reach repetition {form_number} on {form=} - {form.max_repetitions=}")

                if (
                    form.add_another_form
                    and isinstance(flask_form, form.add_another_form.form_class)
                    and form.add_another_if(flask_form)
                ):
                    return form.details_forms[0], form_number + 1

                for i, submission_form in enumerate(form.details_forms):
                    if isinstance(flask_form, submission_form.form_class):
                        if i + 1 < len(form.details_forms):
                            return form.details_forms[i + 1], form_number

                        if form_number + 1 > form.max_repetitions:
                            return_form_from_next_loop = True
                            continue

                        return form.add_another_form, form_number

        return None, None


@dataclasses.dataclass
class SubmissionSection:
    name: str
    path_fragment: str
    subsections: list[SubmissionSubsection]

    def find_subsection(self, path_fragment) -> SubmissionSubsection:
        try:
            return next(subsection for subsection in self.subsections if subsection.path_fragment == path_fragment)
        except StopIteration as e:
            raise KeyError(f"so subsection found with {path_fragment=}") from e


@dataclasses.dataclass
class FundSubmissionStructure:
    sections: list[SubmissionSection]

    def find_section(self, path_fragment) -> SubmissionSection:
        try:
            return next(section for section in self.sections if section.path_fragment == path_fragment)
        except StopIteration as e:
            raise KeyError(f"no section found with {path_fragment=}") from e

    def resolve(
        self, section_path, subsection_path, form_path, form_number
    ) -> tuple[SubmissionSection, SubmissionSubsection, SubmissionForm]:
        section = self.find_section(section_path)
        subsection = section.find_subsection(subsection_path)
        form = subsection.find_form(form_path, form_number)

        return section, subsection, form

    @staticmethod
    def get_first_url_for_section(
        programme_id, project_id, section: SubmissionSection, subsection: SubmissionSubsection
    ):
        return url_for(
            "report.do_submission_form",
            programme_id=programme_id,
            project_id=project_id,
            section_path=section.path_fragment,
            subsection_path=subsection.path_fragment,
            form_path=subsection.get_first_submission_form().path_fragment,
            number=1 if isinstance(subsection.get_first_submission_form(), RepeatableSubmissionForm) else None,
        )

    def get_next_form_url(self, *, programme, project, section_path, subsection_path, form_path, form_number):
        pass


submission_structure = FundSubmissionStructure(
    sections=[
        SubmissionSection(
            name="Project overview",
            path_fragment="project-overview",
            subsections=[
                SubmissionSubsection(
                    name="Progress summary",
                    path_fragment="progress-summary",  # meh this is a bit duplicative for single-form subsections
                    forms=[
                        SubmissionForm(
                            path_fragment="progress-summary",
                            form_class=ProjectOverviewProgressSummary,
                            template="report/project-overview/progress-summary/progress-summary.html",
                        )
                    ],
                ),
                SubmissionSubsection(
                    name="Upcoming communications",
                    path_fragment="upcoming-communications",
                    forms=[
                        RepeatableSubmissionForm(
                            do_you_need_form=SubmissionForm(
                                path_fragment="do-you-have-any",
                                form_class=UpcomingCommunicationOpportunities,
                                template="report/project-overview/upcoming-communications/do-you-have-any.html",
                            ),
                            go_to_details_if=lambda form: form.do_you_have_any.data == "yes",
                            details_forms=[
                                SubmissionForm(
                                    path_fragment="title",
                                    form_class=CommunicationOpportunityTitle,
                                    template="report/project-overview/upcoming-communications/title.html",
                                ),
                                SubmissionForm(
                                    path_fragment="details",
                                    form_class=CommunicationOpportunityDetails,
                                    template="report/project-overview/upcoming-communications/details.html",
                                ),
                            ],
                            add_another_form=SubmissionForm(
                                path_fragment="add-another",
                                form_class=CommunicationOpportunityAddAnother,
                                template="report/project-overview/upcoming-communications/add-another.html",
                            ),
                            add_another_if=lambda form: form.add_another.data == "yes",
                            max_repetitions=5,
                        ),
                    ],
                ),
                SubmissionSubsection(
                    name="Red-Amber-Green (RAG) Rating",
                    path_fragment="rag-rating",
                    forms=[
                        SubmissionForm(
                            path_fragment="overall",
                            form_class=RAGRatingOverall,
                            template="report/project-overview/rag-rating/rating.html",
                        ),
                        SubmissionForm(
                            path_fragment="schedule",
                            form_class=RAGRatingSchedule,
                            template="report/project-overview/rag-rating/rating.html",
                        ),
                        SubmissionForm(
                            path_fragment="budget",
                            form_class=RAGRatingBudget,
                            template="report/project-overview/rag-rating/rating.html",
                        ),
                        SubmissionForm(
                            path_fragment="resourcing",
                            form_class=RAGRatingResourcing,
                            template="report/project-overview/rag-rating/rating.html",
                        ),
                        SubmissionForm(
                            path_fragment="information",
                            form_class=RAGRatingInformation,
                            template="report/project-overview/rag-rating/information.html",
                        ),
                    ],
                ),
                SubmissionSubsection(
                    name="Challenges",
                    path_fragment="challenges",
                    forms=[
                        RepeatableSubmissionForm(
                            do_you_need_form=SubmissionForm(
                                path_fragment="do-you-have-any",
                                form_class=ProjectChallengesDoYouHaveAnyForm,
                                template="report/project-overview/challenges/do-you-have-any.html",
                            ),
                            go_to_details_if=lambda form: form.do_you_have_any.data == "yes",
                            details_forms=[
                                SubmissionForm(
                                    path_fragment="title",
                                    form_class=ProjectChallengesTitle,
                                    template="report/project-overview/challenges/title.html",
                                ),
                                SubmissionForm(
                                    path_fragment="details",
                                    form_class=ProjectChallengesDetails,
                                    template="report/project-overview/challenges/details.html",
                                ),
                            ],
                            add_another_form=SubmissionForm(
                                path_fragment="add-another",
                                form_class=ProjectChallengesAddAnother,
                                template="report/project-overview/challenges/add-another.html",
                            ),
                            add_another_if=lambda form: form.add_another.data == "yes",
                            max_repetitions=5,
                        ),
                    ],
                ),
            ],
        ),
    ]
)
