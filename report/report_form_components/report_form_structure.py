import dataclasses
import json

from report.persistence import SubmissionReport
from report.report_form_components.report_form_page import ReportFormPage
from report.report_form_components.report_form_section import ReportFormSection
from report.report_form_components.report_form_subsection import ReportFormSubsection


@dataclasses.dataclass
class ReportFormStructure:
    sections: list[ReportFormSection]

    @classmethod
    def load_from_json(cls, file_path: str) -> "ReportFormStructure":
        # Need to add logic to prevent duplicate named sections, subsections and pages
        with open(file_path, "r") as file:
            json_data = json.load(file)
        sections = [ReportFormSection.load_from_json(section) for section in json_data["sections"]]
        return cls(sections=sections)

    def resolve_path(
        self, section_path: str, subsection_path: str, page_path: str
    ) -> tuple[ReportFormSection, ReportFormSubsection, ReportFormPage]:
        section = next(section for section in self.sections if section.path_fragment == section_path)
        subsection, page = section.resolve_path(subsection_path, page_path)
        return section, subsection, page

    def get_next_page(
        self, section_path: str, subsection_path: str, page_path: str, form_data: dict
    ) -> ReportFormPage | None:
        _, _, page = self.resolve_path(section_path, subsection_path, page_path)
        next_page_id = None
        if page.next_page_id:
            next_page_id = page.next_page_id
        elif page.next_page_condition:
            value = form_data.get(page.next_page_condition.field)
            next_page_id = page.next_page_condition.value_to_id_mapping.get(value)
        if next_page_id:
            next_page_path = next_page_id.replace("_", "-")
            _, _, next_page = self.resolve_path(section_path, subsection_path, next_page_path)
            return next_page
        return None

    def set_all_form_data(self, report: SubmissionReport) -> None:
        for section in self.sections:
            for subsection in section.subsections:
                for page in subsection.pages:
                    instance_number = 0
                    while form_data := report.get_form_data(section, subsection, page, instance_number):
                        page.set_form_data(instance_number, form_data)
                        instance_number += 1
