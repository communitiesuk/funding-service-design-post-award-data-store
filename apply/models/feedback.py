from dataclasses import dataclass
from typing import Dict


@dataclass
class FeedbackDetails:
    comment: str
    rating: str


@dataclass
class FeedbackSubmission:
    application_id: str
    date_submitted: str
    feedback: FeedbackDetails
    fund_id: str
    id: str
    round_id: str
    section_id: str
    status: str

    @classmethod
    def from_dict(cls, data: Dict):
        feedback_data = data["feedback"]
        feedback = FeedbackDetails(comment=feedback_data["comment"], rating=feedback_data["rating"])

        return cls(
            application_id=data["application_id"],
            date_submitted=data["date_submitted"],
            feedback=feedback,
            fund_id=data["fund_id"],
            id=data["id"],
            round_id=data["round_id"],
            section_id=data["section_id"],
            status=data["status"],
        )


@dataclass
class EndOfApplicationSurveyData:
    application_id: str
    data: dict[str, object]
    date_submitted: str
    fund_id: str
    id: int
    page_number: int
    round_id: str

    @classmethod
    def from_dict(cls, data_dict):
        return cls(**data_dict)
