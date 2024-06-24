import dataclasses

from report.form.form_page import FormPage
from report.form.form_subsection import FormSubsection
from report.interfaces import Loadable
from report.persistence.report_section import ReportSection


@dataclasses.dataclass
class FormSection(Loadable):
    name: str
    path_fragment: str
    subsections: list[FormSubsection]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "FormSection":
        subsections = [FormSubsection.load_from_json(subsection) for subsection in json_data["subsections"]]
        return cls(name=json_data["name"], path_fragment=json_data["path_fragment"], subsections=subsections)

    def resolve_path(self, subsection_path: str, page_path: str) -> tuple["FormSubsection", "FormPage"]:
        subsection = next(subsection for subsection in self.subsections if subsection.path_fragment == subsection_path)
        page = subsection.resolve_path(page_path)
        return subsection, page

    def set_form_data(self, report_section: ReportSection) -> None:
        for form_subsection in self.subsections:
            report_subsection = report_section.subsection(form_subsection)
            form_subsection.set_form_data(report_subsection)
