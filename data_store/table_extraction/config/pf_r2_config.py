"""
Defines the table configurations for the Pathfinders round 2 template. These are used to extract, process, and validate
the data.
"""

from data_store.validation.pathfinders.r2_consts import PFEnums
from data_store.validation.pathfinders.schema_validation import checks
from data_store.validation.pathfinders.schema_validation.columns import (
    datetime_column,
    float_column,
    int_column,
    string_column,
)

PF_TABLE_CONFIG: dict[str, dict[str, dict]] = {
    "Reporting period": {
        "extract": {
            "id_tag": "PF-USER_CURRENT-REPORTING-PERIOD",
            "worksheet_name": "Start",
        },
        "process": {},
        "validate": {"columns": {"Reporting period": string_column(checks.is_in(PFEnums.REPORTING_PERIOD))}},
    },
    "Financial completion date": {
        "extract": {
            "id_tag": "PF-USER_FINANCIAL-COMPLETION-DATE",
            "worksheet_name": "Admin",
        },
        "process": {
            "ignored_non_header_rows": [0],
        },
        "validate": {"columns": {"Financial completion date": datetime_column()}},
    },
    "Activity end date": {
        "extract": {
            "id_tag": "PF-USER_ACTIVITY-END-DATE",
            "worksheet_name": "Admin",
        },
        "process": {
            "ignored_non_header_rows": [0],
        },
        "validate": {"columns": {"Activity end date": datetime_column()}},
    },
    "Practical completion date": {
        "extract": {
            "id_tag": "PF-USER_PRACTICAL-COMPLETION-DATE",
            "worksheet_name": "Admin",
        },
        "process": {
            "ignored_non_header_rows": [0],
        },
        "validate": {"columns": {"Practical completion date": datetime_column()}},
    },
    "Organisation name": {
        "extract": {
            "id_tag": "PF-USER_ORGANISATION-NAME",
            "worksheet_name": "Admin",
        },
        "process": {},
        "validate": {"columns": {"Organisation name": string_column()}},
    },
    "Contact name": {
        "extract": {
            "id_tag": "PF-USER_CONTACT-NAME",
            "worksheet_name": "Admin",
        },
        "process": {},
        "validate": {"columns": {"Contact name": string_column()}},
    },
    "Contact email": {
        "extract": {
            "id_tag": "PF-USER_CONTACT-EMAIL",
            "worksheet_name": "Admin",
        },
        "process": {},
        "validate": {"columns": {"Contact email": string_column(checks.email_regex())}},
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
                "Contact telephone": string_column(checks.phone_regex(), nullable=True),
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
                "Portfolio progress": string_column(),
            },
        },
    },
    "Portfolio RAG ratings": {
        "extract": {
            "id_tag": "PF-USER_PORTFOLIO-RAG-RATINGS",
            "worksheet_name": "Progress",
        },
        "process": {
            "merged_header_rows": [0],
            "dropdown_placeholder": "Please select an option",
        },
        "validate": {
            "columns": {
                "Statement": string_column(checks.is_in(PFEnums.PORTFOLIO_STATEMENTS)),
                "RAG rating": string_column(checks.is_in(PFEnums.RAGS)),
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
                "Project name": string_column(unique=True, report_duplicates="exclude_first"),
                "Project status": string_column(checks.is_in(PFEnums.PROJECT_STATUS)),
                "Spend RAG rating": string_column(checks.is_in(PFEnums.RAGS)),
                "Delivery RAG rating": string_column(checks.is_in(PFEnums.RAGS)),
                "Why have you given these ratings? Enter an explanation (100 words max)": string_column(
                    checks.max_word_count(100)
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
                "Big issues across portfolio": string_column(),
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
                "Upcoming significant milestones": string_column(),
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
                "Project name": string_column(unique=True, report_duplicates="exclude_first"),
                "Project full postcode/postcodes (for example, AB1D 2EF)": string_column(checks.postcode_list()),
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
                "Baseline output",
                "Total cumulative outputs to date, Total",
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
                "Variance % (Between MR and Baseline)",
            ],
            "drop_empty_rows": True,
            "dropdown_placeholder": "Please select an option",
        },
        "validate": {
            "columns": {
                "Intervention theme": string_column(),
                "Output": string_column(unique=True, report_duplicates="exclude_first"),
                "Unit of measurement": string_column(),
                "Total cumulative outputs to date, (Up to and including Mar 2024), Actual": float_column(),
                "Financial year 2024 to 2025, (Apr to Jun), Actual": float_column(),
                "Financial year 2024 to 2025, (Jul to Sep), Actual": float_column(),
                "Financial year 2024 to 2025, (Oct to Dec), Forecast": float_column(),
                "Financial year 2024 to 2025, (Jan to Mar), Forecast": float_column(),
                "Financial year 2025 to 2026, (Apr to Jun), Forecast": float_column(),
                "Financial year 2025 to 2026, (Jul to Sep), Forecast": float_column(),
                "Financial year 2025 to 2026, (Oct to Dec), Forecast": float_column(),
                "Financial year 2025 to 2026, (Jan to Mar), Forecast": float_column(),
                "April 2026 and after, Total": float_column(),
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
                "Baseline output",
                "Total cumulative outputs to date, Total",
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
                "Variance % (Between MR and Baseline)",
            ],
            "drop_empty_rows": True,
            "dropdown_placeholder": "Please select an option",
        },
        "validate": {
            "columns": {
                "Intervention theme": string_column(),
                "Output": string_column(unique=True, report_duplicates="exclude_first"),
                "Unit of measurement": string_column(),
                "Total cumulative outputs to date, (Up to and including Mar 2024), Actual": float_column(),
                "Financial year 2024 to 2025, (Apr to Jun), Actual": float_column(),
                "Financial year 2024 to 2025, (Jul to Sep), Actual": float_column(),
                "Financial year 2024 to 2025, (Oct to Dec), Forecast": float_column(),
                "Financial year 2024 to 2025, (Jan to Mar), Forecast": float_column(),
                "Financial year 2025 to 2026, (Apr to Jun), Forecast": float_column(),
                "Financial year 2025 to 2026, (Jul to Sep), Forecast": float_column(),
                "Financial year 2025 to 2026, (Oct to Dec), Forecast": float_column(),
                "Financial year 2025 to 2026, (Jan to Mar), Forecast": float_column(),
                "April 2026 and after, Total": float_column(),
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
                "Baseline outcome",
                "Total cumulative outcomes to date, Total",
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
                "Variance % (Between MR and Baseline)",
            ],
            "drop_empty_rows": True,
            "dropdown_placeholder": "Please select an option",
        },
        "validate": {
            "columns": {
                "Intervention theme": string_column(),
                "Outcome": string_column(unique=True, report_duplicates="exclude_first"),
                "Unit of measurement": string_column(),
                "Total cumulative outcomes to date, (Up to and including Mar 2024), Actual": float_column(),
                "Financial year 2024 to 2025, (Apr to Jun), Actual": float_column(),
                "Financial year 2024 to 2025, (Jul to Sep), Actual": float_column(),
                "Financial year 2024 to 2025, (Oct to Dec), Forecast": float_column(),
                "Financial year 2024 to 2025, (Jan to Mar), Forecast": float_column(),
                "Financial year 2025 to 2026, (Apr to Jun), Forecast": float_column(),
                "Financial year 2025 to 2026, (Jul to Sep), Forecast": float_column(),
                "Financial year 2025 to 2026, (Oct to Dec), Forecast": float_column(),
                "Financial year 2025 to 2026, (Jan to Mar), Forecast": float_column(),
                "April 2026 and after, Total": float_column(),
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
                "Baseline outcome",
                "Total cumulative outcomes to date, Total",
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
                "Variance % (Between MR and Baseline)",
            ],
            "drop_empty_rows": True,
            "dropdown_placeholder": "Please select an option",
        },
        "validate": {
            "columns": {
                "Intervention theme": string_column(),
                "Outcome": string_column(unique=True, report_duplicates="exclude_first"),
                "Unit of measurement": string_column(),
                "Total cumulative outcomes to date, (Up to and including Mar 2024), Actual": float_column(),
                "Financial year 2024 to 2025, (Apr to Jun), Actual": float_column(),
                "Financial year 2024 to 2025, (Jul to Sep), Actual": float_column(),
                "Financial year 2024 to 2025, (Oct to Dec), Forecast": float_column(),
                "Financial year 2024 to 2025, (Jan to Mar), Forecast": float_column(),
                "Financial year 2025 to 2026, (Apr to Jun), Forecast": float_column(),
                "Financial year 2025 to 2026, (Jul to Sep), Forecast": float_column(),
                "Financial year 2025 to 2026, (Oct to Dec), Forecast": float_column(),
                "Financial year 2025 to 2026, (Jan to Mar), Forecast": float_column(),
                "April 2026 and after, Total": float_column(),
            },
            "unique": ["Intervention theme", "Outcome", "Unit of measurement"],
            "report_duplicates": "exclude_first",
        },
    },
    "Current underspend": {
        "extract": {
            "id_tag": "PF-USER_CURRENT-UNDERSPEND",
            "worksheet_name": "Finances",
        },
        "process": {
            "ignored_non_header_rows": [0, 1],
        },
        "validate": {
            "columns": {
                "Current underspend": float_column(checks.greater_than_or_equal_to(0), nullable=True),
            },
        },
    },
    "Forecast and actual spend (capital)": {
        "extract": {
            "id_tag": "PF-USER_FORECAST-AND-ACTUAL-SPEND-CAPITAL",
            "worksheet_name": "Finances",
        },
        "process": {
            "num_header_rows": 3,
            "merged_header_rows": [0],
            "ignored_non_header_rows": [3, 6, 7],
            "col_names_to_drop": [
                "Total cumulative actuals to date, Total",
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
            ],
        },
        "validate": {
            "columns": {
                "Type of spend": string_column(checks.is_in(PFEnums.SPEND_TYPE)),
                "Total cumulative actuals to date, (Up to and including Mar 2024), Actual": float_column(
                    checks.greater_than_or_equal_to(0)
                ),
                "Financial year 2024 to 2025, (Apr to Jun), Actual": float_column(checks.greater_than_or_equal_to(0)),
                "Financial year 2024 to 2025, (Jul to Sep), Actual": float_column(checks.greater_than_or_equal_to(0)),
                "Financial year 2024 to 2025, (Oct to Dec), Forecast": float_column(checks.greater_than_or_equal_to(0)),
                "Financial year 2024 to 2025, (Jan to Mar), Forecast": float_column(checks.greater_than_or_equal_to(0)),
                "Financial year 2025 to 2026, (Apr to Jun), Forecast": float_column(checks.greater_than_or_equal_to(0)),
                "Financial year 2025 to 2026, (Jul to Sep), Forecast": float_column(checks.greater_than_or_equal_to(0)),
                "Financial year 2025 to 2026, (Oct to Dec), Forecast": float_column(checks.greater_than_or_equal_to(0)),
                "Financial year 2025 to 2026, (Jan to Mar), Forecast": float_column(checks.greater_than_or_equal_to(0)),
            },
        },
    },
    "Forecast and actual spend (revenue)": {
        "extract": {
            "id_tag": "PF-USER_FORECAST-AND-ACTUAL-SPEND-REVENUE",
            "worksheet_name": "Finances",
        },
        "process": {
            "num_header_rows": 3,
            "merged_header_rows": [0],
            "ignored_non_header_rows": [3, 6, 7],
            "col_names_to_drop": [
                "Total cumulative actuals to date, Total",
                "Financial year 2024 to 2025, Total",
                "Financial year 2025 to 2026, Total",
                "Grand total",
            ],
        },
        "validate": {
            "columns": {
                "Type of spend": string_column(checks.is_in(PFEnums.SPEND_TYPE)),
                "Total cumulative actuals to date, (Up to and including Mar 2024), Actual": float_column(
                    checks.greater_than_or_equal_to(0)
                ),
                "Financial year 2024 to 2025, (Apr to Jun), Actual": float_column(checks.greater_than_or_equal_to(0)),
                "Financial year 2024 to 2025, (Jul to Sep), Actual": float_column(checks.greater_than_or_equal_to(0)),
                "Financial year 2024 to 2025, (Oct to Dec), Forecast": float_column(checks.greater_than_or_equal_to(0)),
                "Financial year 2024 to 2025, (Jan to Mar), Forecast": float_column(checks.greater_than_or_equal_to(0)),
                "Financial year 2025 to 2026, (Apr to Jun), Forecast": float_column(checks.greater_than_or_equal_to(0)),
                "Financial year 2025 to 2026, (Jul to Sep), Forecast": float_column(checks.greater_than_or_equal_to(0)),
                "Financial year 2025 to 2026, (Oct to Dec), Forecast": float_column(checks.greater_than_or_equal_to(0)),
                "Financial year 2025 to 2026, (Jan to Mar), Forecast": float_column(checks.greater_than_or_equal_to(0)),
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
                "Uncommitted funding plan": string_column(),
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
                "Summary of changes below change request threshold": string_column(),
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
                "Change number": int_column(unique=True, report_duplicates="exclude_first"),
                "Project funding moved from": string_column(),
                "Intervention theme moved from": string_column(),
                "Project funding moved to": string_column(),
                "Intervention theme moved to": string_column(),
                "Amount moved": float_column(checks=[checks.greater_than(0), checks.less_than(5_000_000)]),
                "What changes have you made / or are planning to make? (100 words max)": string_column(
                    checks.max_word_count(100)
                ),
                "Reason for change (100 words max)": string_column(checks.max_word_count(100)),
                "Actual, forecast or cancelled": string_column(checks.is_in(PFEnums.ACTUAL_FORECAST)),
                "Reporting period change takes place": string_column(checks.is_in(PFEnums.REPORTING_PERIOD)),
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
                "Risk name": string_column(unique=True, report_duplicates="exclude_first"),
                "Category": string_column(checks.is_in(PFEnums.RISK_CATEGORIES)),
                "Description": string_column(checks.max_word_count(100)),
                "Pre-mitigated likelihood score": string_column(checks.is_in(PFEnums.RISK_SCORES)),
                "Pre-mitigated impact score": string_column(checks.is_in(PFEnums.RISK_SCORES)),
                "Mitigations": string_column(checks.max_word_count(100)),
                "Post-mitigated likelihood score": string_column(checks.is_in(PFEnums.RISK_SCORES)),
                "Post-mitigated impact score": string_column(checks.is_in(PFEnums.RISK_SCORES)),
            },
            "checks": checks.exactly_x_rows(5),
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
                "Signatory name": string_column(),
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
                "Signatory role": string_column(),
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
                "Signature date": datetime_column(checks.not_in_future()),
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
                "Local Authority": string_column(),
                "Reference": string_column(),
                "Project name": string_column(),
                "Status": string_column(),
                "Full name": string_column(),
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
                "Standard output": string_column(),
                "UoM": string_column(nullable=True),
                "Intervention theme": string_column(nullable=True),
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
                "Standard outcome": string_column(),
                "UoM": string_column(nullable=True),
                "Intervention theme": string_column(nullable=True),
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
                "Local Authority": string_column(),
                "Output": string_column(),
                "UoM": string_column(nullable=True),
                "Intervention theme": string_column(),
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
                "Local Authority": string_column(),
                "Outcome": string_column(),
                "UoM": string_column(nullable=True),
                "Intervention theme": string_column(),
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
                "Intervention theme": string_column(),
            }
        },
    },
}
