import dataclasses
import json
from enum import Enum

from core.db.entities import Fund
from report.form.form_page import FormPage
from report.form.form_section import FormSection
from report.form.form_subsection import FormSubsection
from report.interfaces import Loadable
from report.persistence.report import Report


class ProgrammeProject(Enum):
    PROGRAMME = 1
    PROJECT = 2


def get_form_json(fund: Fund, programme_project: ProgrammeProject) -> dict:
    path_mapping = {
        "HS": {
            ProgrammeProject.PROGRAMME: "report/form_configs/default_programme.json",
            ProgrammeProject.PROJECT: "report/form_configs/default_project.json",
        }
    }
    file_path = path_mapping[fund.fund_code][programme_project]
    with open(file_path, "r", encoding="utf-8") as file:
        json_data = json.load(file)
    return json_data


@dataclasses.dataclass
class FormStructure(Loadable):
    sections: list[FormSection]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "FormStructure":
        sections = [FormSection.load_from_json(section) for section in json_data["sections"]]

        # Check for duplicate page IDs
        page_ids = set()
        for section in sections:
            for subsection in section.subsections:
                for page in subsection.pages:
                    if page.page_id in page_ids:
                        raise ValueError(f"Duplicate page ID found: {page.page_id}")
                    page_ids.add(page.page_id)

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
