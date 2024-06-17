import dataclasses

from report.submission_form_components.submission_form_page import SubmissionFormPage


@dataclasses.dataclass
class SubmissionFormSubsection:
    name: str
    path_fragment: str
    pages: list[SubmissionFormPage]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "SubmissionFormSubsection":
        pages = [SubmissionFormPage.load_from_json(page) for page in json_data["pages"]]
        return cls(name=json_data["name"], path_fragment=json_data["path_fragment"], pages=pages)

    def resolve_path_to_components(self, page_path: str) -> SubmissionFormPage:
        page = next(page for page in self.pages if page.path_fragment == page_path)
        return page
