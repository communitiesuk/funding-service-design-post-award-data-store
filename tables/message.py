from dataclasses import dataclass


@dataclass
class ErrorMessage:
    sheet: str
    cell_index: str
    description: str
    error_type: str
