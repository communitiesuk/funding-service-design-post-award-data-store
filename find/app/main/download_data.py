from datetime import datetime

fund = {
    "name": "fund",
    "items": [
        {"text": "Towns Fund - Future High Streets Fund", "value": "high-streets"},
        {"text": "Towns Fund - Town Deals", "value": "town-deals"},
    ],
}

area = {
    "name": "area",
    "items": [
        {"text": "North East", "value": "TLC"},
        {"text": "North West", "value": "TLD"},
        {"text": "Yorkshire and the Humber", "value": "TLE"},
        {"text": "East Midlands", "value": "TLF"},
        {"text": "West Midlands", "value": "TLG"},
        {"text": "East of England", "value": "TLH"},
        {"text": "London", "value": "TLI"},
        {"text": "South East", "value": "TLJ"},
        {"text": "South West", "value": "TLK"},
        {"text": "Scotland", "value": "TLM"},
        {"text": "Wales", "value": "TLL"},
        {"text": "Northern Ireland", "value": "TLN"},
    ],
}

fundedOrg = {
    "name": "organisation",
    "items": [
        {"text": "Allerdale Borough Council", "value": "value1"},
        {"text": "Amber Valley Borough Council", "value": "value2"},
        {"text": "Ashfield District Council", "value": "value3"},
        {"text": "Barnsley Metropolitan Borough Council", "value": "value1"},
        {"text": "Bolton Metropolitan Borough Council", "value": "value2"},
        {"text": "Calderdale Metropolitan Borough Council", "value": "value3"},
        {"text": "Carlisle City Council", "value": "value1"},
        {"text": "Cheshire East Council", "value": "value2"},
        {"text": "Cheshire West and Chester Council", "value": "value3"},
        {"text": "Cornwall Council", "value": "value1"},
        {"text": "Derby City Council", "value": "value2"},
        {"text": "Dover District Council", "value": "value3"},
        {"text": "Dudley Metropolitan Borough Council", "value": "value1"},
    ],
}

outcomes = {
    "name": "outcome",
    "items": [
        {"text": "Business", "value": "value1"},
        {"text": "Culture", "value": "value2"},
        {"text": "Economy", "value": "value3"},
        {"text": "Education", "value": "value1"},
        {"text": "Health & Wellbeing", "value": "value2"},
        {"text": "Place", "value": "value3"},
        {"text": "Regeneration", "value": "value1"},
        {"text": "Transport", "value": "value2"},
    ],
}


def generate_financial_years(min_date: datetime, max_date: datetime):
    # Adjust the years for the financial year
    min_year = min_date.year if min_date.month > 3 else min_date.year - 1
    max_year = max_date.year if max_date.month > 3 else max_date.year - 1

    # Generate the list of financial years
    financial_years = ["{}/{}".format(year, year + 1) for year in range(min_year, max_year + 1)]

    return financial_years


def populate_financial_years():
    # TODO: get dates from BE
    # hardcoded values:
    min_date = datetime(2019, 5, 1)
    max_date = datetime(2023, 6, 1)

    return generate_financial_years(min_date, max_date)


returns = {
    "name": "return_period",
    # TODO: replace with validated quarters
    "quarter": (1, 2, 3, 4),
    # TODO: replace with validated years
    "year": (populate_financial_years()),
}
