from dataclasses import dataclass
from typing import List

from app.models.application_parts.question import Question


@dataclass
class Form:
    name: str
    status: str
    questions: List[Question]
    metadata: str
