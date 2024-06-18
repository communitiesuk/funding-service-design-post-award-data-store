import dataclasses

from report.report_form_components.report_form_page import ReportFormPage


@dataclasses.dataclass
class ReportFormSubsection:
    name: str
    path_fragment: str
    pages: list[ReportFormPage]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "ReportFormSubsection":
        pages = [ReportFormPage.load_from_json(page) for page in json_data["pages"]]
        path_fragments = []
        for i in range(len(pages)):
            page: ReportFormPage = pages[i]
            path_fragments.append(page.path_fragment)
            if not page.next_page_path and not page.next_page_conditions and i < len(pages) - 1:
                next_page: ReportFormPage = pages[i + 1]
                page.next_page_path = next_page.path_fragment
                if page.next_page_path in path_fragments:
                    page.backlinked = True
        return cls(name=json_data["name"], path_fragment=json_data["path_fragment"], pages=pages)

    def resolve_path_to_components(self, page_path: str) -> ReportFormPage:
        page = next(page for page in self.pages if page.path_fragment == page_path)
        return page
