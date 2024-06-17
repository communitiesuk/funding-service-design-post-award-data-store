import dataclasses

from report.submission_form_components.submission_form_page import SubmissionFormPage
from report.submission_form_components.submission_form_subsection import SubmissionFormSubsection


@dataclasses.dataclass
class SubmissionFormSection:
    name: str
    path_fragment: str
    subsections: list[SubmissionFormSubsection]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "SubmissionFormSection":
        subsections = [SubmissionFormSubsection.load_from_json(subsection) for subsection in json_data["subsections"]]
        return cls(name=json_data["name"], path_fragment=json_data["path_fragment"], subsections=subsections)

    def resolve_path_to_components(
        self, subsection_path: str, page_path: str
    ) -> tuple[SubmissionFormSubsection, SubmissionFormPage]:
        subsection = next(subsection for subsection in self.subsections if subsection.path_fragment == subsection_path)
        page = subsection.resolve_path_to_components(page_path)
        return subsection, page
