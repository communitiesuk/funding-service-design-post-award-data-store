from datetime import datetime

from apply.models.application import Application
from apply.models.application_summary import ApplicationSummary
from apply.models.round import Round
from tests.api_data.test_data_forms import COF_TEST_FORMS

common_round_data = {
    "opens": "2022-09-01T00:00:01",
    "assessment_deadline": "2030-03-20T00:00:01",
    "contact_us_banner": "",
    "contact_email": "test@example.com",
    "contact_phone": "123456789",
    "contact_textphone": "123456789",
    "support_times": "9-5",
    "support_days": "Mon-Fri",
    "prospectus": "/cof_r2w2_prospectus",
    "instructions": "Round specific instruction text",
    "privacy_notice": "http://privacy.com",
    "project_name_field_id": "",
    "feedback_link": "http://feedback.com",
    "application_guidance": "",
    "mark_as_complete_enabled": False,
    "is_expression_of_interest": False,
    "eligibility_config": {"has_eligibility": True},
}
common_application_data = {
    "account_id": "test-user",
    "reference": "TEST-REF-B",
    "project_name": "Test project",
    "date_submitted": None,
    "started_at": "2022-05-20T14:47:12",
    "last_edited": "2022-05-24T11:03:59",
    "language": "en",
    "id": "xxxx",
    "status": "IN_PROGRESS",
    "fund_id": "xxx",
    "round_id": "xxx",
}
TEST_APPLICATION_SUMMARIES = [
    ApplicationSummary.from_dict(
        {
            **common_application_data,
            "id": "1111",
            "status": "IN_PROGRESS",
            "fund_id": "111",
            "round_id": "fsd-r2w2",
        }
    ),
    ApplicationSummary.from_dict(
        {
            **common_application_data,
            "id": "2222",
            "status": "NOT_STARTED",
            "fund_id": "111",
            "round_id": "fsd-r2w3",
        }
    ),
    ApplicationSummary.from_dict(
        {
            **common_application_data,
            "id": "3333",
            "status": "SUBMITTED",
            "fund_id": "222",
            "round_id": "abc-r1",
        }
    ),
    ApplicationSummary.from_dict(
        {
            **common_application_data,
            "id": "4444",
            "status": "READY_TO_SUBMIT",
            "fund_id": "222",
            "round_id": "abc-r1",
        }
    ),
]
TEST_FUNDS_DATA = [
    {
        "id": "111",
        "name": "Test Fund",
        "description": "test test",
        "short_name": "FSD",
        "title": "fund for testing",
        "welsh_available": True,
        "funding_type": "COMPETITIVE",
    },
    {
        "id": "222",
        "name": "Test Fund 2",
        "description": "test test 2",
        "short_name": "FSD2",
        "title": "fund for testing 2",
        "welsh_available": False,
        "funding_type": "COMPETITIVE",
    },
    {
        "id": "333",
        "name": "Welsh Fund",
        "description": "test test 2",
        "short_name": "FSD2",
        "title": "gronfa cymraeg",
        "welsh_available": True,
        "funding_type": "COMPETITIVE",
    },
]

TEST_ROUNDS_DATA = [
    Round.from_dict(
        {
            **common_round_data,
            "fund_id": "111",
            "id": "fsd-r2w2",
            "short_name": "r2w2",
            "title": "closed_round",
            "deadline": "2023-01-01T00:00:01",
        }
    ),
    Round.from_dict(
        {
            **common_round_data,
            "fund_id": "111",
            "id": "fsd-r2w3",
            "short_name": "r2w3",
            "title": "open_round",
            "deadline": "2050-01-01T00:00:01",
        }
    ),
    Round.from_dict(
        {
            **common_round_data,
            "fund_id": "222",
            "id": "abc-r1",
            "short_name": "r1",
            "title": "closed_round",
            "deadline": "2023-01-01T00:00:01",
        }
    ),
    Round.from_dict(
        {
            **common_round_data,
            "fund_id": "222",
            "id": "abc-r2",
            "short_name": "r2",
            "title": "open_round",
            "deadline": "2050-01-01T00:00:01",
        }
    ),
]

TEST_DISPLAY_DATA = {
    "total_applications_to_display": 4,
    "funds": [
        {
            "fund_data": {
                "id": "funding-service-design",
                "name": "Test Fund",
                "description": "test test",
                "short_name": "FSD",
                "funding_type": "COMPETITIVE",
            },
            "rounds": [
                {
                    "is_past_submission_deadline": True,
                    "is_not_yet_open": False,
                    "round_details": {
                        "opens": "2022-09-01T00:00:01",
                        "deadline": "2030-01-30T00:00:01",
                        "assessment_deadline": "2030-03-20T00:00:01",
                        "id": "cof-r2w2",
                        "title": "Round 2 Window 2",
                        "instructions": "r2w2 instructions",
                        "fund_id": "fund-service-design",
                        "short_name": "R2W2",
                        "contact_email": "test@example.com",
                        "contact_phone": "123456789",
                        "contact_textphone": "123456789",
                        "support_times": "9-5",
                        "support_days": "Mon-Fri",
                    },
                    "applications": [
                        {
                            "id": "uuidv4",
                            "reference": "TEST-REF-B",
                            "status": "NOT_SUBMITTED",
                            "round_id": "summer",
                            "fund_id": "funding-service-design",
                            "started_at": "2020-01-01T12:03:00",
                            "project_name": None,
                            "last_edited": datetime.strptime("2020-01-01T12:03:00", "%Y-%m-%dT%H:%M:%S"),
                        },
                        {
                            "id": "ed221ac8-5d4d-42dd-ab66-6cbcca8fe257",
                            "reference": "TEST-REF-C",
                            "status": "SUBMITTED",
                            "round_id": "summer",
                            "fund_id": "funding-service-design",
                            "started_at": "2023-01-01T12:01:00",
                            "project_name": "",
                            "last_edited": None,
                        },
                    ],
                },
                {
                    "is_past_submission_deadline": False,
                    "is_not_yet_open": False,
                    "round_details": {
                        "opens": "2022-09-01T00:00:01",
                        "deadline": "2030-01-30T00:00:01",
                        "assessment_deadline": "2030-03-20T00:00:01",
                        "id": "summer",
                        "title": "Summer round",
                        "fund_id": "fund-service-design",
                        "short_name": "R2W3",
                        "instructions": "r2w3 instructions",
                        "contact_email": "test@example.com",
                        "contact_phone": "123456789",
                        "contact_textphone": "123456789",
                        "support_times": "9-5",
                        "support_days": "Mon-Fri",
                    },
                    "applications": [
                        {
                            "id": "uuidv4",
                            "reference": "TEST-REF-B",
                            "status": "IN_PROGRESS",
                            "round_id": "summer",
                            "fund_id": "funding-service-design",
                            "started_at": "2020-01-01T12:03:00",
                            "project_name": None,
                            "last_edited": datetime.strptime("2020-01-01T12:03:00", "%Y-%m-%dT%H:%M:%S"),
                        },
                        {
                            "id": "ed221ac8-5d4d-42dd-ab66-6cbcca8fe257",
                            "reference": "TEST-REF-C",
                            "status": "READY_TO_SUBMIT",
                            "round_id": "summer",
                            "fund_id": "funding-service-design",
                            "started_at": "2023-01-01T12:01:00",
                            "project_name": "",
                            "last_edited": None,
                        },
                    ],
                },
            ],
        }
    ],
}
TEST_APPLICATIONS = [
    Application.from_dict(
        {
            "id": "test-application-id",
            "account_id": "test-user",
            "date_submitted": "2022-10-11T10:01:25.216743",
            "fund_id": "funding-service-design",
            "last_edited": "2022-10-11T09:49:00.542371",
            "project_name": "Project name",
            "reference": "TEST-REF",
            "round_id": "summer",
            "round_name": "Round T Window T",
            "started_at": "2022-10-11T09:43:40.632095",
            "status": "IN_PROGRESS",
            "language": "en",
            "forms": COF_TEST_FORMS,
        }
    ),
    Application.from_dict(
        {
            "id": "test-welsh-id",
            "account_id": "test-user",
            "date_submitted": "2022-10-11T10:01:25.216743",
            "fund_id": "333",
            "last_edited": "2022-10-11T09:49:00.542371",
            "project_name": "Project name",
            "reference": "TEST-REF",
            "round_id": "summer",
            "round_name": "Round T Window T",
            "started_at": "2022-10-11T09:43:40.632095",
            "status": "IN_PROGRESS",
            "language": "cy",
            "forms": COF_TEST_FORMS,
        }
    ),
]

SUBMITTED_APPLICATION = Application.from_dict(
    {
        "id": "test-application-id",
        "account_id": "test-user",
        "date_submitted": "2022-10-11T10:01:25.216743",
        "fund_id": "funding-service-design",
        "last_edited": "2022-10-11T09:49:00.542371",
        "project_name": "Project name",
        "reference": "TEST-REF",
        "round_id": "summer",
        "round_name": "Round T Window T",
        "started_at": "2022-10-11T09:43:40.632095",
        "status": "SUBMITTED",
        "language": "en",
        "forms": [],
    }
)

NOT_STARTED_APPLICATION = Application.from_dict(
    {
        "id": "test_id",
        "account_id": "test-user",
        "status": "NOT_STARTED",
        "fund_id": "funding-service-design",
        "round_id": "summer",
        "reference": "TEST-REF-A",
        "project_name": None,
        "date_submitted": None,
        "started_at": "2022-05-20T14:47:12",
        "last_edited": None,
        "language": "en",
        "feedback_survey_config": {
            "has_feedback_survey": True,
            "has_section_feedback": True,
            "is_feedback_survey_optional": False,
            "is_section_feedback_optional": False,
        },
        "forms": [
            {
                "name": "applicant-information",
                "questions": [],
                "status": "NOT_STARTED",
            },
            {
                "name": "asset-information",
                "questions": [],
                "status": "NOT_STARTED",
            },
            {
                "name": "community-benefits",
                "questions": [],
                "status": "NOT_STARTED",
            },
            {
                "name": "community-engagement",
                "questions": [],
                "status": "NOT_STARTED",
            },
            {
                "name": "community-representation",
                "questions": [],
                "status": "NOT_STARTED",
            },
            {
                "name": "community-use",
                "questions": [],
                "status": "NOT_STARTED",
            },
            {"name": "declarations", "questions": [], "status": "NOT_STARTED"},
            {
                "name": "environmental-sustainability",
                "questions": [],
                "status": "NOT_STARTED",
            },
            {"name": "feasibility", "questions": [], "status": "NOT_STARTED"},
            {
                "name": "funding-required",
                "questions": [],
                "status": "NOT_STARTED",
            },
            {
                "name": "inclusiveness-and-integration",
                "questions": [],
                "status": "NOT_STARTED",
            },
            {
                "name": "local-support",
                "questions": [],
                "status": "NOT_STARTED",
            },
            {
                "name": "organisation-information",
                "questions": [],
                "status": "NOT_STARTED",
            },
            {
                "name": "project-costs",
                "questions": [],
                "status": "NOT_STARTED",
            },
            {
                "name": "project-information",
                "questions": [],
                "status": "NOT_STARTED",
            },
            {
                "name": "project-qualification",
                "questions": [],
                "status": "NOT_STARTED",
            },
            {"name": "risk", "questions": [], "status": "NOT_STARTED"},
            {
                "name": "skills-and-resources",
                "questions": [],
                "status": "NOT_STARTED",
            },
            {
                "name": "value-to-the-community",
                "questions": [],
                "status": "NOT_STARTED",
            },
            {
                "name": "upload-business-plan",
                "questions": [],
                "status": "NOT_STARTED",
            },
        ],
    }
)
