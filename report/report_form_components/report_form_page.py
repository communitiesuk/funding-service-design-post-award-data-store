import dataclasses
from typing import Type

from report.forms import ReportDataForm
from report.report_form_components.next_page_condition import NextPageCondition


@dataclasses.dataclass
class ReportFormPage:
    name: str
    path_fragment: str
    form_class: Type[ReportDataForm]
    template: str
    next_page_path_fragment: str = None
    next_page_condition: NextPageCondition = None
    form_data: dict[dict] = dataclasses.field(default_factory=dict)

    @classmethod
    def load_from_json(cls, json_data: dict) -> "ReportFormPage":
        form_class = load_class_from_name("report.forms", json_data["form_class"])
        next_page_condition = None
        if json_data.get("next_page_condition"):
            next_page_condition = NextPageCondition.load_from_json(json_data["next_page_condition"])
        return cls(
            name=json_data["name"],
            path_fragment=json_data["path_fragment"],
            form_class=form_class,
            template=json_data["template"],
            next_page_path_fragment=json_data.get("next_page_path_fragment"),
            next_page_condition=next_page_condition,
        )

    def set_form_data(self, instance_number: int, form_data: dict) -> None:
        self.form_data[instance_number] = form_data

    def get_form(self, instance_number: int) -> ReportDataForm:
        return self.form_class(data=self.form_data[instance_number])


def load_class_from_name(module_name: str, class_name: str):
    # TODO: Add error handling for import errors
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)
