import pandas as pd

PROJECT_DETAILS = pd.DataFrame(
    {
        "Local Authority": ["Bolton Metropolitan Borough Council", "Bolton Metropolitan Borough Council"],
        "Reference": ["PF-BOL-001", "PF-BOL-002"],
        "Project Name": ["Wellsprings Innovation Hub", "Bolton Market Upgrades"],
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

EXTRACTED_MAPPING_TABLES = {
    "Project details": PROJECT_DETAILS,
    "Standard outputs": STANDARD_OUTPUTS,
    "Standard outcomes": STANDARD_OUTCOMES,
    "Bespoke outputs": BESPOKE_OUTPUTS,
    "Bespoke outcomes": BESPOKE_OUTCOMES,
}
