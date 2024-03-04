import pandas as pd

FINANCIAL_COMPLETION_DATE = pd.DataFrame({"Pathfinder financial completion date": [pd.Timestamp("2001-01-01")]})

PRACTICAL_COMPLETION_DATE = pd.DataFrame({"Practical completion date": [pd.Timestamp("2001-01-01")]})

ORGANISATION_NAME = pd.DataFrame({"Organisation name": ["Bolton Metropolitan Borough Council"]})

CONTACT_NAME = pd.DataFrame({"Name": ["Steve Jobs"]})

CONTACT_EMAIL_ADDRESS = pd.DataFrame({"Email address": ["testing@test.gov.uk"]})

CONTACT_TELEPHONE = pd.DataFrame({"Telephone (Optional)": [pd.NA]})

PORTFOLIO_PROGRESS = pd.DataFrame({"How is the delivery of your portfolio progressing?": ["word word word word word"]})

PROJECT_PROGRESS = pd.DataFrame(
    {
        "Project name": ["Wellsprings Innovation Hub"],
        "Spend RAG rating": ["Amber/Green"],
        "Delivery RAG rating": ["Amber/Green"],
        "Why have you given these ratings?": ["an explanation"],
    }
)

PORTFOLIO_BIG_ISSUES = pd.DataFrame({"What are the big issues across your portfolio?": ["some big issues"]})

SIGNIFICANT_MILESTONES = pd.DataFrame({"What significant milestones are coming up?": ["some milestones"]})

PROJECT_LOCATION = pd.DataFrame(
    {
        "Project name": ["Wellsprings Innovation Hub"],
        "Location": ["M1 1AG"],
    }
)

OUTPUTS = pd.DataFrame(
    {
        "Intervention theme": ["Enhancing sub-regional and regional connectivity"],
        "Output": ["Total length of new pedestrian paths"],
        "Unit of measurement": ["km"],
        **{
            f"Financial year {year} to {year + 1}, ({quarter}), {'Actual' if year < 2024 else 'Forecast'}": [1.0]
            for year in range(2023, 2026)
            for quarter in ["Apr to June", "July to Sept", "Oct to Dec", "Jan to Mar"]
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
            f"Financial year {year} to {year + 1}, ({quarter}), {'Actual' if year < 2024 else 'Forecast'}": [1.0]
            for year in range(2023, 2026)
            for quarter in ["Apr to June", "July to Sept", "Oct to Dec", "Jan to Mar"]
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

UNDERSPEND = pd.DataFrame({"What's your underspend for this financial year?": [0.0]})

CURRENT_UNDERSPEND = pd.DataFrame({"What's your current underspend for this financial year?": [0.0]})

UNDERSPEND_REQUESTED = pd.DataFrame({"How much underspend are you asking for with a credible plan?": [0.0]})

SPENDING_PLAN = pd.DataFrame({"How do you plan to spend this value in the next financial year?": [pd.NA]})

FORECAST_SPEND = pd.DataFrame({"What is your forecast spend for the next financial year?": [0.0]})

FORECAST_AND_ACTUAL_SPEND = pd.DataFrame(
    {
        "Type of spend": [
            "How much of your forecast is contractually committed?",
            "Freedom and flexibilities spend",
            "Total DLUHC spend (incl F&F)",
            "Secured Match Funding Spend",
            "Unsecured Match Funding",
            "Total Match",
        ],
        **{
            f"Financial year {year} to {year + 1}, ({quarter}), {'Actual' if year < 2024 else 'Forecast'}": [
                1.0,
                0.0,
                0.0,
                0.0,
                0.0,
                0.0,
            ]
            for year in range(2023, 2026)
            for quarter in ["Apr to June", "July to Sept", "Oct to Dec", "Jan to Mar"]
        },
        "April 2026 and after, Total": [0.0, 0.0, 0.0, 0.0, 0.0, 0.0],
    }
)

UNCOMMITTED_FUNDING_PLAN = pd.DataFrame({"What is your plan for using any uncommitted funding?": [pd.NA]})

CHANGE_REQUEST_THRESHOLD = pd.DataFrame(
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

SIGN_OFF_NAME = pd.DataFrame({"Name": [pd.NA]})

SIGN_OFF_ROLE = pd.DataFrame({"Role": [pd.NA]})

SIGN_OFF_DATE = pd.DataFrame({"Date": [pd.NA]})

EXTRACTED_VALIDATED_DATA = {
    "Financial Completion Date": FINANCIAL_COMPLETION_DATE,
    "Practical Completion Date": PRACTICAL_COMPLETION_DATE,
    "Organisation Name": ORGANISATION_NAME,
    "Contact Name": CONTACT_NAME,
    "Contact Email Address": CONTACT_EMAIL_ADDRESS,
    "Contact Telephone": CONTACT_TELEPHONE,
    "Portfolio Progress": PORTFOLIO_PROGRESS,
    "Project Progress": PROJECT_PROGRESS,
    "Portfolio Big Issues": PORTFOLIO_BIG_ISSUES,
    "Significant Milestones": SIGNIFICANT_MILESTONES,
    "Project Location": PROJECT_LOCATION,
    "Outputs": OUTPUTS,
    "Outcomes": OUTCOMES,
    "Risks": RISKS,
    "Underspend": UNDERSPEND,
    "Current Underspend": CURRENT_UNDERSPEND,
    "Underspend Requested": UNDERSPEND_REQUESTED,
    "Spending Plan": SPENDING_PLAN,
    "Forecast Spend": FORECAST_SPEND,
    "Forecast and Actual Spend": FORECAST_AND_ACTUAL_SPEND,
    "Uncommitted Funding Plan": UNCOMMITTED_FUNDING_PLAN,
    "Change Request Threshold": CHANGE_REQUEST_THRESHOLD,
    "Project Finance Changes": PROJECT_FINANCE_CHANGES,
    "Sign Off Name": SIGN_OFF_NAME,
    "Sign Off Role": SIGN_OFF_ROLE,
    "Sign Off Date": SIGN_OFF_DATE,
}
