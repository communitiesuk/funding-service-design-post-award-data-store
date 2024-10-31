from dataclasses import dataclass


@dataclass
class ResearchSurveyData:
    application_id: str
    data: dict[str, object]
    date_submitted: str
    fund_id: str
    id: int
    round_id: str

    @classmethod
    def from_dict(cls, data_dict):
        return cls(**data_dict)
