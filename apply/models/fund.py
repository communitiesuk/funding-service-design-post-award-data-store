import inspect
from dataclasses import dataclass


@dataclass
class Fund:
    id: str
    name: str
    funding_type: str
    short_name: str
    description: str
    title: str
    welsh_available: bool

    @classmethod
    def from_dict(cls, d: dict):
        # Filter unknown fields from JSON dictionary
        return cls(**{k: v for k, v in d.items() if k in inspect.signature(cls).parameters})
