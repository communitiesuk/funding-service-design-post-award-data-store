"""
Defines the table configurations for the Pathfinder round 1 template. These are used to extract, process, and validate
the data.
"""

from datetime import datetime

import pandera as pa


class PFRegex:
    BASIC_EMAIL = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"  # will catch most common errors
    BASIC_TELEPHONE = (
        r"^(((\+44\s?\d{4}|\(?0\d{4}\)?)\s?\d{3}\s?\d{3})|((\+44\s?\d{3}|\(?0\d{3}\)?)\s?\d{3}"
        r"\s?\d{4})|((\+44\s?\d{2}|\(?0\d{2}\)?)\s?\d{4}\s?\d{4}))(\s?\#(\d{4}|\d{3}))?$"
    )


class PFEnums:
    RAGS = ["Green", "Amber/Green", "Amber", "Amber/Red", "Red"]
    INTERVENTION_THEMES = [
        "Employment & Education",
        "Enhancing sub-regional and regional connectivity",
        "Improving the quality of life of residents",
        "Strengthening the visitor and local service economy",
        "Unlocking and enabling industrial, commercial, and residential development",
        "Unlocking and enabling industrial and commercial development",
    ]
    RISK_CATEGORIES = [
        "Strategy risks",
        "Programme or project delivery risks",
        "People risks",
        "Operational process or control risks",
        "Resilience risks",
        "Governance risks",
        "System or IT infrastructure risks",
        "Security risks",
        "Financial risks",
        "Commercial or procurement risks",
        "Lega, regulatory or compliance risks",
        "Arm’s length body risks",
        "Local government risks",
        "Political sensitivity",
        "Reputational Risk",
        "Resource & Expertise",
        "Slippage",
        "Planning Permission / other consents",
        "Procurement / contracting",
        "Delivery Partner",
        "Financial flexibility",
        "Subsidy Control",
        "Other",
    ]
    RISK_SCORES = ["1 - Very Low", "2 - Low", "3 - Medium", "4 - High", "5 - Very High"]
    ACTUAL_FORECAST = ["Actual", "Forecast"]
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
        "Q1 2024/25: Apr 2024 - Jun 2024",
        "Q2 2024/25: Jul 2024 - Sep 2024",
        "Q3 2024/25: Oct 2024 - Dec 2024",
        "Q4 2024/25: Jan 2025 - Mar 2025",
        "Q1 2025/26: Apr 2025 - Jun 2025",
        "Q2 2025/26: Jul 2025 - Sep 2025",
        "Q3 2025/26: Oct 2025 - Dec 2025",
        "Q4 2025/26: Jan 2026 - Mar 2026",
    ]


class PFErrors:
    IS_FLOAT = (
        "You entered text instead of a number. Remove any units of measurement and only use numbers, for example, 9."
    )
    IS_DATETIME = "You entered text instead of a date."
    ISIN = (
        "You’ve entered your own content, instead of selecting from the dropdown list provided. Select an "
        "option from the dropdown list."
    )
    LTE_X_WORDS = "Please enter a maximum of {x} words."
    POSITIVE = "Amount must be positive."
    EMAIL = "Please enter a valid email address."
    AMOUNT_MOVED_GT_ZERO = "Amount moved must be greater than £0."
    AMOUNT_MOVED_LT_5M = "Amount moved must be less than £5m."
    FUTURE_DATE = "You must not enter a date in the future."


PF_TABLE_CONFIG = {
    "Financial completion date": {
        "extract": {
            "id_tag": "PF-USER_FINANCIAL-COMPLETION-DATE",
            "worksheet_name": "Admin",
        },
        "process": {
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "Financial completion date": pa.Column(datetime, pa.Check.is_datetime(error=PFErrors.IS_DATETIME))
            }
        },
    },
    "Practical completion date": {
        "extract": {
            "id_tag": "PF-USER_PRACTICAL-COMPLETION-DATE",
            "worksheet_name": "Admin",
        },
        "process": {
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "Practical completion date": pa.Column(datetime, pa.Check.is_datetime(error=PFErrors.IS_DATETIME))
            }
        },
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
        "validate": {
            "columns": {
                "Contact email": pa.Column(str, pa.Check.str_matches(PFRegex.BASIC_EMAIL, error=PFErrors.EMAIL))
            }
        },
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
                "Contact telephone": pa.Column(str, nullable=True),
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
                "Spend RAG rating": pa.Column(str, pa.Check.isin(PFEnums.RAGS, error=PFErrors.ISIN)),
                "Delivery RAG rating": pa.Column(str, pa.Check.isin(PFEnums.RAGS, error=PFErrors.ISIN)),
                "Why have you given these ratings? Enter an explanation (100 words max)": pa.Column(
                    str, pa.Check.max_word_count(100, error=PFErrors.LTE_X_WORDS.format(x=100))
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
            "worksheet_name": "Project Location",
        },
        "process": {
            "ignored_non_header_rows": [0],
            "drop_empty_rows": True,
        },
        "validate": {
            "columns": {
                "Project name": pa.Column(str, unique=True, report_duplicates="exclude_first"),
                "Project full postcode/postcodes (for example, AB1D 2EF)": pa.Column(str),
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
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
            ],
            "drop_empty_rows": True,
            "dropdown_placeholder": "Please select an option",
        },
        "validate": {
            "columns": {
                "Intervention theme": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Output": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Unit of measurement": pa.Column(str),  # TODO: isin - the dropdown
                # values are still being finalised
                "Financial year 2024 to 2025, (Apr to Jun), Actual": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2024 to 2025, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2024 to 2025, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2024 to 2025, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2025 to 2026, (Apr to Jun), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2025 to 2026, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2025 to 2026, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2025 to 2026, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "April 2026 and after, Total": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
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
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
            ],
            "drop_empty_rows": True,
            "dropdown_placeholder": "Please select an option",
        },
        "validate": {
            "columns": {
                "Intervention theme": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Output": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Unit of measurement": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Financial year 2024 to 2025, (Apr to Jun), Actual": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2024 to 2025, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2024 to 2025, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2024 to 2025, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2025 to 2026, (Apr to Jun), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2025 to 2026, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2025 to 2026, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2025 to 2026, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "April 2026 and after, Total": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
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
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
            ],
            "drop_empty_rows": True,
            "dropdown_placeholder": "Please select an option",
        },
        "validate": {
            "columns": {
                "Intervention theme": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Outcome": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Unit of measurement": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Financial year 2024 to 2025, (Apr to Jun), Actual": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2024 to 2025, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2024 to 2025, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2024 to 2025, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2025 to 2026, (Apr to Jun), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2025 to 2026, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2025 to 2026, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2025 to 2026, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "April 2026 and after, Total": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
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
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
            ],
            "drop_empty_rows": True,
            "dropdown_placeholder": "Please select an option",
        },
        "validate": {
            "columns": {
                "Intervention theme": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Outcome": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Unit of measurement": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Financial year 2024 to 2025, (Apr to Jun), Actual": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2024 to 2025, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2024 to 2025, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2024 to 2025, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2025 to 2026, (Apr to Jun), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2025 to 2026, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2025 to 2026, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "Financial year 2025 to 2026, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
                ),
                "April 2026 and after, Total": pa.Column(
                    float,
                    checks=[pa.Check.is_float(error=PFErrors.IS_FLOAT)],
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
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
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
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
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
                "Credible plan summary": pa.Column(str),
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
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
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
            "ignored_non_header_rows": [7],
            "col_names_to_drop": [
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
            ],
        },
        "validate": {
            "columns": {
                "Type of spend": pa.Column(str, pa.Check.isin(PFEnums.SPEND_TYPE, error=PFErrors.ISIN)),
                "Financial year 2024 to 2025, (Apr to Jun), Actual": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2024 to 2025, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2024 to 2025, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2024 to 2025, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2025 to 2026, (Apr to Jun), Forecast": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2025 to 2026, (Jul to Sep), Forecast": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2025 to 2026, (Oct to Dec), Forecast": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2025 to 2026, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "April 2026 and after, Total": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
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
                # TODO: confirm what this is?
                "Change number": pa.Column(
                    int, pa.Check.is_int(error=PFErrors.IS_FLOAT), unique=True, report_duplicates="exclude_first"
                ),
                # TODO: allowed projects in the dropdown are unknown at this stage, if this needs validation then it
                #   should be done during fund specific validation
                "Project funding moved from": pa.Column(str),
                # TODO: isin - the dropdown values are still being finalised
                "Intervention theme moved from": pa.Column(str),
                "Project funding moved to": pa.Column(str),
                # TODO: isin - the dropdown values are still being finalised
                "Intervention theme moved to": pa.Column(str),
                "Amount moved": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than(0, error=PFErrors.AMOUNT_MOVED_GT_ZERO),
                        pa.Check.less_than(5000000, error=PFErrors.AMOUNT_MOVED_LT_5M),
                    ],
                ),
                "What changes have you made / or are planning to make? (100 words max)": pa.Column(
                    str, pa.Check.max_word_count(100, error=PFErrors.LTE_X_WORDS.format(x=100))
                ),
                "Reason for change (100 words max)": pa.Column(
                    str, pa.Check.max_word_count(100, error=PFErrors.LTE_X_WORDS.format(x=100))
                ),
                "Actual, forecast or cancelled": pa.Column(
                    str, pa.Check.isin(PFEnums.ACTUAL_FORECAST, error=PFErrors.ISIN)
                ),
                "Reporting period change takes place": pa.Column(
                    str, pa.Check.isin(PFEnums.REPORTING_PERIOD, error=PFErrors.ISIN)
                ),
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
                "Category": pa.Column(str, pa.Check.isin(PFEnums.RISK_CATEGORIES, error=PFErrors.ISIN)),
                "Description": pa.Column(str, pa.Check.max_word_count(100, error=PFErrors.LTE_X_WORDS.format(x=100))),
                "Pre-mitigated likelihood score": pa.Column(
                    str, pa.Check.isin(PFEnums.RISK_SCORES, error=PFErrors.ISIN)
                ),
                "Pre-mitigated impact score": pa.Column(str, pa.Check.isin(PFEnums.RISK_SCORES, error=PFErrors.ISIN)),
                "Mitigations": pa.Column(str, pa.Check.max_word_count(100, error=PFErrors.LTE_X_WORDS.format(x=100))),
                "Post-mitigated likelihood score": pa.Column(
                    str, pa.Check.isin(PFEnums.RISK_SCORES, error=PFErrors.ISIN)
                ),
                "Post-mitigated impact score": pa.Column(str, pa.Check.isin(PFEnums.RISK_SCORES, error=PFErrors.ISIN)),
            },
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
                        pa.Check.is_datetime(error=PFErrors.IS_DATETIME),
                        pa.Check.not_in_future(error=PFErrors.FUTURE_DATE),
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
            "id_tag": "PF-CONTROL_STANDARD-OUTPUT-START",
            "worksheet_name": "Dropdown Values",
        },
        "process": {},
        "validate": {"columns": {"Standard outputs": pa.Column(str)}},
    },
    "Outcomes control": {
        "extract": {
            "id_tag": "PF-CONTROL_STANDARD-OUTCOME-START",
            "worksheet_name": "Dropdown Values",
        },
        "process": {},
        "validate": {"columns": {"Standard outcomes": pa.Column(str)}},
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
}
