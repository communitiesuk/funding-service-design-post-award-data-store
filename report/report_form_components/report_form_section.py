import dataclasses

from report.report_form_components.report_form_page import ReportFormPage
from report.report_form_components.report_form_subsection import ReportFormSubsection


@dataclasses.dataclass
class ReportFormSection:
    name: str
    path_fragment: str
    subsections: list[ReportFormSubsection]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "ReportFormSection":
        subsections = [ReportFormSubsection.load_from_json(subsection) for subsection in json_data["subsections"]]
        return cls(name=json_data["name"], path_fragment=json_data["path_fragment"], subsections=subsections)

    def resolve_path_to_components(
        self, subsection_path: str, page_path: str
    ) -> tuple[ReportFormSubsection, ReportFormPage]:
        subsection = next(subsection for subsection in self.subsections if subsection.path_fragment == subsection_path)
        page = subsection.resolve_path_to_components(page_path)
        return subsection, page
