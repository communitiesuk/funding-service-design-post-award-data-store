import dataclasses
import json

from report.submission_form_components.submission_form_page import SubmissionFormPage
from report.submission_form_components.submission_form_section import SubmissionFormSection
from report.submission_form_components.submission_form_subsection import SubmissionFormSubsection


@dataclasses.dataclass
class SubmissionFormStructure:
    sections: list[SubmissionFormSection]

    @classmethod
    def load_from_json(cls, file_path: str) -> "SubmissionFormStructure":
        # Need to add logic to prevent duplicate named sections, subsections and pages
        with open(file_path, "r") as file:
            json_data = json.load(file)
        sections = [SubmissionFormSection.load_from_json(section) for section in json_data["sections"]]
        return cls(sections=sections)

    def resolve_path_to_components(
        self, section_path: str, subsection_path: str, page_path: str
    ) -> tuple[SubmissionFormSection, SubmissionFormSubsection, SubmissionFormPage]:
        section = next(section for section in self.sections if section.path_fragment == section_path)
        subsection, page = section.resolve_path_to_components(subsection_path, page_path)
        return section, subsection, page
