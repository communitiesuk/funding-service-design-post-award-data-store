import dataclasses
from typing import Type

from report.forms import ReportDataForm


@dataclasses.dataclass
class ReportFormPage:
    name: str
    path_fragment: str
    form_class: Type[ReportDataForm]
    template: str
    next_page_path: str = None
    next_page_conditions: dict = None
    backlinked: bool = False

    @classmethod
    def load_from_json(cls, json_data: dict) -> "ReportFormPage":
        form_class = load_class_from_name("report.forms", json_data["form_class"])
        return cls(
            name=json_data["name"],
            path_fragment=json_data["path_fragment"],
            form_class=form_class,
            template=json_data["template"],
            next_page_path=json_data.get("next_page_path"),
            next_page_conditions=json_data.get("next_page_conditions"),
        )


def load_class_from_name(module_name: str, class_name: str):
    # TODO: Add error handling for import errors
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)
