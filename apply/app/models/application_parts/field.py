from dataclasses import dataclass


@dataclass
class Field:
    key: str
    title: str
    type: str
    answer: str
