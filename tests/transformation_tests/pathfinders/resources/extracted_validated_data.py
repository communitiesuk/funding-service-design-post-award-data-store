import pandas as pd

financial_completion_date = pd.DataFrame({"Pathfinder financial completion date": [pd.Timestamp("2001-01-01")]})

practical_completion_date = pd.DataFrame({"Practical completion date": [pd.Timestamp("2001-01-01")]})

organisation_name = pd.DataFrame({"Organisation name": ["Bolton Metropolitan Borough Council"]})

contact_name = pd.DataFrame({"Name": ["Steve Jobs"]})

contact_email_address = pd.DataFrame({"Email address": ["testing@test.gov.uk"]})

contact_telephone = pd.DataFrame({"Telephone (Optional)": [pd.NA]})

portfolio_progress = pd.DataFrame({"How is the delivery of your portfolio progressing?": ["word word word word word"]})

project_progress = pd.DataFrame(
    {
        "Project name": ["Wellsprings Innovation Hub"],
        "Spend RAG rating": ["Amber/Green"],
        "Delivery RAG rating": ["Amber/Green"],
        "Why have you given these ratings?": ["an explanation"],
    }
)

portfolio_big_issues = pd.DataFrame({"What are the big issues across your portfolio?": ["some big issues"]})

significant_milestones = pd.DataFrame({"What significant milestones are coming up?": ["some milestones"]})

project_location = pd.DataFrame(
    {
        "Project name": ["Wellsprings Innovation Hub"],
        "Location": ["M1 1AG"],
    }
)

outputs = pd.DataFrame(
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

outcomes = pd.DataFrame(
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

risks = pd.DataFrame(
    {
        "Risk name": ["A risk"],
        "Category": ["Strategy risks"],
        "Description": ["a description"],
        "Likelihood score": ["3 - medium"],
        "Impact score": ["1 - very low"],
        "Mitigations": ["some mitigations"],
    }
)

underspend = pd.DataFrame({"What's your underspend for this financial year?": [0.0]})

current_underspend = pd.DataFrame({"What's your current underspend for this financial year?": [0.0]})

underspend_requested = pd.DataFrame({"How much underspend are you asking for with a credible plan?": [0.0]})

spending_plan = pd.DataFrame({"How do you plan to spend this value in the next financial year?": [pd.NA]})

forecast_spend = pd.DataFrame({"What is your forecast spend for the next financial year?": [0.0]})

forecast_and_actual_spend = pd.DataFrame(
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

uncommitted_funding_plan = pd.DataFrame({"What is your plan for using any uncommitted funding?": [pd.NA]})

change_request_threshold = pd.DataFrame(
    {"What changes have you made, or plan to make, that are below the change request threshold?": [pd.NA]}
)

project_finance_changes = pd.DataFrame(
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

sign_off_name = pd.DataFrame({"Name": [pd.NA]})

sign_off_role = pd.DataFrame({"Role": [pd.NA]})

sign_off_date = pd.DataFrame({"Date": [pd.NA]})

extracted_validated_dict = {
    "Financial Completion Date": financial_completion_date,
    "Practical Completion Date": practical_completion_date,
    "Organisation Name": organisation_name,
    "Contact Name": contact_name,
    "Contact Email Address": contact_email_address,
    "Contact Telephone": contact_telephone,
    "Portfolio Progress": portfolio_progress,
    "Project Progress": project_progress,
    "Portfolio Big Issues": portfolio_big_issues,
    "Significant Milestones": significant_milestones,
    "Project Location": project_location,
    "Outputs": outputs,
    "Outcomes": outcomes,
    "Risks": risks,
    "Underspend": underspend,
    "Current Underspend": current_underspend,
    "Underspend Requested": underspend_requested,
    "Spending Plan": spending_plan,
    "Forecast Spend": forecast_spend,
    "Forecast and Actual Spend": forecast_and_actual_spend,
    "Uncommitted Funding Plan": uncommitted_funding_plan,
    "Change Request Threshold": change_request_threshold,
    "Project Finance Changes": project_finance_changes,
    "Sign Off Name": sign_off_name,
    "Sign Off Role": sign_off_role,
    "Sign Off Date": sign_off_date,
}
