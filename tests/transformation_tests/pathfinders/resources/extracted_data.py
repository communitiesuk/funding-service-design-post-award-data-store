import pandas as pd

FINANCIAL_COMPLETION_DATE = pd.DataFrame({"Pathfinder financial completion date": [pd.Timestamp("2001-01-01")]})

PRACTICAL_COMPLETION_DATE = pd.DataFrame({"Practical completion date": [pd.Timestamp("2001-01-01")]})

ORGANISATION_NAME = pd.DataFrame({"Organisation name": ["Bolton Metropolitan Borough Council"]})

CONTACT_NAME = pd.DataFrame({"Name": ["Steve Jobs"]})

CONTACT_EMAIL_ADDRESS = pd.DataFrame({"Email address": ["testing@test.gov.uk"]})

CONTACT_TELEPHONE = pd.DataFrame({"Telephone (optional)": [pd.NA]})

PORTFOLIO_PROGRESS = pd.DataFrame({"How is the delivery of your portfolio progressing?": ["word word word word word"]})

PROJECT_PROGRESS = pd.DataFrame(
    {
        "Project name": ["Wellsprings Innovation Hub", "Bolton Market Upgrades"],
        "Spend RAG rating": ["Amber/Green", "Green"],
        "Delivery RAG rating": ["Green", "Amber"],
        "Why have you given these ratings? Enter an explanation (100 words max)": [
            "No comment",
            "Wouldn't you like to know",
        ],
    }
)

PORTFOLIO_BIG_ISSUES = pd.DataFrame({"What are the big issues across your portfolio?": ["some big issues"]})

SIGNIFICANT_MILESTONES = pd.DataFrame({"What significant milestones are coming up?": ["some milestones"]})

PROJECT_LOCATION = pd.DataFrame(
    {
        "Project name": ["Wellsprings Innovation Hub", "Bolton Market Upgrades"],
        'Project full postcode/postcodes (e.g., "AB1D 2EF")': ["BL1 1SE", "BL1 1TJ, BL1 1TQ"],
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

RISKS = pd.DataFrame(
    {
        "Risk name": ["A risk"],
        "Category": ["Strategy risks"],
        "Description": ["a description"],
        "Likelihood score": ["3 - medium"],
        "Impact score": ["1 - very low"],
        "Mitigations": ["some mitigations"],
    }
)

CREDIBLE_PLAN = pd.DataFrame(
    {
        'Do you wish to submit a "credible plan" for any grant paid to you but not spent in the current financial '
        "year?": ["Yes"]
    }
)

TOTAL_UNDERSPEND = pd.DataFrame({"What is the total underspend for this financial year?": [0.0]})

UNDERSPEND_USE_PROPOSAL = pd.DataFrame({'How much underspend are you proposing to use in the "credible plan"?': [0.0]})

CREDIBLE_PLAN_SUMMARY = pd.DataFrame(
    {
        "Please summarise your credible plan including how you intend to spend the proposed amount of funding given for"
        " Q3 in the upcoming financial year?": [pd.NA]
    }
)

CURRENT_UNDERSPEND = pd.DataFrame({"What is the current underspend for this financial year?": [0.0]})

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

UNCOMMITTED_FUNDING_PLAN = pd.DataFrame({"What is your plan for using any uncommitted funding?": [pd.NA]})

CHANGES_BELOW_THRESHOLD_SUMMARY = pd.DataFrame(
    {"What changes have you made, or plan to make, that are below the change request threshold?": [pd.NA]}
)

PROJECT_FINANCE_CHANGES = pd.DataFrame(
    {
        "Change number": [1],
        "Project funding moved from": ["Wellsprings Innovation Hub"],
        "Intervention theme moved from": ["Enhancing sub-regional and regional connectivity"],
        "Project funding moved to": ["Wellsprings Innovation Hub"],
        "Intervention theme moved to": ["Strengthening the visitor and local service economy"],
        "Amount moved": [100.32],
        "Changes made (100 words max)": ["changes"],
        "Reason for change (100 words max)": ["reasons"],
        "Forecast or actual change": ["Actual"],
        "Reporting period change took place": ["Q1 Apr - Jun 23/24"],
    }
)

SIGN_OFF_NAME = pd.DataFrame({"Name": ["Graham Bell"]})

SIGN_OFF_ROLE = pd.DataFrame({"Role": ["Project Manager"]})

SIGN_OFF_DATE = pd.DataFrame({"Date": [pd.Timestamp("2024-03-05")]})

EXTRACTED_USER_TABLES = {
    "Financial completion date": FINANCIAL_COMPLETION_DATE,
    "Practical completion date": PRACTICAL_COMPLETION_DATE,
    "Organisation name": ORGANISATION_NAME,
    "Contact name": CONTACT_NAME,
    "Contact email address": CONTACT_EMAIL_ADDRESS,
    "Contact telephone": CONTACT_TELEPHONE,
    "Portfolio progress": PORTFOLIO_PROGRESS,
    "Project progress": PROJECT_PROGRESS,
    "Portfolio big issues": PORTFOLIO_BIG_ISSUES,
    "Significant milestones": SIGNIFICANT_MILESTONES,
    "Project location": PROJECT_LOCATION,
    "Outputs": OUTPUTS,
    "Outcomes": OUTCOMES,
    "Risks": RISKS,
    "Credible plan": CREDIBLE_PLAN,
    "Total underspend": TOTAL_UNDERSPEND,
    "Underspend use proposal": UNDERSPEND_USE_PROPOSAL,
    "Credible plan summary": CREDIBLE_PLAN_SUMMARY,
    "Current underspend": CURRENT_UNDERSPEND,
    "Forecast and actual spend": FORECAST_AND_ACTUAL_SPEND,
    "Uncommitted funding plan": UNCOMMITTED_FUNDING_PLAN,
    "Changes below threshold summary": CHANGES_BELOW_THRESHOLD_SUMMARY,
    "Project finance changes": PROJECT_FINANCE_CHANGES,
    "Sign off name": SIGN_OFF_NAME,
    "Sign off role": SIGN_OFF_ROLE,
    "Sign off date": SIGN_OFF_DATE,
}

PROJECT_DETAILS = pd.DataFrame(
    {
        "Local Authority": ["Bolton Metropolitan Borough Council", "Bolton Metropolitan Borough Council"],
        "Reference": ["PF-BOL-001", "PF-BOL-002"],
        "Project name": ["Wellsprings Innovation Hub", "Bolton Market Upgrades"],
        "Status": ["Active", "Active"],
        "Full name": ["PF-BOL-001: Wellsprings Innovation Hub", "PF-BOL-002: Bolton Market Upgrades"],
    }
)

STANDARD_OUTPUTS = pd.DataFrame({"Standard outputs": ["Amount of existing parks/greenspace/outdoor improved"]})

STANDARD_OUTCOMES = pd.DataFrame({"Standard outcomes": ["Audience numbers for cultural events"]})

BESPOKE_OUTPUTS = pd.DataFrame(
    {
        "Local Authority": ["Bolton Metropolitan Borough Council"],
        "Output": ["Amount of new office space (m2)"],
    }
)

BESPOKE_OUTCOMES = pd.DataFrame(
    {
        "Local Authority": ["Bolton Metropolitan Borough Council"],
        "Outcome": ["Travel times in corridors of interest"],
    }
)

EXTRACTED_CONTROL_TABLES = {
    "Project details control": PROJECT_DETAILS,
    "Bespoke outputs control": BESPOKE_OUTPUTS,
    "Bespoke outcomes control": BESPOKE_OUTCOMES,
}

EXTRACTED_TABLES = {
    **EXTRACTED_USER_TABLES,
    **EXTRACTED_CONTROL_TABLES,
}
