import dataclasses
from typing import Type

from report.forms import ReportForm
from report.report_form_components.next_page_condition import NextPageCondition


@dataclasses.dataclass
class ReportFormPage:
    page_id: str
    form_class: Type[ReportForm]
    template: str
    next_page_id: str = None
    next_page_condition: NextPageCondition = None
    form_data: dict[dict] = dataclasses.field(default_factory=dict)

    @property
    def path_fragment(self) -> str:
        return self.page_id.replace("_", "-")

    def set_next_page_id(self, next_page_id: str) -> None:
        self.next_page_id = next_page_id

    def set_next_page_condition(self, next_page_condition: NextPageCondition) -> None:
        self.next_page_condition = next_page_condition

    def set_form_data(self, instance_number: int, form_data: dict) -> None:
        self.form_data[instance_number] = form_data

    def get_form(self, instance_number: int) -> ReportForm:
        form_data = self.form_data.get(instance_number, {})
        return self.form_class(data=form_data)
