from dataclasses import dataclass


@dataclass
class ErrorMessage:
    sheet: str
    section: str
    cell_index: str
    description: str
    error_type: str
