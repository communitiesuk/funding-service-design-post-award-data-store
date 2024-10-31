import inspect
from dataclasses import dataclass
from typing import List


@dataclass
class Form:
    title: str
    form_name: str

    @staticmethod
    def from_dict(d: dict):
        return Form(**{k: v for k, v in d.items() if k in inspect.signature(Form).parameters})


@dataclass
class ApplicationMapping:
    title: str
    weighting: int
    section_id: str
    children: List[Form]
    requires_feedback: bool = False

    @staticmethod
    def from_dict(d: dict):
        children_data = d.pop("children", [])
        children = [Form.from_dict(child) for child in children_data]
        return ApplicationMapping(
            **{k: v for k, v in d.items() if k in inspect.signature(ApplicationMapping).parameters},
            children=children,
            section_id=d.get("id"),
        )
