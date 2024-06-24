import dataclasses
import json

from report.form.form_page import FormPage
from report.form.form_section import FormSection
from report.form.form_subsection import FormSubsection
from report.persistence.report import Report


@dataclasses.dataclass
class FormStructure:
    sections: list[FormSection]

    @classmethod
    def load_from_json(cls, file_path: str) -> "FormStructure":
        # Need to add logic to prevent duplicate named sections, subsections and pages
        with open(file_path, "r") as file:
            json_data = json.load(file)
        sections = [FormSection.load_from_json(section) for section in json_data["sections"]]
        return cls(sections=sections)

    def resolve_path(
        self, section_path: str, subsection_path: str, page_path: str
    ) -> tuple[FormSection, FormSubsection, FormPage]:
        section = next(section for section in self.sections if section.path_fragment == section_path)
        subsection, page = section.resolve_path(subsection_path, page_path)
        return section, subsection, page

    def get_next_page(
        self, section_path: str, subsection_path: str, page_path: str, form_data: dict
    ) -> FormPage | None:
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

    def set_form_data(self, report: Report) -> None:
        for form_section in self.sections:
            report_section = report.section(form_section)
            form_section.set_form_data(report_section)
