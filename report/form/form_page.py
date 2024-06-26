import dataclasses
from typing import Type

from report.form.next_page_condition import NextPageCondition
from report.forms import ReportForm


@dataclasses.dataclass
class FormPage:
    page_id: str
    form_class: Type[ReportForm]
    template: str
    next_page_id: str = None
    next_page_condition: NextPageCondition = None
    form_data_by_instance: dict[dict] = dataclasses.field(default_factory=dict)

    def set_next_page_id(self, next_page_id: str) -> None:
        self.next_page_id = next_page_id

    def set_next_page_condition(self, next_page_condition: NextPageCondition) -> None:
        self.next_page_condition = next_page_condition

    def load(self, instance_number: int, form_data: dict) -> None:
        self.form_data_by_instance[instance_number] = form_data

    def get_form(self, instance_number: int) -> ReportForm:
        form_data = self.form_data_by_instance.get(instance_number, {})
        return self.form_class(data=form_data)
