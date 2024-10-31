from __future__ import annotations

import inspect
from dataclasses import dataclass


@dataclass
class FeedbackSurveyConfig:
    has_feedback_survey: bool = False
    is_feedback_survey_optional: bool = True
    has_section_feedback: bool = False
    is_section_feedback_optional: bool = True
    has_research_survey: bool = False
    is_research_survey_optional: bool = True

    @classmethod
    def from_dict(cls, d: dict):
        # Filter unknown fields from JSON dictionary
        return cls(**{k: v for k, v in d.items() if k in inspect.signature(cls).parameters})


@dataclass
class Round:
    id: str
    assessment_deadline: str
    deadline: str
    fund_id: str
    opens: str
    title: str
    short_name: str
    prospectus: str
    privacy_notice: str
    instructions: str
    contact_us_banner: str
    contact_email: str
    contact_phone: str
    contact_textphone: str
    support_days: str
    support_times: str
    feedback_link: str
    project_name_field_id: str
    application_guidance: str
    mark_as_complete_enabled: bool = False
    is_expression_of_interest: bool = False
    reference_contact_page_over_email: bool = False
    feedback_survey_config: FeedbackSurveyConfig = None
    has_eligibility: bool = False

    def __post_init__(self):
        if isinstance(self.feedback_survey_config, dict):
            self.feedback_survey_config = FeedbackSurveyConfig.from_dict(self.feedback_survey_config)
        elif self.feedback_survey_config is None:
            self.feedback_survey_config = FeedbackSurveyConfig()

    @classmethod
    def from_dict(cls, d: dict):
        # Filter unknown fields from JSON dictionary
        return cls(
            **{k: v for k, v in d.items() if k in inspect.signature(cls).parameters},
            has_eligibility=d["eligibility_config"]["has_eligibility"],
        )
