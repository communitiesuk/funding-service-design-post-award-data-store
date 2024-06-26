import dataclasses
import os
from abc import ABC, abstractmethod
from typing import Type

from report.flask_form import CustomFlaskForm
from report.form.next_page_condition import NextPageCondition

TEMPLATE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "templates")


@dataclasses.dataclass
class FormPage(ABC):
    next_page_id: str = None
    next_page_condition: NextPageCondition = None
    form_data_by_instance: dict[dict] = dataclasses.field(default_factory=dict)

    @property
    @abstractmethod
    def page_id(self) -> str:
        pass

    @property
    @abstractmethod
    def template(self) -> str:
        pass

    @property
    @abstractmethod
    def form_class(self) -> Type[CustomFlaskForm]:
        pass

    def __post_init__(self):
        if not os.path.exists(os.path.join(TEMPLATE_DIR, self.template)):
            raise ValueError(f"Template file not found: {self.template}")

    def set_next_page_id(self, next_page_id: str) -> None:
        self.next_page_id = next_page_id

    def set_next_page_condition(self, next_page_condition: NextPageCondition) -> None:
        self.next_page_condition = next_page_condition

    def load(self, instance_number: int, form_data: dict) -> None:
        self.form_data_by_instance[instance_number] = form_data

    def get_form(self, instance_number: int) -> CustomFlaskForm:
        form_data = self.form_data_by_instance.get(instance_number, {})
        return self.form_class(data=form_data)
