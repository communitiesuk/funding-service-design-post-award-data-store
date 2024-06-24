import dataclasses

from core.db import db
from core.db.entities import PendingSubmission, Programme, ProjectRef
from report.report_form_components.report_form_page import ReportFormPage
from report.report_form_components.report_form_section import ReportFormSection
from report.report_form_components.report_form_subsection import ReportFormSubsection


@dataclasses.dataclass
class ReportPage:
    page_id: str
    form_data: dict

    @classmethod
    def load_from_json(cls, json_data: dict) -> "ReportPage":
        page_id = json_data["page_id"]
        form_data = json_data["form_data"]
        return cls(page_id=page_id, form_data=form_data)

    def serialize(self) -> dict:
        return {"page_id": self.page_id, "form_data": self.form_data}


@dataclasses.dataclass
class ReportSubsection:
    name: str
    pages: list[ReportPage]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "ReportSubsection":
        name = json_data["name"]
        pages = [ReportPage.load_from_json(page_data) for page_data in json_data["pages"]]
        return cls(name=name, pages=pages)

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "pages": [page.serialize() for page in self.pages],
        }

    def get_form_data(self, form_page: ReportFormPage, instance_number: int) -> dict:
        matched_pages = [page for page in self.pages if page.page_id == form_page.page_id]
        if instance_number >= len(matched_pages):
            return {}
        return matched_pages[instance_number].form_data

    def set_form_data(self, form_page: ReportFormPage, instance_number: int, form_data: dict) -> None:
        matched_pages = [page for page in self.pages if page.page_id == form_page.page_id]
        if instance_number >= len(matched_pages):
            new_page = ReportPage(page_id=form_page.page_id, form_data=form_data)
            self.pages.append(new_page)
            return
        existing_page = matched_pages[instance_number]
        existing_page.form_data = form_data


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
            new_subsection = ReportSubsection(name=form_subsection.name, pages=[])
            self.subsections.append(new_subsection)
            return new_subsection
        return existing_subsection


@dataclasses.dataclass
class SubmissionReport:
    name: str
    sections: list[ReportSection]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "Submission":
        name = json_data["name"]
        sections = [ReportSection.load_from_json(section_data) for section_data in json_data["sections"]]
        return cls(name=name, sections=sections)

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "sections": [section.serialize() for section in self.sections],
        }

    def section(self, form_section: ReportFormSection) -> ReportSection:
        existing_section = next((section for section in self.sections if section.name == form_section.name), None)
        if not existing_section:
            new_section = ReportSection(name=form_section.name, subsections=[])
            self.sections.append(new_section)
            return new_section
        return existing_section

    def get_form_data(
        self,
        form_section: ReportFormSection,
        form_subsection: ReportFormSubsection,
        form_page: ReportFormPage,
        instance_number: int,
    ) -> dict:
        section = self.section(form_section)
        subsection = section.subsection(form_subsection)
        return subsection.get_form_data(form_page, instance_number)

    def set_form_data(
        self,
        form_section: ReportFormSection,
        form_subsection: ReportFormSubsection,
        form_page: ReportFormPage,
        instance_number: int,
        form_data: dict,
    ) -> None:
        section = self.section(form_section)
        subsection = section.subsection(form_subsection)
        subsection.set_form_data(form_page, instance_number, form_data)


@dataclasses.dataclass
class Submission:
    programme_report: SubmissionReport
    project_reports: list[SubmissionReport]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "Submission":
        programme_report = SubmissionReport.load_from_json(json_data["programme_report"])
        project_reports = [SubmissionReport.load_from_json(report_data) for report_data in json_data["project_reports"]]
        return cls(programme_report=programme_report, project_reports=project_reports)

    def serialize(self) -> dict:
        return {
            "programme_report": self.programme_report.serialize(),
            "project_reports": [report.serialize() for report in self.project_reports],
        }

    def project_report(self, project: ProjectRef) -> SubmissionReport:
        project_name = project.project_name
        existing_report = next((report for report in self.project_reports if report.name == project_name), None)
        if not existing_report:
            new_report = SubmissionReport(name=project_name, sections=[])
            self.project_reports.append(new_report)
            return new_report
        return existing_report


def get_submission(programme: Programme) -> Submission:
    pending_submission = PendingSubmission.query.filter_by(programme_id=programme.id).one_or_none()
    if not pending_submission:
        return Submission(
            programme_report=SubmissionReport(name=programme.programme_name, sections=[]), project_reports=[]
        )
    return Submission.load_from_json(pending_submission.data_blob)


def persist_submission(programme: Programme, submission: Submission):
    pending_submission = PendingSubmission.query.filter_by(programme_id=programme.id).one_or_none()
    if not pending_submission:
        pending_submission = PendingSubmission(programme_id=programme.id)
        db.session.add(pending_submission)
    pending_submission.data_blob = submission.serialize()
    db.session.commit()
