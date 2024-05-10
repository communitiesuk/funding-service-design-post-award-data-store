"""
Defines the table configurations for the Pathfinder round 1 template. These are used to extract, process, and validate
the data.
"""

from datetime import datetime

import pandera as pa

from core.validation.pathfinders.schema_validation import checks


class PFEnums:
    RAGS = ["Green", "Amber/Green", "Amber", "Amber/Red", "Red"]
    INTERVENTION_THEMES = [
        "Employment & Education",
        "Enhancing subregional and regional connectivity",
        "Improving the quality of life of residents",
        "Strengthening the visitor and local service economy",
        "Unlocking and enabling industrial, commercial, and residential development",
        "Unlocking and enabling industrial and commercial development",
    ]
    RISK_CATEGORIES = [
        "Arm’s length body risks",
        "Commercial or procurement risks",
        "Delivery Partner",
        "Financial flexibility",
        "Financial risks",
        "Governance risks",
        "Legal, regulatory or compliance risks",
        "Local government risks",
        "Operational process or control risks",
        "People risks",
        "Planning Permission / other consents",
        "Political sensitivity",
        "Procurement / contracting",
        "Programme or project delivery risks",
        "Reputational Risk",
        "Resilience risks",
        "Resource & Expertise",
        "Security risks",
        "Slippage",
        "Strategy risks",
        "Subsidy Control",
        "System or IT infrastructure risks",
        "Other",
    ]
    RISK_SCORES = ["1 - Very Low", "2 - Low", "3 - Medium", "4 - High", "5 - Very High"]
    ACTUAL_FORECAST = ["Actual", "Forecast", "Cancelled"]
    SPEND_TYPE = [
        "How much of your forecast is contractually committed?",
        "How much of your forecast is not contractually committed?",
        "Freedom and flexibilities spend",
        "Total DLUHC spend (inc. F&F)",
        "Secured match funding spend",
        "Unsecured match funding",
        "Total match",
    ]
    REPORTING_PERIOD = [
        "Q4 2023/24: Jan 2024 - Mar 2024",
        "Q1 2024/25: Apr 2024 - Jun 2024",
        "Q2 2024/25: Jul 2024 - Sep 2024",
        "Q3 2024/25: Oct 2024 - Dec 2024",
        "Q4 2024/25: Jan 2025 - Mar 2025",
        "Q1 2025/26: Apr 2025 - Jun 2025",
        "Q2 2025/26: Jul 2025 - Sep 2025",
        "Q3 2025/26: Oct 2025 - Dec 2025",
        "Q4 2025/26: Jan 2026 - Mar 2026",
    ]


PF_TABLE_CONFIG = {
    "Reporting period": {
        "extract": {
            "id_tag": "PF-USER_CURRENT-REPORTING-PERIOD",
            "worksheet_name": "Start",
        },
        "process": {},
        "validate": {
            "columns": {
                "Reporting period": pa.Column(str, checks.is_in_check(PFEnums.REPORTING_PERIOD)),
            }
        },
    },
    "Financial completion date": {
        "extract": {
            "id_tag": "PF-USER_FINANCIAL-COMPLETION-DATE",
            "worksheet_name": "Admin",
        },
        "process": {
            "ignored_non_header_rows": [0],
        },
        "validate": {"columns": {"Financial completion date": pa.Column(datetime, checks.datetime_check())}},
    },
    "Practical completion date": {
        "extract": {
            "id_tag": "PF-USER_PRACTICAL-COMPLETION-DATE",
            "worksheet_name": "Admin",
        },
        "process": {
            "ignored_non_header_rows": [0],
        },
        "validate": {"columns": {"Practical completion date": pa.Column(datetime, checks.datetime_check())}},
    },
    "Organisation name": {
        "extract": {
            "id_tag": "PF-USER_ORGANISATION-NAME",
            "worksheet_name": "Admin",
        },
        "process": {},
        "validate": {"columns": {"Organisation name": pa.Column(str)}},
    },
    "Contact name": {
        "extract": {
            "id_tag": "PF-USER_CONTACT-NAME",
            "worksheet_name": "Admin",
        },
        "process": {},
        "validate": {"columns": {"Contact name": pa.Column(str)}},
    },
    "Contact email": {
        "extract": {
            "id_tag": "PF-USER_CONTACT-EMAIL",
            "worksheet_name": "Admin",
        },
        "process": {},
        "validate": {"columns": {"Contact email": pa.Column(str, checks.email_regex_check())}},
    },
    "Contact telephone": {
        "extract": {
            "id_tag": "PF-USER_CONTACT-TELEPHONE",
            "worksheet_name": "Admin",
        },
        "process": {
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "Contact telephone": pa.Column(str, checks.phone_regex_check(), nullable=True),
            },
        },
    },
    "Portfolio progress": {
        "extract": {
            "id_tag": "PF-USER_PORTFOLIO-PROGRESS",
            "worksheet_name": "Progress",
        },
        "process": {
            "ignored_non_header_rows": [0],
            "merged_header_rows": [0],
        },
        "validate": {
            "columns": {
                "Portfolio progress": pa.Column(str),
            },
        },
    },
    "Project progress": {
        "extract": {
            "id_tag": "PF-USER_PROJECT-PROGRESS",
            "worksheet_name": "Progress",
        },
        "process": {
            "ignored_non_header_rows": [0],
            "drop_empty_rows": True,
            "dropdown_placeholder": "Please select an option",
        },
        "validate": {
            "columns": {
                "Project name": pa.Column(str, unique=True, report_duplicates="exclude_first"),
                "Spend RAG rating": pa.Column(str, checks.is_in_check(PFEnums.RAGS)),
                "Delivery RAG rating": pa.Column(str, checks.is_in_check(PFEnums.RAGS)),
                "Why have you given these ratings? Enter an explanation (100 words max)": pa.Column(
                    str, checks.max_word_count_check(100)
                ),
            },
        },
    },
    "Big issues across portfolio": {
        "extract": {
            "id_tag": "PF-USER_BIG-ISSUES-ACROSS-PORTFOLIO",
            "worksheet_name": "Progress",
        },
        "process": {
            "merged_header_rows": [0],
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "Big issues across portfolio": pa.Column(str),
            },
        },
    },
    "Upcoming significant milestones": {
        "extract": {
            "id_tag": "PF-USER_UPCOMING-SIGNIFICANT-MILESTONES",
            "worksheet_name": "Progress",
        },
        "process": {
            "merged_header_rows": [0],
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "Upcoming significant milestones": pa.Column(str),
            },
        },
    },
    "Project location": {
        "extract": {
            "id_tag": "PF-USER_PROJECT-LOCATION",
            "worksheet_name": "Project location",
        },
        "process": {
            "ignored_non_header_rows": [0],
            "drop_empty_rows": True,
        },
        "validate": {
            "columns": {
                "Project name": pa.Column(str, unique=True, report_duplicates="exclude_first"),
                "Project full postcode/postcodes (for example, AB1D 2EF)": pa.Column(str, checks.postcode_list_check()),
            },
        },
    },
    "Outputs": {
        "extract": {
            "id_tag": "PF-USER_STANDARD-OUTPUTS",
            "worksheet_name": "Outputs",
        },
        "process": {
            "num_header_rows": 3,
            "merged_header_rows": [0],
            "col_names_to_drop": [
                "Financial year 2023 to 2024, Total",
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
            ],
            "drop_empty_rows": True,
            "dropdown_placeholder": "Please select an option",
        },
        "validate": {
            "columns": {
                "Intervention theme": pa.Column(str),
                "Output": pa.Column(str),
                "Unit of measurement": pa.Column(str),
                "Financial year 2023 to 2024, (Jan to Mar), Actual": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2024 to 2025, (Apr to Jun), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2024 to 2025, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2024 to 2025, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2024 to 2025, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2025 to 2026, (Apr to Jun), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2025 to 2026, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2025 to 2026, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2025 to 2026, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "April 2026 and after, Total": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
            },
            "unique": ["Intervention theme", "Output", "Unit of measurement"],
            "report_duplicates": "exclude_first",
        },
    },
    "Bespoke outputs": {
        "extract": {
            "id_tag": "PF-USER_BESPOKE-OUTPUTS",
            "worksheet_name": "Outputs",
        },
        "process": {
            "num_header_rows": 3,
            "merged_header_rows": [0],
            "col_names_to_drop": [
                "Financial year 2023 to 2024, Total",
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
            ],
            "drop_empty_rows": True,
            "dropdown_placeholder": "Please select an option",
        },
        "validate": {
            "columns": {
                "Intervention theme": pa.Column(str),
                "Output": pa.Column(str),
                "Unit of measurement": pa.Column(str),
                "Financial year 2023 to 2024, (Jan to Mar), Actual": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2024 to 2025, (Apr to Jun), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2024 to 2025, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2024 to 2025, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2024 to 2025, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2025 to 2026, (Apr to Jun), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2025 to 2026, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2025 to 2026, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2025 to 2026, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "April 2026 and after, Total": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
            },
            "unique": ["Intervention theme", "Output", "Unit of measurement"],
            "report_duplicates": "exclude_first",
        },
    },
    "Outcomes": {
        "extract": {
            "id_tag": "PF-USER_STANDARD-OUTCOMES",
            "worksheet_name": "Outcomes",
        },
        "process": {
            "num_header_rows": 3,
            "merged_header_rows": [0],
            "col_names_to_drop": [
                "Financial year 2023 to 2024, Total",
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
            ],
            "drop_empty_rows": True,
            "dropdown_placeholder": "Please select an option",
        },
        "validate": {
            "columns": {
                "Intervention theme": pa.Column(str),
                "Outcome": pa.Column(str),
                "Unit of measurement": pa.Column(str),
                "Financial year 2023 to 2024, (Jan to Mar), Actual": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2024 to 2025, (Apr to Jun), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2024 to 2025, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2024 to 2025, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2024 to 2025, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2025 to 2026, (Apr to Jun), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2025 to 2026, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2025 to 2026, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2025 to 2026, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "April 2026 and after, Total": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
            },
            "unique": ["Intervention theme", "Outcome", "Unit of measurement"],
            "report_duplicates": "exclude_first",
        },
    },
    "Bespoke outcomes": {
        "extract": {
            "id_tag": "PF-USER_BESPOKE-OUTCOMES",
            "worksheet_name": "Outcomes",
        },
        "process": {
            "num_header_rows": 3,
            "merged_header_rows": [0],
            "col_names_to_drop": [
                "Financial year 2023 to 2024, Total",
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
            ],
            "drop_empty_rows": True,
            "dropdown_placeholder": "Please select an option",
        },
        "validate": {
            "columns": {
                "Intervention theme": pa.Column(str),
                "Outcome": pa.Column(str),
                "Unit of measurement": pa.Column(str),
                "Financial year 2023 to 2024, (Jan to Mar), Actual": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2024 to 2025, (Apr to Jun), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2024 to 2025, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2024 to 2025, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2024 to 2025, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2025 to 2026, (Apr to Jun), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2025 to 2026, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2025 to 2026, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "Financial year 2025 to 2026, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
                "April 2026 and after, Total": pa.Column(
                    float,
                    checks=[checks.float_check()],
                ),
            },
            "unique": ["Intervention theme", "Outcome", "Unit of measurement"],
            "report_duplicates": "exclude_first",
        },
    },
    "Credible plan": {
        "extract": {
            "id_tag": "PF-USER_CREDIBLE-PLAN",
            "worksheet_name": "Finances",
        },
        "process": {
            "ignored_non_header_rows": [0, 1, 2],
        },
        "validate": {
            "columns": {
                "Credible plan": pa.Column(str),
            },
        },
    },
    "Total underspend": {
        "extract": {
            "id_tag": "PF-USER_TOTAL-UNDERSPEND",
            "worksheet_name": "Finances",
        },
        "process": {
            "ignored_non_header_rows": [0, 1, 2],
        },
        "validate": {
            "columns": {
                "Total underspend": pa.Column(
                    float,
                    checks=[
                        checks.float_check(),
                        checks.greater_than_or_equal_to_check(0),
                    ],
                    nullable=True,
                ),
            },
        },
    },
    "Proposed underspend use": {
        "extract": {
            "id_tag": "PF-USER_PROPOSED-UNDERSPEND-USE",
            "worksheet_name": "Finances",
        },
        "process": {
            "ignored_non_header_rows": [0, 1, 2],
        },
        "validate": {
            "columns": {
                "Proposed underspend use": pa.Column(
                    float,
                    checks=[
                        checks.float_check(),
                        checks.greater_than_or_equal_to_check(0),
                    ],
                    nullable=True,
                ),
            },
        },
    },
    "Credible plan summary": {
        "extract": {
            "id_tag": "PF-USER_CREDIBLE-PLAN-SUMMARY",
            "worksheet_name": "Finances",
        },
        "process": {
            "ignored_non_header_rows": [0, 1],
            "merged_header_rows": [0],
        },
        "validate": {
            "columns": {
                "Credible plan summary": pa.Column(str, nullable=True),
            },
        },
    },
    "Current underspend": {
        "extract": {
            "id_tag": "PF-USER_CURRENT-UNDERSPEND",
            "worksheet_name": "Finances",
        },
        "process": {
            "ignored_non_header_rows": [0, 1, 2],
        },
        "validate": {
            "columns": {
                "Current underspend": pa.Column(
                    float,
                    # Value is not required in Q4
                    nullable=True,
                    checks=[
                        checks.float_check(),
                        checks.greater_than_or_equal_to_check(0),
                    ],
                ),
            },
        },
    },
    "Forecast and actual spend": {
        "extract": {
            "id_tag": "PF-USER_FORECAST-AND-ACTUAL-SPEND",
            "worksheet_name": "Finances",
        },
        "process": {
            "num_header_rows": 3,
            "merged_header_rows": [0],
            "ignored_non_header_rows": [3, 6, 7],
            "col_names_to_drop": [
                "Financial year 2023 to 2024, Total",
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
            ],
        },
        "validate": {
            "columns": {
                "Type of spend": pa.Column(str, checks.is_in_check(PFEnums.SPEND_TYPE)),
                "Financial year 2023 to 2024, (Jan to Mar), Actual": pa.Column(
                    float,
                    checks=[
                        checks.float_check(),
                        checks.greater_than_or_equal_to_check(0),
                    ],
                ),
                "Financial year 2024 to 2025, (Apr to Jun), Forecast": pa.Column(
                    float,
                    checks=[
                        checks.float_check(),
                        checks.greater_than_or_equal_to_check(0),
                    ],
                ),
                "Financial year 2024 to 2025, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[
                        checks.float_check(),
                        checks.greater_than_or_equal_to_check(0),
                    ],
                ),
                "Financial year 2024 to 2025, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[
                        checks.float_check(),
                        checks.greater_than_or_equal_to_check(0),
                    ],
                ),
                "Financial year 2024 to 2025, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[
                        checks.float_check(),
                        checks.greater_than_or_equal_to_check(0),
                    ],
                ),
                "Financial year 2025 to 2026, (Apr to Jun), Forecast": pa.Column(
                    float,
                    checks=[
                        checks.float_check(),
                        checks.greater_than_or_equal_to_check(0),
                    ],
                ),
                "Financial year 2025 to 2026, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[
                        checks.float_check(),
                        checks.greater_than_or_equal_to_check(0),
                    ],
                ),
                "Financial year 2025 to 2026, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[
                        checks.float_check(),
                        checks.greater_than_or_equal_to_check(0),
                    ],
                ),
                "Financial year 2025 to 2026, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[
                        checks.float_check(),
                        checks.greater_than_or_equal_to_check(0),
                    ],
                ),
            },
        },
    },
    "Uncommitted funding plan": {
        "extract": {
            "id_tag": "PF-USER_UNCOMMITTED-FUNDING-PLAN",
            "worksheet_name": "Finances",
        },
        "process": {
            "merged_header_rows": [0],
            "ignored_non_header_rows": [0, 1],
        },
        "validate": {
            "columns": {
                "Uncommitted funding plan": pa.Column(str),
            },
        },
    },
    "Summary of changes below change request threshold": {
        "extract": {
            "id_tag": "PF-USER_SUMMARY-OF-CHANGES-BELOW-CHANGE-REQUEST-THRESHOLD",
            "worksheet_name": "Finances",
        },
        "process": {
            "merged_header_rows": [0],
            "ignored_non_header_rows": [0, 1],
        },
        "validate": {
            "columns": {
                "Summary of changes below change request threshold": pa.Column(str),
            },
        },
    },
    "Project finance changes": {
        "extract": {
            "id_tag": "PF-USER_PROJECT-FINANCE-CHANGES",
            "worksheet_name": "Finances",
        },
        "process": {
            "merged_header_rows": [0],
            "drop_empty_rows": True,
            "dropdown_placeholder": "Please select an option",
        },
        "validate": {
            "columns": {
                "Change number": pa.Column(int, checks.int_check(), unique=True, report_duplicates="exclude_first"),
                "Project funding moved from": pa.Column(str),
                "Intervention theme moved from": pa.Column(str),
                "Project funding moved to": pa.Column(str),
                "Intervention theme moved to": pa.Column(str),
                "Amount moved": pa.Column(
                    float,
                    checks=[
                        checks.float_check(),
                        checks.greater_than_check(0),
                        checks.less_than_check(5_000_000),
                    ],
                ),
                "What changes have you made / or are planning to make? (100 words max)": pa.Column(
                    str, checks.max_word_count_check(100)
                ),
                "Reason for change (100 words max)": pa.Column(str, checks.max_word_count_check(100)),
                "Actual, forecast or cancelled": pa.Column(str, checks.is_in_check(PFEnums.ACTUAL_FORECAST)),
                "Reporting period change takes place": pa.Column(str, checks.is_in_check(PFEnums.REPORTING_PERIOD)),
            },
        },
    },
    "Risks": {
        "extract": {
            "id_tag": "PF-USER_RISKS",
            "worksheet_name": "Risks",
        },
        "process": {
            "ignored_non_header_rows": [0],
            "col_names_to_drop": [
                "Pre-mitigated total risk score",
                "Post-mitigated total risk score",
            ],
            "drop_empty_rows": True,
            "dropdown_placeholder": "Please select an option",
        },
        "validate": {
            "columns": {
                "Risk name": pa.Column(str, unique=True, report_duplicates="exclude_first"),
                "Category": pa.Column(str, checks.is_in_check(PFEnums.RISK_CATEGORIES)),
                "Description": pa.Column(str, checks.max_word_count_check(100)),
                "Pre-mitigated likelihood score": pa.Column(str, checks.is_in_check(PFEnums.RISK_SCORES)),
                "Pre-mitigated impact score": pa.Column(str, checks.is_in_check(PFEnums.RISK_SCORES)),
                "Mitigations": pa.Column(str, checks.max_word_count_check(100)),
                "Post-mitigated likelihood score": pa.Column(str, checks.is_in_check(PFEnums.RISK_SCORES)),
                "Post-mitigated impact score": pa.Column(str, checks.is_in_check(PFEnums.RISK_SCORES)),
            },
            "checks": checks.exactly_x_rows_check(5),
        },
    },
    "Signatory name": {
        "extract": {
            "id_tag": "PF-USER_SIGNATORY-NAME",
            "worksheet_name": "Sign off",
        },
        "process": {},
        "validate": {
            "columns": {
                "Signatory name": pa.Column(str),
            },
        },
    },
    "Signatory role": {
        "extract": {
            "id_tag": "PF-USER_SIGNATORY-ROLE",
            "worksheet_name": "Sign off",
        },
        "process": {},
        "validate": {
            "columns": {
                "Signatory role": pa.Column(str),
            },
        },
    },
    "Signature date": {
        "extract": {
            "id_tag": "PF-USER_SIGNATURE-DATE",
            "worksheet_name": "Sign off",
        },
        "process": {
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "Signature date": pa.Column(
                    datetime,
                    checks=[
                        checks.datetime_check(),
                        checks.not_in_future_check(),
                    ],
                ),
            },
        },
    },
    "Project details control": {
        "extract": {
            "id_tag": "PF-CONTROL_PROJECT-DETAILS",
            "worksheet_name": "Project Details",
        },
        "process": {},
        "validate": {
            "columns": {
                "Local Authority": pa.Column(str),
                "Reference": pa.Column(str),
                "Project name": pa.Column(str),
                "Status": pa.Column(str),
                "Full name": pa.Column(str),
            },
        },
    },
    "Outputs control": {
        "extract": {
            "id_tag": "PF-CONTROL_STANDARD-OUTPUTS",
            "worksheet_name": "Dropdown Values",
        },
        "process": {},
        "validate": {
            "columns": {
                "Standard output": pa.Column(str),
                "UoM": pa.Column(str, nullable=True),
                "Intervention theme": pa.Column(str, nullable=True),
            }
        },
    },
    "Outcomes control": {
        "extract": {
            "id_tag": "PF-CONTROL_STANDARD-OUTCOMES",
            "worksheet_name": "Dropdown Values",
        },
        "process": {},
        "validate": {
            "columns": {
                "Standard outcome": pa.Column(str),
                "UoM": pa.Column(str, nullable=True),
                "Intervention theme": pa.Column(str, nullable=True),
            }
        },
    },
    "Bespoke outputs control": {
        "extract": {
            "id_tag": "PF-CONTROL_BESPOKE-OUTPUTS",
            "worksheet_name": "Bespoke Outputs",
        },
        "process": {},
        "validate": {
            "columns": {
                "Local Authority": pa.Column(str),
                "Output": pa.Column(str),
                "UoM": pa.Column(str, nullable=True),
                "Intervention theme": pa.Column(str),
            },
        },
    },
    "Bespoke outcomes control": {
        "extract": {
            "id_tag": "PF-CONTROL_BESPOKE-OUTCOMES",
            "worksheet_name": "Bespoke Outcomes",
        },
        "process": {},
        "validate": {
            "columns": {
                "Local Authority": pa.Column(str),
                "Outcome": pa.Column(str),
                "UoM": pa.Column(str, nullable=True),
                "Intervention theme": pa.Column(str),
            },
        },
    },
    "Intervention themes control": {
        "extract": {
            "id_tag": "PF-CONTROL_INTERVENTION-THEME",
            "worksheet_name": "Dropdown Values",
        },
        "process": {},
        "validate": {
            "columns": {
                "Intervention theme": pa.Column(str),
            }
        },
    },
}
