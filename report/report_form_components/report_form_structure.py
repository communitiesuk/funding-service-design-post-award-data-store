import dataclasses
import json

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

    def resolve_path_to_components(
        self, section_path: str, subsection_path: str, page_path: str
    ) -> tuple[ReportFormSection, ReportFormSubsection, ReportFormPage]:
        section = next(section for section in self.sections if section.path_fragment == section_path)
        subsection, page = section.resolve_path_to_components(subsection_path, page_path)
        return section, subsection, page

    def get_next_page(
        self, section_path: str, subsection_path: str, page_path: str, form_data: dict
    ) -> ReportFormPage | None:
        _, _, page = self.resolve_path_to_components(section_path, subsection_path, page_path)
        next_page_path = None
        if page.next_page_path:
            next_page_path = page.next_page_path
        if page.next_page_conditions:
            for field, conditions in page.next_page_conditions.items():
                field_value = form_data.get(field)
                if field_value in conditions:
                    next_page_path = conditions[field_value]
        if next_page_path:
            _, _, next_page = self.resolve_path_to_components(section_path, subsection_path, next_page_path)
            return next_page
        return None
