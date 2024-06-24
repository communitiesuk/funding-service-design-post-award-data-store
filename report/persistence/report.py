import dataclasses
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from report.form.form_page import FormPage
    from report.form.form_section import FormSection
    from report.form.form_subsection import FormSubsection

from report.interfaces import Loadable, Serializable
from report.persistence.report_section import ReportSection


@dataclasses.dataclass
class Report(Loadable, Serializable):
    name: str
    sections: list[ReportSection]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "Report":
        name = json_data["name"]
        sections = [ReportSection.load_from_json(section_data) for section_data in json_data["sections"]]
        return cls(name=name, sections=sections)

    def serialize(self) -> dict:
        return {
            "name": self.name,
            "sections": [section.serialize() for section in self.sections],
        }

    def section(self, form_section: "FormSection") -> ReportSection:
        existing_section = next((section for section in self.sections if section.name == form_section.name), None)
        if not existing_section:
            new_section = ReportSection(name=form_section.name, subsections=[])
            self.sections.append(new_section)
            return new_section
        return existing_section

    def get_form_data(
        self,
        form_section: "FormSection",
        form_subsection: "FormSubsection",
        form_page: "FormPage",
        instance_number: int,
    ) -> dict:
        section = self.section(form_section)
        subsection = section.subsection(form_subsection)
        return subsection.get_form_data(form_page, instance_number)

    def set_form_data(
        self,
        form_section: "FormSection",
        form_subsection: "FormSubsection",
        form_page: "FormPage",
        instance_number: int,
        form_data: dict,
    ) -> None:
        section = self.section(form_section)
        subsection = section.subsection(form_subsection)
        subsection.set_form_data(form_page, instance_number, form_data)
