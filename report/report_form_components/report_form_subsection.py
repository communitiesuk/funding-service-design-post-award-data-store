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
    path_fragments_seen: dict[str] = dataclasses.field(default_factory=lambda: defaultdict(int))

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

    def navigation_complete(self, path_fragment: str, instance_number: int) -> bool:
        self.path_fragments_seen[path_fragment] += 1
        page = self.resolve_path(path_fragment)
        instance_form_data = page.form_data.get(instance_number)
        if not instance_form_data:
            return False
        if page.next_page_path_fragment or page.next_page_condition:
            next_page_path_fragment = None
            if page.next_page_path_fragment:
                next_page_path_fragment = page.next_page_path_fragment
            elif page.next_page_condition:
                value = instance_form_data[page.next_page_condition.field]
                next_page_path_fragment = page.next_page_condition.value_to_path_mapping.get(value)
            if not next_page_path_fragment:
                return True
            instance_number = self.path_fragments_seen[path_fragment]
            return self.navigation_complete(next_page_path_fragment, instance_number)
        return True

    def status(self) -> SubsectionStatus:
        first_page = self.pages[0]
        if not first_page.form_data.get(0):
            return SubsectionStatus.NOT_STARTED
        navigation_complete = self.navigation_complete(first_page.path_fragment, 0)
        return SubsectionStatus.COMPLETE if navigation_complete else SubsectionStatus.IN_PROGRESS
