import dataclasses
from collections import defaultdict
from enum import Enum

from report.form.form_page import FormPage
from report.form.next_page_condition import NextPageCondition
from report.form_pages import get_form_page
from report.interfaces import Loadable
from report.persistence.report_subsection import ReportSubsection


class SubsectionStatus(Enum):
    NOT_STARTED = "Not started"
    IN_PROGRESS = "In progress"
    COMPLETE = "Complete"


@dataclasses.dataclass
class FormSubsection(Loadable):
    name: str
    path_fragment: str
    check_your_answers: bool
    answers_confirmed: bool
    pages: list[FormPage]

    @classmethod
    def load_from_json(cls, json_data: dict) -> "FormSubsection":
        pages_data = json_data["pages"]
        pages = []
        for i in range(len(pages_data)):  # pylint: disable=consider-using-enumerate
            page_data = pages_data[i]
            page = get_form_page(page_data["page_id"])
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
        return cls(
            name=json_data["name"],
            path_fragment=json_data["path_fragment"],
            check_your_answers=json_data.get("check_your_answers", False),
            answers_confirmed=False,
            pages=pages,
        )

    def __post_init__(self):
        """
        Check that the next page IDs as specified in the JSON file are valid.
        """
        for page in self.pages:
            if page.next_page_id and not self.resolve(page.next_page_id):
                raise ValueError(f"Next page ID {page.next_page_id} (specified for {page.page_id}) not found")
            if page.next_page_condition:
                for page_id in page.next_page_condition.value_to_id_mapping.values():
                    if not self.resolve(page_id):
                        raise ValueError(f"Next page ID {page_id} (specified for {page.page_id}) not found")

    def resolve(self, page_id: str | None) -> FormPage | None:
        return next((page for page in self.pages if page.page_id == page_id), None)

    def load(self, report_subsection: ReportSubsection) -> None:
        for page in self.pages:
            instance_number = 0
            while form_data := report_subsection.get_form_data(page, instance_number):
                page.load(instance_number, form_data)
                instance_number += 1
        self.answers_confirmed = report_subsection.answers_confirmed

    def complete(self) -> bool:
        navigator = SubsectionNavigator(subsection=self)
        navigated_forms = navigator.navigate()
        if not navigated_forms:
            return False
        final_form_navigated = navigated_forms[-1]
        return bool(final_form_navigated["form_data"])

    def status(self) -> SubsectionStatus:
        first_page = self.pages[0]
        if not first_page.form_data.get(0):
            return SubsectionStatus.NOT_STARTED
        if not self.check_your_answers:
            return SubsectionStatus.COMPLETE if self.complete() else SubsectionStatus.IN_PROGRESS
        return SubsectionStatus.COMPLETE if self.complete() and self.answers_confirmed else SubsectionStatus.IN_PROGRESS

    def navigated_forms(self) -> list[dict]:
        navigator = SubsectionNavigator(subsection=self)
        return navigator.navigate()

    def get_next_page(self, current_page: FormPage, form_data: dict) -> FormPage | None:
        next_page_id = None
        if current_page.next_page_id:
            next_page_id = current_page.next_page_id
        elif current_page.next_page_condition:
            value = form_data.get(current_page.next_page_condition.field)
            next_page_id = current_page.next_page_condition.value_to_id_mapping.get(value)
        if next_page_id:
            return self.resolve(next_page_id)
        return None


class SubsectionNavigator:
    subsection: FormSubsection
    page_ids_seen: defaultdict[int]
    navigated_forms: list[dict]

    def __init__(self, subsection: FormSubsection):
        self.subsection = subsection
        self.page_ids_seen = defaultdict(int)
        self.navigated_forms = []

    def _traverse_path(self, page_id: str) -> None:
        instance_number = self.page_ids_seen[page_id]
        self.page_ids_seen[page_id] += 1
        page = self.subsection.resolve(page_id)
        instance_form_data = page.form_data.get(instance_number, {})
        self.navigated_forms.append(
            {
                "page_id": page.page_id,
                "instance_number": instance_number,
                "form_data": instance_form_data,
            }
        )
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

    def navigate(self) -> list[dict]:
        self.page_ids_seen = defaultdict(int)
        self.navigated_forms = []
        self._traverse_path(self.subsection.pages[0].page_id)
        return self.navigated_forms
