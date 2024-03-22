import pandas as pd

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
        "Intervention theme": ["Enhancing sub-regional and regional connectivity"],
        "Output": ["Total length of new pedestrian paths"],
        "Unit of measurement": ["km"],
        **{
            f"Financial year {year} to {year + 1}, ({quarter}), "
            f"{'Actual' if year == 2024 and quarter == 'Apr to Jun' else 'Forecast'}": [1.0]
            for year in range(2024, 2026)
            for quarter in ["Apr to Jun", "Jul to Sep", "Oct to Dec", "Jan to Mar"]
        },
        "April 2026 and after, Total": [1.0],
    }
)

BESPOKE_OUTPUTS = pd.DataFrame(
    {
        "Intervention theme": ["Strengthening the visitor and local service economy"],
        "Output": ["Potential entrepreneurs assisted"],
        "Unit of measurement": ["n of"],
        **{
            f"Financial year {year} to {year + 1}, ({quarter}), "
            f"{'Actual' if year == 2024 and quarter == 'Apr to Jun' else 'Forecast'}": [5.0]
            for year in range(2024, 2026)
            for quarter in ["Apr to Jun", "Jul to Sep", "Oct to Dec", "Jan to Mar"]
        },
        "April 2026 and after, Total": [5.0],
    }
)

OUTCOMES = pd.DataFrame(
    {
        "Intervention theme": ["Unlocking and enabling industrial, commercial, and residential development"],
        "Outcome": ["Vehicle flow"],
        "Unit of measurement": ["km"],
        **{
            f"Financial year {year} to {year + 1}, ({quarter}), "
            f"{'Actual' if year == 2024 and quarter == 'Apr to Jun' else 'Forecast'}": [1.0]
            for year in range(2024, 2026)
            for quarter in ["Apr to Jun", "Jul to Sep", "Oct to Dec", "Jan to Mar"]
        },
        "April 2026 and after, Total": [1.0],
    }
)

BESPOKE_OUTCOMES = pd.DataFrame(
    {
        "Intervention theme": [],
        "Outcome": [],
        "Unit of measurement": [],
        **{
            f"Financial year {year} to {year + 1}, ({quarter}), "
            f"{'Actual' if year == 2024 and quarter == 'Apr to Jun' else 'Forecast'}": []
            for year in range(2024, 2026)
            for quarter in ["Apr to Jun", "Jul to Sep", "Oct to Dec", "Jan to Mar"]
        },
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
            "Total DLUHC spend (inc. F&F)",
            "Secured match funding spend",
            "Unsecured match funding",
            "Total match",
        ],
        **{
            f"Financial year {year} to {year + 1}, ({quarter}), "
            f"{'Actual' if year == 2024 and quarter == 'Apr to Jun' else 'Forecast'}": [
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ]
            for year in range(2024, 2026)
            for quarter in ["Apr to Jun", "Jul to Sep", "Oct to Dec", "Jan to Mar"]
        },
        "April 2026 and after, Total": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
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
        "Intervention theme moved from": ["Enhancing sub-regional and regional connectivity"],
        "Project funding moved to": ["PF-BOL-001: Wellsprings Innovation Hub"],
        "Intervention theme moved to": ["Strengthening the visitor and local service economy"],
        "Amount moved": [100.32],
        "What changes have you made / or are planning to make? (100 words max)": ["change"],
        "Reason for change (100 words max)": ["reason"],
        "Actual, forecast or cancelled": ["Actual"],
        "Reporting period change takes place": ["Q1 Apr - Jun 23/24"],
    }
)

SIGNATORY_NAME = pd.DataFrame({"Signatory name": ["Graham Bell"]})

SIGNATORY_ROLE = pd.DataFrame({"Signatory role": ["Project Manager"]})

SIGNATURE_DATE = pd.DataFrame({"Signature date": [pd.Timestamp("2024-03-05")]})

EXTRACTED_USER_TABLES = {
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

PROJECT_DETAILS = pd.DataFrame(
    {
        "Local Authority": ["Bolton Council", "Bolton Council"],
        "Reference": ["PF-BOL-001", "PF-BOL-002"],
        "Project name": ["Wellsprings Innovation Hub", "Bolton Market Upgrades"],
        "Status": ["Active", "Active"],
        "Full name": ["PF-BOL-001: Wellsprings Innovation Hub", "PF-BOL-002: Bolton Market Upgrades"],
    }
)

STANDARD_OUTPUTS = pd.DataFrame(
    {
        "Standard output": ["Amount of existing parks/greenspace/outdoor improved"],
        "UoM": ["sqm"],
        "Intervention theme": ["Improving the quality of life of residents"],
    }
)

STANDARD_OUTCOMES = pd.DataFrame(
    {
        "Standard outcome": ["Audience numbers for cultural events"],
        "UoM": ["n of"],
        "Intervention theme": ["Strengthening the visitor and local service economy"],
    }
)

BESPOKE_OUTPUTS = pd.DataFrame(
    {
        "Local Authority": ["Bolton Council"],
        "Output": ["Amount of new office space (m2)"],
        "UoM": ["sqm"],
        "Intervention theme": ["Bespoke"],
    }
)

BESPOKE_OUTCOMES = pd.DataFrame(
    {
        "Local Authority": ["Bolton Council"],
        "Outcome": ["Travel times in corridors of interest"],
        "UoM": ["%"],
        "Intervention theme": ["Bespoke"],
    }
)

EXTRACTED_CONTROL_TABLES = {
    "Project details control": PROJECT_DETAILS,
    "Outputs control": STANDARD_OUTPUTS,
    "Outcomes control": STANDARD_OUTCOMES,
    "Bespoke outputs control": BESPOKE_OUTPUTS,
    "Bespoke outcomes control": BESPOKE_OUTCOMES,
}

EXTRACTED_TABLES = {
    **EXTRACTED_USER_TABLES,
    **EXTRACTED_CONTROL_TABLES,
}
