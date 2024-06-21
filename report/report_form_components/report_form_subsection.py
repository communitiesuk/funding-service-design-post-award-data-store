import dataclasses
from collections import defaultdict
from enum import Enum

from report.report_form_components.report_form_page import ReportFormPage


class SubsectionStatus(Enum):
    NOT_STARTED = "Not started"
    IN_PROGRESS = "In progress"
    COMPLETE = "Complete"


@dataclasses.dataclass
class ReportFormSubsection:
    name: str
    path_fragment: str
    pages: list[ReportFormPage]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "ReportFormSubsection":
        pages = [ReportFormPage.load_from_json(page) for page in json_data["pages"]]
        # Automatically set the next page path fragment for each page to the next page in the list if it is not set
        for i in range(len(pages)):
            page: ReportFormPage = pages[i]
            if not page.next_page_path_fragment and not page.next_page_condition and i < len(pages) - 1:
                next_page: ReportFormPage = pages[i + 1]
                page.next_page_path_fragment = next_page.path_fragment
        return cls(name=json_data["name"], path_fragment=json_data["path_fragment"], pages=pages)

    def resolve_path(self, page_path: str) -> ReportFormPage:
        page = next(page for page in self.pages if page.path_fragment == page_path)
        return page

    def status(self) -> SubsectionStatus:
        first_page = self.pages[0]
        if not first_page.form_data.get(0):
            return SubsectionStatus.NOT_STARTED
        navigator = SubsectionNavigator(subsection=self)
        subsection_complete = navigator.subsection_complete()
        return SubsectionStatus.COMPLETE if subsection_complete else SubsectionStatus.IN_PROGRESS


class SubsectionNavigator:
    def __init__(self, subsection: ReportFormSubsection):
        self.subsection = subsection
        self.path_fragments_seen = defaultdict(int)
        self._navigated_forms = []

    def _traverse_path(self, path_fragment: str) -> None:
        instance_number = self.path_fragments_seen[path_fragment]
        self.path_fragments_seen[path_fragment] += 1
        page = self.subsection.resolve_path(path_fragment)
        instance_form_data = page.form_data.get(instance_number, {})
        self._navigated_forms.append({"name": page.name, "data": instance_form_data})
        if page.next_page_path_fragment or page.next_page_condition:
            next_page_path_fragment = None
            if page.next_page_path_fragment:
                next_page_path_fragment = page.next_page_path_fragment
            elif instance_form_data and page.next_page_condition:
                value = instance_form_data[page.next_page_condition.field]
                next_page_path_fragment = page.next_page_condition.value_to_path_mapping.get(value)
            if not next_page_path_fragment:
                return
            return self._traverse_path(next_page_path_fragment)
        return

    def _navigate(self) -> None:
        self.path_fragments_seen = defaultdict(int)
        self._navigated_forms = []
        self._traverse_path(self.subsection.pages[0].path_fragment)

    def subsection_complete(self) -> bool:
        self._navigate()
        if not self._navigated_forms:
            return False
        final_form = self._navigated_forms[-1]
        return bool(final_form["data"])

    def navigated_forms(self) -> list[dict]:
        self._navigate()
        return self._navigated_forms
