import dataclasses
import enum

from core.db import db
from core.db.entities import PendingSubmission, Programme
from report.report_form_components.report_form_page import ReportFormPage
from report.report_form_components.report_form_section import ReportFormSection
from report.report_form_components.report_form_subsection import ReportFormSubsection


class ReportSubsectionStatus(enum.Enum):
    NOT_STARTED = "Not started"
    IN_PROGRESS = "In progress"
    COMPLETE = "Complete"


@dataclasses.dataclass
class ReportPageInstance:
    form_data: dict


@dataclasses.dataclass
class ReportPage:
    name: str
    form_data: dict

    @classmethod
    def load_from_json(cls, json_data: dict) -> "ReportPage":
        name = json_data["name"]
        form_data = json_data["form_data"]
        return cls(name=name, form_data=form_data)

    def serialize(self) -> dict:
        return {"name": self.name, "form_data": self.form_data}


@dataclasses.dataclass
class ReportSubsection:
    name: str
    pages: list[ReportPage]
    complete: bool

    @classmethod
    def load_from_json(cls, json_data: dict) -> "ReportSubsection":
        name = json_data["name"]
        pages = [ReportPage.load_from_json(page_data) for page_data in json_data["pages"]]
        complete = json_data["complete"]
        return cls(name=name, pages=pages, complete=complete)

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "pages": [page.serialize() for page in self.pages],
            "complete": self.complete,
        }

    def num_existing_pages(self, form_page: ReportFormPage) -> int:
        return len([page for page in self.pages if page.name == form_page.name])

    def page(self, form_page: ReportFormPage, instance_number: int) -> ReportPage:
        existing_pages = [page for page in self.pages if page.name == form_page.name]
        if not existing_pages or instance_number >= len(existing_pages):
            new_page = ReportPage(name=form_page.name, form_data={})
            self.pages.append(new_page)
            return new_page
        return existing_pages[instance_number]


@dataclasses.dataclass
class ReportSection:
    name: str
    subsections: list[ReportSubsection]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "ReportSection":
        name = json_data["name"]
        subsections = [ReportSubsection.load_from_json(subsection_data) for subsection_data in json_data["subsections"]]
        return cls(name=name, subsections=subsections)

    def serialize(self) -> dict:
        return {"name": self.name, "subsections": [subsection.serialize() for subsection in self.subsections]}

    def subsection(self, form_subsection: ReportFormSubsection) -> ReportSubsection:
        existing_subsection = next(
            (subsection for subsection in self.subsections if subsection.name == form_subsection.name), None
        )
        if not existing_subsection:
            new_subsection = ReportSubsection(name=form_subsection.name, pages=[], complete=False)
            self.subsections.append(new_subsection)
            return new_subsection
        return existing_subsection


@dataclasses.dataclass
class SubmissionReport:
    name: str
    programme_project: str
    sections: list[ReportSection]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "Submission":
        name = json_data["name"]
        programme_project = json_data["programme_project"]
        sections = [ReportSection.load_from_json(section_data) for section_data in json_data["sections"]]
        return cls(name=name, programme_project=programme_project, sections=sections)

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "programme_project": self.programme_project,
            "sections": [section.serialize() for section in self.sections],
        }

    def section(self, form_section: ReportFormSection) -> ReportSection:
        existing_section = next((section for section in self.sections if section.name == form_section.name), None)
        if not existing_section:
            new_section = ReportSection(name=form_section.name, subsections=[])
            self.sections.append(new_section)
            return new_section
        return existing_section

    def subsection_status(self, section_name: str, subsection_name: str) -> ReportSubsectionStatus:
        section = next(
            (section for section in self.sections if section.name == section_name),
            None,
        )
        if not section:
            return ReportSubsectionStatus.NOT_STARTED
        subsection = next(
            (subsection for subsection in section.subsections if subsection.name == subsection_name),
            None,
        )
        if not subsection:
            return ReportSubsectionStatus.NOT_STARTED
        return ReportSubsectionStatus.COMPLETE if subsection.complete else ReportSubsectionStatus.IN_PROGRESS


@dataclasses.dataclass
class Submission:
    reports: list[SubmissionReport]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "Submission":
        reports = [SubmissionReport.load_from_json(report_data) for report_data in json_data["reports"]]
        return cls(reports=reports)

    def serialize(self) -> dict:
        return {"reports": [report.serialize() for report in self.reports]}

    def report(self, name: str) -> SubmissionReport:
        existing_report = next((report for report in self.reports if report.name == name), None)
        if not existing_report:
            new_report = SubmissionReport(name=name, programme_project="", sections=[])
            self.reports.append(new_report)
            return new_report
        return existing_report

    def get_form_data(
        self,
        report_name: str,
        section: ReportSection,
        subsection: ReportSubsection,
        page: ReportPage,
        instance_number: int,
    ) -> dict:
        report = self.report(report_name)
        section = report.section(section)
        subsection = section.subsection(subsection)
        page = subsection.page(page, instance_number)
        return page.form_data


def get_submission(programme: Programme) -> Submission:
    pending_submission = PendingSubmission.query.filter_by(programme_id=programme.id).one_or_none()
    if not pending_submission:
        return Submission(reports=[])
    return Submission.load_from_json(pending_submission.data_blob)


def persist_submission(programme: Programme, submission: Submission):
    pending_submission = PendingSubmission.query.filter_by(programme_id=programme.id).one_or_none()
    if not pending_submission:
        pending_submission = PendingSubmission(programme_id=programme.id)
        db.session.add(pending_submission)
    pending_submission.data_blob = submission.serialize()
    db.session.commit()


# submission_structure = FundSubmissionStructure(
#     sections=[
#         ReportSection(
#             name="Project overview",
#             path_fragment="project-overview",
#             subsections=[
#                 ReportSubsection(
#                     name="Progress summary",
#                     path_fragment="progress-summary",  # meh this is a bit duplicative for single-form subsections
#                     pages=[
#                         SubmissionPage(
#                             path_fragment="progress-summary",
#                             form_class=ProjectOverviewProgressSummary,
#                             template="report/project-overview/progress-summary/progress-summary.html",
#                         )
#                     ],
#                 ),
#                 ReportSubsection(
#                     name="Upcoming communications",
#                     path_fragment="upcoming-communications",
#                     pages=[
#                         SubmissionAddMultiplePages(
#                             do_you_need_page=SubmissionPage(
#                                 path_fragment="do-you-have-any",
#                                 form_class=UpcomingCommunicationOpportunities,
#                                 template="report/project-overview/upcoming-communications/do-you-have-any.html",
#                             ),
#                             go_to_details_if=lambda form: form.do_you_have_any.data == "yes",
#                             details_pages=[
#                                 SubmissionPage(
#                                     path_fragment="title",
#                                     form_class=CommunicationOpportunityTitle,
#                                     template="report/project-overview/upcoming-communications/title.html",
#                                 ),
#                                 SubmissionPage(
#                                     path_fragment="details",
#                                     form_class=CommunicationOpportunityDetails,
#                                     template="report/project-overview/upcoming-communications/details.html",
#                                 ),
#                             ],
#                             add_another_page=SubmissionPage(
#                                 path_fragment="add-another",
#                                 form_class=CommunicationOpportunityAddAnother,
#                                 template="report/project-overview/upcoming-communications/add-another.html",
#                             ),
#                             add_another_if=lambda form: form.add_another.data == "yes",
#                             max_repetitions=5,
#                         ),
#                     ],
#                 ),
#                 ReportSubsection(
#                     name="Red-Amber-Green (RAG) Rating",
#                     path_fragment="rag-rating",
#                     pages=[
#                         SubmissionPage(
#                             path_fragment="overall",
#                             form_class=RAGRatingOverall,
#                             template="report/project-overview/rag-rating/overall-rating.html",
#                         ),
#                         SubmissionPage(
#                             path_fragment="schedule",
#                             form_class=RAGRatingSchedule,
#                             template="report/project-overview/rag-rating/schedule-rating.html",
#                         ),
#                         SubmissionPage(
#                             path_fragment="budget",
#                             form_class=RAGRatingBudget,
#                             template="report/project-overview/rag-rating/budget-rating.html",
#                         ),
#                         SubmissionPage(
#                             path_fragment="resourcing",
#                             form_class=RAGRatingResourcing,
#                             template="report/project-overview/rag-rating/resourcing-rating.html",
#                         ),
#                         SubmissionPage(
#                             path_fragment="information",
#                             form_class=RAGRatingInformation,
#                             template="report/project-overview/rag-rating/information.html",
#                         ),
#                     ],
#                 ),
#                 ReportSubsection(
#                     name="Challenges",
#                     path_fragment="challenges",
#                     pages=[
#                         SubmissionAddMultiplePages(
#                             do_you_need_page=SubmissionPage(
#                                 path_fragment="do-you-have-any",
#                                 form_class=ProjectChallengesDoYouHaveAnyForm,
#                                 template="report/project-overview/challenges/do-you-have-any.html",
#                             ),
#                             go_to_details_if=lambda form: form.do_you_have_any.data == "yes",
#                             details_pages=[
#                                 SubmissionPage(
#                                     path_fragment="title",
#                                     form_class=ProjectChallengesTitle,
#                                     template="report/project-overview/challenges/title.html",
#                                 ),
#                                 SubmissionPage(
#                                     path_fragment="details",
#                                     form_class=ProjectChallengesDetails,
#                                     template="report/project-overview/challenges/details.html",
#                                 ),
#                             ],
#                             add_another_page=SubmissionPage(
#                                 path_fragment="add-another",
#                                 form_class=ProjectChallengesAddAnother,
#                                 template="report/project-overview/challenges/add-another.html",
#                             ),
#                             add_another_if=lambda form: form.add_another.data == "yes",
#                             max_repetitions=5,
#                         ),
#                     ],
#                 ),
#             ],
#         ),
#         ReportSection(
#             name="Issues and risks",
#             path_fragment="issues-and-risks",
#             subsections=[
#                 ReportSubsection(
#                     name="Issues",
#                     path_fragment="issues",
#                     pages=[
#                         SubmissionAddMultiplePages(
#                             do_you_need_page=SubmissionPage(
#                                 path_fragment="do-you-have-any",
#                                 form_class=ProjectIssuesDoYouHaveAnyForm,
#                                 template="report/issues-and-risks/issues/do-you-have-any.html",
#                             ),
#                             go_to_details_if=lambda form: form.do_you_have_any.data == "yes",
#                             details_pages=[
#                                 SubmissionPage(
#                                     path_fragment="title",
#                                     form_class=ProjectIssuesTitle,
#                                     template="report/issues-and-risks/issues/title.html",
#                                 ),
#                                 SubmissionPage(
#                                     path_fragment="impact-rating",
#                                     form_class=ProjectIssuesImpactRating,
#                                     template="report/issues-and-risks/issues/impact-rating.html",
#                                 ),
#                                 SubmissionPage(
#                                     path_fragment="details",
#                                     form_class=ProjectIssuesDetails,
#                                     template="report/issues-and-risks/issues/details.html",
#                                 ),
#                             ],
#                             add_another_page=SubmissionPage(
#                                 path_fragment="add-another",
#                                 form_class=ProjectChallengesAddAnother,
#                                 template="report/issues-and-risks/issues/add-another.html",
#                             ),
#                             add_another_if=lambda form: form.add_another.data == "yes",
#                             max_repetitions=5,
#                         )
#                     ],
#                 )
#             ],
#         ),
#     ]
# )
