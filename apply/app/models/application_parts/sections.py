from dataclasses import dataclass
from typing import Dict


@dataclass
class Sections:
    Sections: Dict


COF_R2_SECTION_DISPLAY_CONFIG = {
    "About your organisation": {
        "forms_within_section": {
            "organisation-information": None,
            "applicant-information": None,
        },
        "section_weighting": None,
    },
    "About your project": {
        "forms_within_section": {
            "project-information": None,
            "asset-information": None,
        },
        "section_weighting": None,
    },
    "Strategic case": {
        "forms_within_section": {
            "community-use": None,
            "community-engagement": None,
            "local-support": None,
            "environmental-sustainability": None,
        },
        "section_weighting": 30,
    },
    "Management case": {
        "forms_within_section": {
            "funding-required": None,
            "feasibility": None,
            "risk": None,
            "project-costs": None,
            "skills-and-resources": None,
            "community-representation": None,
            "inclusiveness-and-integration": None,
            "upload-business-plan": None,
        },
        "section_weighting": 30,
    },
    "Potential to deliver community benefits": {
        "forms_within_section": {"community-benefits": None},
        "section_weighting": 30,
    },
    "Added value to community": {
        "forms_within_section": {"value-to-the-community": None},
        "section_weighting": 10,
    },
    "Subsidy control / state aid": {
        "forms_within_section": {"project-qualification": None},
        "section_weighting": None,
    },
    "Check declarations": {
        "forms_within_section": {"declarations": None},
        "section_weighting": None,
    },
}
