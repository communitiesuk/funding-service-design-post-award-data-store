import dataclasses
import json

from report.form.form_page import FormPage
from report.form.form_section import FormSection
from report.form.form_subsection import FormSubsection
from report.interfaces import Loadable
from report.persistence.report import Report


@dataclasses.dataclass
class FormStructure(Loadable):
    sections: list[FormSection]

    @classmethod
    def load_from_json(cls, file_path: str) -> "FormStructure":
        # Need to add logic to prevent duplicate named sections, subsections and pages
        with open(file_path, "r") as file:
            json_data = json.load(file)
        sections = [FormSection.load_from_json(section) for section in json_data["sections"]]
        return cls(sections=sections)

    def resolve(
        self, section_path: str, subsection_path: str, page_id: str | None
    ) -> tuple[FormSection, FormSubsection, FormPage]:
        section = next(section for section in self.sections if section.path_fragment == section_path)
        subsection, page = section.resolve(subsection_path, page_id)
        return section, subsection, page

    def load(self, report: Report) -> None:
        for form_section in self.sections:
            report_section = report.section(form_section)
            form_section.load(report_section)
