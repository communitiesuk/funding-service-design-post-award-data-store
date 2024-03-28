import pandas as pd

REPORTING_PERIOD = pd.DataFrame({"Reporting period": ["Q4 2023/24: Jan 2024 - Mar 2024"]})

FINANCIAL_COMPLETION_DATE = pd.DataFrame({"Financial completion date": [pd.Timestamp("2001-01-01")]})

PRACTICAL_COMPLETION_DATE = pd.DataFrame({"Practical completion date": [pd.Timestamp("2001-01-01")]})

ORGANISATION_NAME = pd.DataFrame({"Organisation name": ["Bolton Council"]})

CONTACT_NAME = pd.DataFrame({"Contact name": ["Steve Jobs"]})

CONTACT_EMAIL_ADDRESS = pd.DataFrame({"Contact email": ["testing@test.gov.uk"]})

CONTACT_TELEPHONE = pd.DataFrame({"Contact telephone": [pd.NA]})

PORTFOLIO_PROGRESS = pd.DataFrame({"Portfolio progress": ["word word word word word"]})

PROJECT_PROGRESS = pd.DataFrame(
    {
        "Project name": ["PF-BOL-001: Wellsprings Innovation Hub", "PF-BOL-002: Bolton Market Upgrades"],
        "Spend RAG rating": ["Amber/Green", "Green"],
        "Delivery RAG rating": ["Green", "Amber"],
        "Why have you given these ratings? Enter an explanation (100 words max)": [
            "No comment",
            "Wouldn't you like to know",
        ],
    }
)

BIG_ISSUES_ACROSS_PORTFOLIO = pd.DataFrame({"Big issues across portfolio": ["some big issues"]})

UPCOMING_SIGNIFICANT_MILESTONES = pd.DataFrame({"Upcoming significant milestones": ["some milestones"]})

PROJECT_LOCATION = pd.DataFrame(
    {
        "Project name": ["PF-BOL-001: Wellsprings Innovation Hub", "PF-BOL-002: Bolton Market Upgrades"],
        "Project full postcode/postcodes (for example, AB1D 2EF)": ["BL1 1SE", "BL1 1TJ, BL1 1TQ"],
    }
)

OUTPUTS = pd.DataFrame(
    {
        "Intervention theme": ["Enhancing subregional and regional connectivity"],
        "Output": ["Total length of new pedestrian paths"],
        "Unit of measurement": ["km"],
        "Financial year 2023 to 2024, (Jan to Mar), Actual": [1.0],
        "Financial year 2024 to 2025, (Apr to Jun), Forecast": [1.0],
        "Financial year 2024 to 2025, (Jul to Sep), Forecast": [1.0],
        "Financial year 2024 to 2025, (Oct to Dec), Forecast": [1.0],
        "Financial year 2024 to 2025, (Jan to Mar), Forecast": [1.0],
        "Financial year 2025 to 2026, (Apr to Jun), Forecast": [1.0],
        "Financial year 2025 to 2026, (Jul to Sep), Forecast": [1.0],
        "Financial year 2025 to 2026, (Oct to Dec), Forecast": [1.0],
        "Financial year 2025 to 2026, (Jan to Mar), Forecast": [1.0],
        "April 2026 and after, Total": [1.0],
    }
)

BESPOKE_OUTPUTS = pd.DataFrame(
    {
        "Intervention theme": ["Strengthening the visitor and local service economy"],
        "Output": ["Potential entrepreneurs assisted"],
        "Unit of measurement": ["n of"],
        "Financial year 2023 to 2024, (Jan to Mar), Actual": [5.0],
        "Financial year 2024 to 2025, (Apr to Jun), Forecast": [5.0],
        "Financial year 2024 to 2025, (Jul to Sep), Forecast": [5.0],
        "Financial year 2024 to 2025, (Oct to Dec), Forecast": [5.0],
        "Financial year 2024 to 2025, (Jan to Mar), Forecast": [5.0],
        "Financial year 2025 to 2026, (Apr to Jun), Forecast": [5.0],
        "Financial year 2025 to 2026, (Jul to Sep), Forecast": [5.0],
        "Financial year 2025 to 2026, (Oct to Dec), Forecast": [5.0],
        "Financial year 2025 to 2026, (Jan to Mar), Forecast": [5.0],
        "April 2026 and after, Total": [5.0],
    }
)

OUTCOMES = pd.DataFrame(
    {
        "Intervention theme": ["Unlocking and enabling industrial, commercial, and residential development"],
        "Outcome": ["Vehicle flow"],
        "Unit of measurement": ["km"],
        "Financial year 2023 to 2024, (Jan to Mar), Actual": [1.0],
        "Financial year 2024 to 2025, (Apr to Jun), Forecast": [1.0],
        "Financial year 2024 to 2025, (Jul to Sep), Forecast": [1.0],
        "Financial year 2024 to 2025, (Oct to Dec), Forecast": [1.0],
        "Financial year 2024 to 2025, (Jan to Mar), Forecast": [1.0],
        "Financial year 2025 to 2026, (Apr to Jun), Forecast": [1.0],
        "Financial year 2025 to 2026, (Jul to Sep), Forecast": [1.0],
        "Financial year 2025 to 2026, (Oct to Dec), Forecast": [1.0],
        "Financial year 2025 to 2026, (Jan to Mar), Forecast": [1.0],
        "April 2026 and after, Total": [1.0],
    }
)

BESPOKE_OUTCOMES = pd.DataFrame(
    {
        "Intervention theme": [],
        "Outcome": [],
        "Unit of measurement": [],
        "Financial year 2023 to 2024, (Jan to Mar), Actual": [],
        "Financial year 2024 to 2025, (Apr to Jun), Forecast": [],
        "Financial year 2024 to 2025, (Jul to Sep), Forecast": [],
        "Financial year 2024 to 2025, (Oct to Dec), Forecast": [],
        "Financial year 2024 to 2025, (Jan to Mar), Forecast": [],
        "Financial year 2025 to 2026, (Apr to Jun), Forecast": [],
        "Financial year 2025 to 2026, (Jul to Sep), Forecast": [],
        "Financial year 2025 to 2026, (Oct to Dec), Forecast": [],
        "Financial year 2025 to 2026, (Jan to Mar), Forecast": [],
        "April 2026 and after, Total": [],
    }
)

RISKS = pd.DataFrame(
    {
        "Risk name": ["A risk"],
        "Category": ["Strategy risks"],
        "Description": ["a description"],
        "Pre-mitigated likelihood score": ["3 - medium"],
        "Pre-mitigated impact score": ["1 - very low"],
        "Mitigations": ["some mitigations"],
        "Post-mitigated likelihood score": ["1 - very low"],
        "Post-mitigated impact score": ["1 - very low"],
    }
)

CREDIBLE_PLAN = pd.DataFrame({"Credible plan": ["Yes"]})

TOTAL_UNDERSPEND = pd.DataFrame({"Total underspend": [0.0]})

PROPOSED_UNDERSPEND_USE = pd.DataFrame({"Proposed underspend use": [0.0]})

CREDIBLE_PLAN_SUMMARY = pd.DataFrame({"Credible plan summary": ["This is a summary"]})

CURRENT_UNDERSPEND = pd.DataFrame({"Current underspend": [0.0]})

FORECAST_AND_ACTUAL_SPEND = pd.DataFrame(
    {
        "Type of spend": [
            "How much of your forecast is contractually committed?",
            "How much of your forecast is not contractually committed?",
            "Freedom and flexibilities spend",
            "Secured match funding spend",
            "Unsecured match funding",
        ],
        "Financial year 2023 to 2024, (Jan to Mar), Actual": [1.0, 0.0, 0.0, 0.0, 0.0],
        "Financial year 2024 to 2025, (Apr to Jun), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
        "Financial year 2024 to 2025, (Jul to Sep), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
        "Financial year 2024 to 2025, (Oct to Dec), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
        "Financial year 2024 to 2025, (Jan to Mar), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
        "Financial year 2025 to 2026, (Apr to Jun), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
        "Financial year 2025 to 2026, (Jul to Sep), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
        "Financial year 2025 to 2026, (Oct to Dec), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
        "Financial year 2025 to 2026, (Jan to Mar), Forecast": [1.0, 0.0, 0.0, 0.0, 0.0],
    }
)

UNCOMMITTED_FUNDING_PLAN = pd.DataFrame({"Uncommitted funding plan": [pd.NA]})

SUMMARY_OF_CHANGES_BELOW_CHANGE_REQUEST_THRESHOLD = pd.DataFrame(
    {"Summary of changes below change request threshold": [pd.NA]}
)

PROJECT_FINANCE_CHANGES = pd.DataFrame(
    {
        "Change number": [1],
        "Project funding moved from": ["PF-BOL-001: Wellsprings Innovation Hub"],
        "Intervention theme moved from": ["Enhancing subregional and regional connectivity"],
        "Project funding moved to": ["PF-BOL-001: Wellsprings Innovation Hub"],
        "Intervention theme moved to": ["Strengthening the visitor and local service economy"],
        "Amount moved": [100.32],
        "What changes have you made / or are planning to make? (100 words max)": ["change"],
        "Reason for change (100 words max)": ["reason"],
        "Actual, forecast or cancelled": ["Actual"],
        "Reporting period change takes place": ["Q4 2023/24: Jan 2024 - Mar 2024"],
    }
)

SIGNATORY_NAME = pd.DataFrame({"Signatory name": ["Graham Bell"]})

SIGNATORY_ROLE = pd.DataFrame({"Signatory role": ["Project Manager"]})

SIGNATURE_DATE = pd.DataFrame({"Signature date": [pd.Timestamp("2024-03-05")]})

EXTRACTED_USER_TABLES = {
    "Reporting period": REPORTING_PERIOD,
    "Financial completion date": FINANCIAL_COMPLETION_DATE,
    "Practical completion date": PRACTICAL_COMPLETION_DATE,
    "Organisation name": ORGANISATION_NAME,
    "Contact name": CONTACT_NAME,
    "Contact email": CONTACT_EMAIL_ADDRESS,
    "Contact telephone": CONTACT_TELEPHONE,
    "Portfolio progress": PORTFOLIO_PROGRESS,
    "Project progress": PROJECT_PROGRESS,
    "Big issues across portfolio": BIG_ISSUES_ACROSS_PORTFOLIO,
    "Upcoming significant milestones": UPCOMING_SIGNIFICANT_MILESTONES,
    "Project location": PROJECT_LOCATION,
    "Outputs": OUTPUTS,
    "Bespoke outputs": BESPOKE_OUTPUTS,
    "Outcomes": OUTCOMES,
    "Bespoke outcomes": BESPOKE_OUTCOMES,
    "Risks": RISKS,
    "Credible plan": CREDIBLE_PLAN,
    "Total underspend": TOTAL_UNDERSPEND,
    "Proposed underspend use": PROPOSED_UNDERSPEND_USE,
    "Credible plan summary": CREDIBLE_PLAN_SUMMARY,
    "Current underspend": CURRENT_UNDERSPEND,
    "Forecast and actual spend": FORECAST_AND_ACTUAL_SPEND,
    "Uncommitted funding plan": UNCOMMITTED_FUNDING_PLAN,
    "Summary of changes below change request threshold": SUMMARY_OF_CHANGES_BELOW_CHANGE_REQUEST_THRESHOLD,
    "Project finance changes": PROJECT_FINANCE_CHANGES,
    "Signatory name": SIGNATORY_NAME,
    "Signatory role": SIGNATORY_ROLE,
    "Signature date": SIGNATURE_DATE,
}

PROJECT_DETAILS_CONTROL = pd.DataFrame(
    {
        "Local Authority": ["Bolton Council", "Bolton Council"],
        "Reference": ["PF-BOL-001", "PF-BOL-002"],
        "Project name": ["Wellsprings Innovation Hub", "Bolton Market Upgrades"],
        "Status": ["Active", "Active"],
        "Full name": ["PF-BOL-001: Wellsprings Innovation Hub", "PF-BOL-002: Bolton Market Upgrades"],
    }
)

STANDARD_OUTPUTS_CONTROL = pd.DataFrame(
    {
        "Standard output": [
            "Amount of existing parks/greenspace/outdoor improved",
            "Total length of new pedestrian paths",
        ],
        "UoM": [
            "sqm",
            "km",
        ],
        "Intervention theme": [
            "Improving the quality of life of residents",
            "Enhancing subregional and regional connectivity",
        ],
    }
)

STANDARD_OUTCOMES_CONTROL = pd.DataFrame(
    {
        "Standard outcome": [
            "Audience numbers for cultural events",
            "Vehicle flow",
        ],
        "UoM": [
            "n of",
            "km",
        ],
        "Intervention theme": [
            "Strengthening the visitor and local service economy",
            "Unlocking and enabling industrial, commercial, and residential development",
        ],
    }
)


BESPOKE_OUTPUTS_CONTROL = pd.DataFrame(
    {
        "Local Authority": ["Bolton Council"],
        "Output": ["Amount of new office space (m2)"],
        "UoM": ["sqm"],
        "Intervention theme": ["Bespoke"],
    }
)

BESPOKE_OUTCOMES_CONTROL = pd.DataFrame(
    {
        "Local Authority": ["Bolton Council"],
        "Outcome": ["Travel times in corridors of interest"],
        "UoM": ["%"],
        "Intervention theme": ["Bespoke"],
    }
)


INTERVENTION_THEMES_CONTROL = pd.DataFrame(
    {
        "Intervention theme": [
            "Enhancing subregional and regional connectivity",
            "Strengthening the visitor and local service economy",
            "Improving the quality of life of residents",
            "Unlocking and enabling industrial, commercial, and residential development",
        ]
    }
)


EXTRACTED_CONTROL_TABLES = {
    "Project details control": PROJECT_DETAILS_CONTROL,
    "Outputs control": STANDARD_OUTPUTS_CONTROL,
    "Outcomes control": STANDARD_OUTCOMES_CONTROL,
    "Bespoke outputs control": BESPOKE_OUTPUTS_CONTROL,
    "Bespoke outcomes control": BESPOKE_OUTCOMES_CONTROL,
    "Intervention themes control": INTERVENTION_THEMES_CONTROL,
}


EXTRACTED_TABLES = {
    **EXTRACTED_USER_TABLES,
    **EXTRACTED_CONTROL_TABLES,
}
