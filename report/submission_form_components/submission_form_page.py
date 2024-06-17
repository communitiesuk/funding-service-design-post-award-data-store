import dataclasses
from typing import Type

from report.forms import SubmissionDataForm


@dataclasses.dataclass
class SubmissionFormPage:
    name: str
    path_fragment: str
    form_class: Type[SubmissionDataForm]
    template: str
    next_page: str = None
    next_page_conditions: dict = None

    @classmethod
    def load_from_json(cls, json_data: dict) -> "SubmissionFormPage":
        form_class = load_class_from_name("report.forms", json_data["form_class"])
        return cls(
            name=json_data["name"],
            path_fragment=json_data["path_fragment"],
            form_class=form_class,
            template=json_data["template"],
            next_page=json_data.get("next_page"),
            next_page_conditions=json_data.get("next_page_conditions"),
        )


def load_class_from_name(module_name: str, class_name: str):
    # TODO: Add error handling for import errors
    module = __import__(module_name, fromlist=[class_name])
    return getattr(module, class_name)
