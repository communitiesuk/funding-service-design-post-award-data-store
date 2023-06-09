from app.main.data import get_response
from config import Config


def get_checkbox_data(endpoint):
    response = get_response(hostname=Config.DATA_STORE_API_HOST, endpoint=endpoint)

    # If the API returns 404, use empty array
    if response.status_code == 404:
        return []

    # Else, populate checkboxes with the response
    elif response.status_code == 200:
        return response.json()


# TODO remove all hardcoded data and replace with API calls
fund = [
    {"id": "FHSF", "name": "High Street Fund"},
    {"id": "TFTD", "name": "Towns Fund - Town Deals"},
]


area = [
    {"name": "North East", "id": "TLC"},
    {"name": "North West", "id": "TLD"},
    {"name": "Yorkshire and the Humber", "id": "TLE"},
    {"name": "East Midlands", "id": "TLF"},
    {"name": "West Midlands", "id": "TLG"},
    {"name": "East of England", "id": "TLH"},
    {"name": "London", "id": "TLI"},
    {"name": "South East", "id": "TLJ"},
    {"name": "South West", "id": "TLK"},
    {"name": "Scotland", "id": "TLM"},
    {"name": "Wales", "id": "TLL"},
    {"name": "Northern Ireland", "id": "TLN"},
]


fundedOrg = (
    [
        {"text": "Allerdale Borough Council", "value": "Allerdale Borough Council"},
        {
            "text": "Amber Valley Borough Council",
            "value": "Amber Valley Borough Council",
        },
        {"text": "Ashfield District Council", "value": "Ashfield District Council"},
        {
            "text": "Barnsley Metropolitan Borough Council",
            "value": "Barnsley Metropolitan Borough Council",
        },
        {
            "text": "Bolton Metropolitan Borough Council",
            "value": "Bolton Metropolitan Borough Council",
        },
        {
            "text": "Calderdale Metropolitan Borough Council",
            "value": "Calderdale Metropolitan Borough Council",
        },
        {"text": "Carlisle City Council", "value": "Carlisle City Council"},
        {"text": "Cheshire East Council", "value": "Cheshire East Council"},
        {
            "text": "Cheshire West and Chester Council",
            "value": "Cheshire West and Chester Council",
        },
        {"text": "Cornwall Council", "value": "Cornwall Council"},
        {"text": "Derby City Council", "value": "Derby City Council"},
        {"text": "Dover District Council", "value": "Dover District Council"},
        {
            "text": "Dudley Metropolitan Borough Council",
            "value": "Dudley Metropolitan Borough Council",
        },
    ],
)


outcomes = {
    "name": "outcome",
    "items": [
        {"text": "Business", "value": "Business"},
        {"text": "Culture", "value": "Culture"},
        {"text": "Economy", "value": "Economy"},
        {"text": "Education", "value": "Education"},
        {"text": "Health & Wellbeing", "value": "Health & Wellbeing"},
        {"text": "Place", "value": "Place"},
        {"text": "Regeneration", "value": "Regeneration"},
        {"text": "Transport", "value": "Transport"},
    ],
}


returns = {
    "name": "return_period",
    "quarter": (1, 2, 3, 4),
    "year": ("2022/2023", "2023/2024"),
}
