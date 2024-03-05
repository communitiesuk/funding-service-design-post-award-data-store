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
        "Enhancing sub-regional and regional connectivity",
        "Unlocking and enabling industrial, commercial, and residential development",
        "Unlocking and enabling industrial and commercial development",
        "Strengthening the visitor and local service economy",
        "Improving the quality of life of residents",
        "Employment & Education",
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
    RISK_SCORES = ["1 - very low", "2 - low", "3 - medium", "4 - high", "5 - very high"]
    FORECAST_ACTUAL = ["Forecast", "Actual"]
    SPEND_TYPE = [
        "How much of your forecast is contractually committed?",
        "Freedom and flexibilities spend",
        "Total DLUHC spend (incl F&F)",
        "Secured Match Funding Spend",
        "Unsecured Match Funding",
        "Total Match",
    ]
    REPORTING_PERIOD = [
        "Q1 Apr - Jun 23/24",
        "Q2 Jul - Sep 23/24",
        "Q3 Oct - Dec 23/24",
        "Q4 Jan - Mar 23/24",
        "Q1 Apr - Jun 24/25",
        "Q2 Jul - Sep 24/25",
        "Q3 Oct - Dec 24/25",
        "Q4 Jan - Mar 24/25",
        "Q1 Apr - Jun 25/26",
        "Q2 Jul - Sep 25/26",
        "Q3 Oct - Dec 25/26",
        "Q4 Jan - Mar 25/26",
        "Apr 26 onwards",
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
    "Financial Completion Date": {
        "extract": {
            "id_tag": "PF-TABLE-FINANCIAL-COMPLETION-DATE",
            "worksheet_name": "Admin",
        },
        "process": {
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "Pathfinder Financial Completion Date": pa.Column(
                    datetime, pa.Check.is_datetime(error=PFErrors.IS_DATETIME)
                ),
            }
        },
    },
    "Practical Completion Date": {
        "extract": {
            "id_tag": "PF-TABLE-PRACTICAL-COMPLETION-DATE",
            "worksheet_name": "Admin",
        },
        "process": {
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "Practical Completion Date": pa.Column(datetime, pa.Check.is_datetime(error=PFErrors.IS_DATETIME))
            }
        },
    },
    "Organisation name": {
        "extract": {
            "id_tag": "PF-TABLE-ORGANISATION",
            "worksheet_name": "Admin",
        },
        "process": {},
        "validate": {"columns": {"Organisation name": pa.Column(str)}},
    },
    "Contact name": {
        "extract": {
            "id_tag": "PF-TABLE-CONTACT-NAME",
            "worksheet_name": "Admin",
        },
        "process": {},
        "validate": {"columns": {"Name": pa.Column(str)}},
    },
    "Contact email address": {
        "extract": {
            "id_tag": "PF-TABLE-CONTACT-EMAIL",
            "worksheet_name": "Admin",
        },
        "process": {},
        "validate": {
            "columns": {
                "Email address": pa.Column(str, pa.Check.str_matches(PFRegex.BASIC_EMAIL, error=PFErrors.EMAIL))
            }
        },
    },
    "Contact telephone": {
        "extract": {
            "id_tag": "PF-TABLE-CONTACT-TELEPHONE",
            "worksheet_name": "Admin",
        },
        "process": {},
        "validate": {
            "columns": {
                "Telephone (Optional)": pa.Column(str, nullable=True),
            },
        },
    },
    "Portfolio progress": {
        "extract": {
            "id_tag": "PF-TABLE-PORTFOLIO-PROGRESS",
            "worksheet_name": "Progress",
        },
        "process": {
            "merged_header_rows": [0],
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "How is the delivery of your portfolio progressing?": pa.Column(str),
            },
        },
    },
    "Project progress": {
        "extract": {
            "id_tag": "PF-TABLE-PROJECT-PROGRESS",
            "worksheet_name": "Progress",
        },
        "process": {
            "ignored_non_header_rows": [0],
            "drop_empty_rows": True,
        },
        "validate": {
            "columns": {
                # TODO: project names should be unique but if the constraint is broken, it's a spreadsheet
                #  configuration error rather than a user error because the project names are pre-configured.
                #  Is it best to omit this constraint here (preventing user error messages) and rely on later
                #  validation/db constraints.
                "Project name": pa.Column(str),
                "Spend RAG rating": pa.Column(str, pa.Check.isin(PFEnums.RAGS, error=PFErrors.ISIN)),
                "Delivery RAG rating": pa.Column(str, pa.Check.isin(PFEnums.RAGS, error=PFErrors.ISIN)),
                "Why have you given these ratings?": pa.Column(
                    str, pa.Check.max_word_count(100, error=PFErrors.LTE_X_WORDS.format(x=100))
                ),
            },
        },
    },
    "Portfolio big issues": {
        "extract": {
            "id_tag": "PF-TABLE-PORTFOLIO-BIG-ISSUES",
            "worksheet_name": "Progress",
        },
        "process": {
            "merged_header_rows": [0],
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "What are the big issues across your portfolio?": pa.Column(str),
            },
        },
    },
    "Significant milestones": {
        "extract": {
            "id_tag": "PF-TABLE-SIGNIFICANT-MILESTONES",
            "worksheet_name": "Progress",
        },
        "process": {
            "merged_header_rows": [0],
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "What significant milestones are coming up?": pa.Column(str),
            },
        },
    },
    "Outputs": {
        "extract": {
            "id_tag": "PF-TABLE-OUTPUTS",
            "worksheet_name": "Outputs and outcomes",
        },
        "process": {
            "num_header_rows": 3,
            "merged_header_rows": [0],
            "ignored_non_header_rows": [0],
            "col_names_to_drop": [
                "Financial year 2023 to 2024, Total",
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
            ],
            "drop_empty_rows": True,
        },
        "validate": {
            "columns": {
                "Intervention theme": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Output": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Unit of Measurement": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Financial year 2023 to 2024, (Apr to June), Actual": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2023 to 2024, (July to Sept), Actual": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2023 to 2024, (Oct to Dec), Actual": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2023 to 2024, (Jan to Mar), Actual": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2024 to 2025, (Apr to June), Forecast": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2024 to 2025, (July to Sept), Forecast": pa.Column(
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
                "Financial year 2025 to 2026, (Apr to June), Forecast": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2025 to 2026, (July to Sept), Forecast": pa.Column(
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
            "unique": ["Intervention theme", "Output", "Unit of Measurement"],
            "report_duplicates": "exclude_first",
        },
    },
    "Outcomes": {
        "extract": {
            "id_tag": "PF-TABLE-OUTCOMES",
            "worksheet_name": "Outputs and outcomes",
        },
        "process": {
            "num_header_rows": 3,
            "merged_header_rows": [0],
            "ignored_non_header_rows": [0],
            "col_names_to_drop": [
                "Financial year 2023 to 2024, Total",
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
            ],
            "drop_empty_rows": True,
        },
        "validate": {
            "columns": {
                "Intervention theme": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Outcome": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Unit of Measurement": pa.Column(str),  # TODO: isin - the dropdown values are still being finalised
                "Financial year 2023 to 2024, (Apr to June), Actual": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2023 to 2024, (July to Sept), Actual": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2023 to 2024, (Oct to Dec), Actual": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2023 to 2024, (Jan to Mar), Actual": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2024 to 2025, (Apr to June), Forecast": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2024 to 2025, (July to Sept), Forecast": pa.Column(
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
                "Financial year 2025 to 2026, (Apr to June), Forecast": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2025 to 2026, (July to Sept), Forecast": pa.Column(
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
            "unique": ["Intervention theme", "Outcome", "Unit of Measurement"],
            "report_duplicates": "exclude_first",
        },
    },
    "Risks": {
        "extract": {
            "id_tag": "PF-TABLE-RISKS",
            "worksheet_name": "Risks",
        },
        "process": {
            "ignored_non_header_rows": [0],
            "col_names_to_drop": ["Total risk score"],
            "drop_empty_rows": True,
        },
        "validate": {
            "columns": {
                "Risk name": pa.Column(str, unique=True, report_duplicates="exclude_first"),
                "Category": pa.Column(str, pa.Check.isin(PFEnums.RISK_CATEGORIES, error=PFErrors.ISIN)),
                "Description": pa.Column(str, pa.Check.max_word_count(100, error=PFErrors.LTE_X_WORDS.format(x=100))),
                "Likelihood score": pa.Column(str, pa.Check.isin(PFEnums.RISK_SCORES, error=PFErrors.ISIN)),
                "Impact score": pa.Column(str, pa.Check.isin(PFEnums.RISK_SCORES, error=PFErrors.ISIN)),
                "Mitigations": pa.Column(str, pa.Check.max_word_count(100, error=PFErrors.LTE_X_WORDS.format(x=100))),
                "Risk Owner": pa.Column(str),
            },
            "checks": [pa.Check(lambda df: len(df.index) == 5, error="You must enter 5 risks.")],
        },
    },
    "Underspend": {
        "extract": {
            "id_tag": "PF-TABLE-UNDERSPEND",
            "worksheet_name": "Finances",
        },
        "process": {
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "What's your underspend for this financial year?": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
            },
        },
    },
    "Current underspend": {
        "extract": {
            "id_tag": "PF-TABLE-CURRENT-UNDERSPEND",
            "worksheet_name": "Finances",
        },
        "process": {
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "What's your current underspend for this financial year?": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
            },
        },
    },
    "Underspend requested": {
        "extract": {
            "id_tag": "PF-TABLE-REQUESTED-UNDERSPEND",
            "worksheet_name": "Finances",
        },
        "process": {
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "How much underspend are you asking for with a credible plan?": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
            },
        },
    },
    "Spending plan": {
        "extract": {
            "id_tag": "PF-TABLE-SPENDING-PLAN",
            "worksheet_name": "Finances",
        },
        "process": {
            "merged_header_rows": [0],
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "How do you plan to spend this value in the next financial year?": pa.Column(str),
            },
        },
    },
    "Forecast spend": {
        "extract": {
            "id_tag": "PF-TABLE-FORECAST-SPEND",
            "worksheet_name": "Finances",
        },
        "process": {
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "What is your forecast spend for the next financial year?": pa.Column(
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
            "id_tag": "PF-TABLE-FORECAST-ACTUAL-SPEND",
            "worksheet_name": "Finances",
        },
        "process": {
            "num_header_rows": 4,
            "merged_header_rows": [0],
            "ignored_non_header_rows": [6],
            "col_names_to_drop": [
                "Financial year 2023 to 2024, Total",
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
            ],
        },
        "validate": {
            "columns": {
                "Type of spend": pa.Column(str, pa.Check.isin(PFEnums.SPEND_TYPE, error=PFErrors.ISIN)),
                "Financial year 2023 to 2024, (Apr to June), Actual": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2023 to 2024, (July to Sept), Actual": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2023 to 2024, (Oct to Dec), Actual": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2023 to 2024, (Jan to Mar), Forecast": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2024 to 2025, (Apr to June), Forecast": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2024 to 2025, (July to Sept), Forecast": pa.Column(
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
                "Financial year 2025 to 2026, (Apr to June), Forecast": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than_or_equal_to(0, error=PFErrors.POSITIVE),
                    ],
                ),
                "Financial year 2025 to 2026, (July to Sept), Forecast": pa.Column(
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
            "id_tag": "PF-TABLE-UNCOMMITTED-FUNDING-PLAN",
            "worksheet_name": "Finances",
        },
        "process": {
            "merged_header_rows": [0],
        },
        "validate": {
            "columns": {
                "What is your plan for using any uncommitted funding?": pa.Column(str),
            },
        },
    },
    "Change request threshold": {
        "extract": {
            "id_tag": "PF-TABLE-CHANGE-REQUEST-THRESHOLD",
            "worksheet_name": "Finances",
        },
        "process": {
            "merged_header_rows": [0],
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                (
                    "What changes have you made, or plan to make, that are below the change request threshold?"
                ): pa.Column(str),
            },
        },
    },
    "Project finance changes": {
        "extract": {
            "id_tag": "PF-TABLE-PROJECT-FINANCE-CHANGES",
            "worksheet_name": "Finances",
        },
        "process": {
            "merged_header_rows": [0],
            "drop_empty_rows": True,
        },
        "validate": {
            "columns": {
                # TODO: confirm what this is?
                "Change Number": pa.Column(
                    int, pa.Check.is_int(error=PFErrors.IS_FLOAT), unique=True, report_duplicates="exclude_first"
                ),
                # TODO: allowed projects in the dropdown are unknown at this stage, if this needs validation then it
                #   should be done during fund specific validation
                "Project Funding Moved From": pa.Column(str),
                # TODO: isin - the dropdown values are still being finalised
                "Intervention Theme Moved From": pa.Column(str),
                "Project Funding Moved To": pa.Column(str),
                # TODO: isin - the dropdown values are still being finalised
                "Intervention Theme Moved To": pa.Column(str),
                "Amount Moved": pa.Column(
                    float,
                    checks=[
                        pa.Check.is_float(error=PFErrors.IS_FLOAT),
                        pa.Check.greater_than(0, error=PFErrors.AMOUNT_MOVED_GT_ZERO),
                        pa.Check.less_than(5000000, error=PFErrors.AMOUNT_MOVED_LT_5M),
                    ],
                ),
                "Changes Made (100 words Max)": pa.Column(
                    str, pa.Check.max_word_count(100, error=PFErrors.LTE_X_WORDS.format(x=100))
                ),
                "Reason for Change (100 words Max)": pa.Column(
                    str, pa.Check.max_word_count(100, error=PFErrors.LTE_X_WORDS.format(x=100))
                ),
                "Forecast or Actual Change": pa.Column(
                    str, pa.Check.isin(PFEnums.FORECAST_ACTUAL, error=PFErrors.ISIN)
                ),
                "Reporting Period Change Took Place": pa.Column(
                    str, pa.Check.isin(PFEnums.REPORTING_PERIOD, error=PFErrors.ISIN)
                ),
            },
        },
    },
    "Sign off name": {
        "extract": {
            "id_tag": "PF-TABLE-SIGN-OFF-NAME",
            "worksheet_name": "Sign off",
        },
        "process": {},
        "validate": {
            "columns": {
                "Name": pa.Column(str),
            },
        },
    },
    "Sign off role": {
        "extract": {
            "id_tag": "PF-TABLE-SIGN-OFF-ROLE",
            "worksheet_name": "Sign off",
        },
        "process": {},
        "validate": {
            "columns": {
                "Role": pa.Column(str),
            },
        },
    },
    "Sign off date": {
        "extract": {
            "id_tag": "PF-TABLE-SIGN-OFF-DATE",
            "worksheet_name": "Sign off",
        },
        "process": {
            "ignored_non_header_rows": [0],
        },
        "validate": {
            "columns": {
                "Date": pa.Column(
                    datetime,
                    checks=[
                        pa.Check.is_datetime(error=PFErrors.IS_DATETIME),
                        pa.Check.not_in_future(error=PFErrors.FUTURE_DATE),
                    ],
                ),
            },
        },
    },
}
