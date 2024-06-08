import dataclasses
from typing import Callable, Type

from flask import url_for
from flask_wtf import FlaskForm

from report.forms import (
    CommunicationOpportunityAddAnother,
    CommunicationOpportunityDetails,
    CommunicationOpportunityTitle,
    ProjectChallengesAddAnother,
    ProjectChallengesDetails,
    ProjectChallengesDoYouHaveAnyForm,
    ProjectChallengesTitle,
    ProjectOverviewProgressSummary,
    RAGRatingBudget,
    RAGRatingInformation,
    RAGRatingOverall,
    RAGRatingResourcing,
    RAGRatingSchedule,
    UpcomingCommunicationOpportunities,
)


@dataclasses.dataclass
class SubmissionPage:
    path_fragment: str
    form_class: Type[FlaskForm]
    template: str


@dataclasses.dataclass
class SubmissionAddMultiplePages:
    do_you_need_page: SubmissionPage | None
    details_pages: list[SubmissionPage]
    add_another_page: SubmissionPage

    go_to_details_if: Callable
    add_another_if: Callable

    max_repetitions: int = 5


@dataclasses.dataclass
class SubmissionSubsection:
    name: str
    path_fragment: str
    pages: list[SubmissionPage | SubmissionAddMultiplePages]

    def find_page(self, path_fragment, number: int | None) -> SubmissionPage:
        """Find a page by its URL path fragment."""
        try:
            for page in self.pages:
                if isinstance(page, SubmissionPage) and number is None and page.path_fragment == path_fragment:
                    return page

                elif isinstance(page, SubmissionAddMultiplePages):
                    if page.do_you_need_page and page.do_you_need_page.path_fragment == path_fragment:
                        return page.do_you_need_page

                    if number is None:
                        continue

                    if number > page.max_repetitions:
                        raise KeyError(f"Cannot reach repetition {number} on {page=} - {page.max_repetitions=}")

                    if page.add_another_page.path_fragment == path_fragment:
                        return page.add_another_page

                    for subpage in page.details_pages:
                        if subpage.path_fragment == path_fragment:
                            return subpage

            raise RuntimeError(f"unknown {type(page)=} and {number=} combination")

        except StopIteration as e:
            raise KeyError(f"no page found with {path_fragment=}") from e

    def get_first_page(self) -> SubmissionPage:
        if len(self.pages) < 1:
            raise ValueError(f"no pages added to {self=}")

        if isinstance(self.pages[0], SubmissionAddMultiplePages):
            if self.pages[0].do_you_need_page:
                return self.pages[0].do_you_need_page

            return self.pages[0].details_pages[0]

        if isinstance(self.pages[0], SubmissionPage):
            return self.pages[0]

        raise ValueError(f"unknown page type: {type(self.pages[0])=}")

    def get_next_page(self, flask_form, form_number) -> tuple[SubmissionPage, int | None] | tuple[None, None]:  # noqa: C901
        """OK GROSS NEED TO COME UP WITH A CLEANER INTERFACE HERE

        All this does is find the next SubmissionPage instance based on a FlaskForm and a form number (in the case of
        a SubmissionAddMultiplePages"""
        # TODO: fix this whole shit
        return_page_from_next_loop = False

        if flask_form.save_as_draft.data:
            return None, None

        for page in self.pages:
            if return_page_from_next_loop:
                if isinstance(page, SubmissionPage):
                    return page, None
                elif isinstance(page, SubmissionAddMultiplePages):
                    if page.do_you_need_page:
                        return page.do_you_need_page, None

                    return page.details_pages[0], 1

                raise RuntimeError("did not expect to get here")

            if isinstance(page, SubmissionPage) and form_number is None and isinstance(flask_form, page.form_class):
                return_page_from_next_loop = True
                continue

            elif isinstance(page, SubmissionAddMultiplePages):
                if (
                    page.do_you_need_page
                    and isinstance(flask_form, page.do_you_need_page.form_class)
                    and page.go_to_details_if(flask_form)
                ):
                    return page.details_pages[0], 1

                if form_number is None:
                    continue

                if form_number > page.max_repetitions:
                    raise KeyError(f"Cannot reach repetition {form_number} on {page=} - {page.max_repetitions=}")

                if (
                    page.add_another_page
                    and isinstance(flask_form, page.add_another_page.form_class)
                    and page.add_another_if(flask_form)
                ):
                    return page.details_pages[0], form_number + 1

                for i, submission_form in enumerate(page.details_pages):
                    if isinstance(flask_form, submission_form.form_class):
                        if i + 1 < len(page.details_pages):
                            return page.details_pages[i + 1], form_number

                        if form_number + 1 > page.max_repetitions:
                            return_page_from_next_loop = True
                            continue

                        return page.add_another_page, form_number

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
        self, section_path, subsection_path, page_path, form_number
    ) -> tuple[SubmissionSection, SubmissionSubsection, SubmissionPage]:
        section = self.find_section(section_path)
        subsection = section.find_subsection(subsection_path)
        page = subsection.find_page(page_path, form_number)

        return section, subsection, page

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
            page_path=subsection.get_first_page().path_fragment,
            number=1 if isinstance(subsection.get_first_page(), SubmissionAddMultiplePages) else None,
        )

    def get_next_form_url(self, *, programme, project, section_path, subsection_path, page_path, form_number):
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
                    pages=[
                        SubmissionPage(
                            path_fragment="progress-summary",
                            form_class=ProjectOverviewProgressSummary,
                            template="report/project-overview/progress-summary/progress-summary.html",
                        )
                    ],
                ),
                SubmissionSubsection(
                    name="Upcoming communications",
                    path_fragment="upcoming-communications",
                    pages=[
                        SubmissionAddMultiplePages(
                            do_you_need_page=SubmissionPage(
                                path_fragment="do-you-have-any",
                                form_class=UpcomingCommunicationOpportunities,
                                template="report/project-overview/upcoming-communications/do-you-have-any.html",
                            ),
                            go_to_details_if=lambda form: form.do_you_have_any.data == "yes",
                            details_pages=[
                                SubmissionPage(
                                    path_fragment="title",
                                    form_class=CommunicationOpportunityTitle,
                                    template="report/project-overview/upcoming-communications/title.html",
                                ),
                                SubmissionPage(
                                    path_fragment="details",
                                    form_class=CommunicationOpportunityDetails,
                                    template="report/project-overview/upcoming-communications/details.html",
                                ),
                            ],
                            add_another_page=SubmissionPage(
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
                    pages=[
                        SubmissionPage(
                            path_fragment="overall",
                            form_class=RAGRatingOverall,
                            template="report/project-overview/rag-rating/rating.html",
                        ),
                        SubmissionPage(
                            path_fragment="schedule",
                            form_class=RAGRatingSchedule,
                            template="report/project-overview/rag-rating/rating.html",
                        ),
                        SubmissionPage(
                            path_fragment="budget",
                            form_class=RAGRatingBudget,
                            template="report/project-overview/rag-rating/rating.html",
                        ),
                        SubmissionPage(
                            path_fragment="resourcing",
                            form_class=RAGRatingResourcing,
                            template="report/project-overview/rag-rating/rating.html",
                        ),
                        SubmissionPage(
                            path_fragment="information",
                            form_class=RAGRatingInformation,
                            template="report/project-overview/rag-rating/information.html",
                        ),
                    ],
                ),
                SubmissionSubsection(
                    name="Challenges",
                    path_fragment="challenges",
                    pages=[
                        SubmissionAddMultiplePages(
                            do_you_need_page=SubmissionPage(
                                path_fragment="do-you-have-any",
                                form_class=ProjectChallengesDoYouHaveAnyForm,
                                template="report/project-overview/challenges/do-you-have-any.html",
                            ),
                            go_to_details_if=lambda form: form.do_you_have_any.data == "yes",
                            details_pages=[
                                SubmissionPage(
                                    path_fragment="title",
                                    form_class=ProjectChallengesTitle,
                                    template="report/project-overview/challenges/title.html",
                                ),
                                SubmissionPage(
                                    path_fragment="details",
                                    form_class=ProjectChallengesDetails,
                                    template="report/project-overview/challenges/details.html",
                                ),
                            ],
                            add_another_page=SubmissionPage(
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
