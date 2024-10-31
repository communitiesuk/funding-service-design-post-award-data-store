from enum import auto
from enum import Enum


class ApplicationStatus(Enum):
    NOT_STARTED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()
    SUBMITTED = auto()
