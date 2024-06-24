import dataclasses
from collections import defaultdict
from enum import Enum

from report.form.form_page import FormPage
from report.form.next_page_condition import NextPageCondition
from report.interfaces import Loadable
from report.pages import AVAILABLE_PAGES_DICT
from report.persistence.report_subsection import ReportSubsection


class SubsectionStatus(Enum):
    NOT_STARTED = "Not started"
    IN_PROGRESS = "In progress"
    COMPLETE = "Complete"


@dataclasses.dataclass
class FormSubsection(Loadable):
    name: str
    path_fragment: str
    pages: list[FormPage]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "FormSubsection":
        pages_data = json_data["pages"]
        pages = []
        for i in range(len(pages_data)):
            page_data = pages_data[i]
            page = AVAILABLE_PAGES_DICT[page_data["page_id"]]
            if not page:
                raise ValueError(f"Page with id {page_data['page_id']} not found in available pages")
            if "next_page_id" in page_data:
                page.set_next_page_id(page_data["next_page_id"])
            elif "next_page_condition" in page_data:
                next_page_condition = NextPageCondition.load_from_json(page_data["next_page_condition"])
                page.set_next_page_condition(next_page_condition)
            elif i < len(pages_data) - 1:
                # Automatically set the next page path fragment for each page to the next page in the list if not set
                next_page_id = pages_data[i + 1]["page_id"]
                page.set_next_page_id(next_page_id)
            pages.append(page)
        return cls(name=json_data["name"], path_fragment=json_data["path_fragment"], pages=pages)

    def resolve_path(self, page_path: str) -> FormPage:
        page = next(page for page in self.pages if page.path_fragment == page_path)
        return page

    def set_form_data(self, report_subsection: ReportSubsection) -> None:
        for page in self.pages:
            instance_number = 0
            while form_data := report_subsection.get_form_data(page, instance_number):
                page.set_form_data(instance_number, form_data)
                instance_number += 1

    def status(self) -> SubsectionStatus:
        first_page = self.pages[0]
        if not first_page.form_data.get(0):
            return SubsectionStatus.NOT_STARTED
        navigator = SubsectionNavigator(subsection=self)
        subsection_complete = navigator.subsection_complete()
        return SubsectionStatus.COMPLETE if subsection_complete else SubsectionStatus.IN_PROGRESS


class SubsectionNavigator:
    def __init__(self, subsection: FormSubsection):
        self.subsection = subsection
        self.page_ids_seen = defaultdict(int)
        self._navigated_forms = []

    def _traverse_path(self, page_id: str) -> None:
        instance_number = self.page_ids_seen[page_id]
        self.page_ids_seen[page_id] += 1
        page = next(page for page in self.subsection.pages if page.page_id == page_id)
        instance_form_data = page.form_data.get(instance_number, {})
        self._navigated_forms.append({"page_id": page.page_id, "data": instance_form_data})
        if page.next_page_id or page.next_page_condition:
            next_page_id = None
            if page.next_page_id:
                next_page_id = page.next_page_id
            elif instance_form_data and page.next_page_condition:
                value = instance_form_data[page.next_page_condition.field]
                next_page_id = page.next_page_condition.value_to_id_mapping.get(value)
            if not next_page_id:
                return
            return self._traverse_path(next_page_id)
        return

    def _navigate(self) -> None:
        self.page_ids_seen = defaultdict(int)
        self._navigated_forms = []
        self._traverse_path(self.subsection.pages[0].page_id)

    def subsection_complete(self) -> bool:
        self._navigate()
        if not self._navigated_forms:
            return False
        final_form = self._navigated_forms[-1]
        return bool(final_form["data"])

    def navigated_forms(self) -> list[dict]:
        self._navigate()
        return self._navigated_forms
