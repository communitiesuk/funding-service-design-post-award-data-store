import re
from copy import deepcopy
from datetime import datetime

import pandas as pd

from core.const import EXCEL_MIMETYPE
from core.controllers.download import sort_output_dataframes


def test_invalid_file_format(test_client):
    response = test_client.get("/download?file_format=invalid")
    assert response.status_code == 400


def test_download_json_format(seeded_test_client):  # noqa
    response = seeded_test_client.get("/download?file_format=json")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_download_json_with_outcome_categories(seeded_test_client):  # noqa
    response = seeded_test_client.get("/download?file_format=json&outcome_categories=Place")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_download_excel_format(seeded_test_client):
    response = seeded_test_client.get("/download?file_format=xlsx")
    assert response.status_code == 200
    assert response.content_type == EXCEL_MIMETYPE


def test_download_json_format_empty_db(test_client):  # noqa
    response = test_client.get("/download?file_format=json")
    assert response.status_code == 200
    assert response.content_type == "application/json"


def test_download_excel_format_empty_db(test_client):
    response = test_client.get("/download?file_format=xlsx")
    assert response.status_code == 200
    assert response.content_type == EXCEL_MIMETYPE


def test_sort_columns_function(test_client):
    """Test dataframe sorted according to primary and secondary columns defined in constants dict."""

    # Example data for PlaceDetails
    test_data = {
        "SubmissionID": ["S-R03-3", "S-R03-2", "S-R03-2", "S-R03-1"],
        "ProgrammeID": ["FHSF001", "FHSF002", "FHSF002", "FHSF003"],
        "Question": [
            "Grant Recipient's Single Point of Contact",
            "Different Question for duplicate submission:",
            "Grant Recipient:",
            "Programme Senior Responsible Owner",
        ],
        "Indicator": ["Name", "Email", "different indicator", "Telephone"],
        "Answer": ["Town Deal", "Lewes District Council", "whatever", "Surrey"],
        "Place": ["Place 1", "Place 2", "Place 2", "Place 3"],
        "OrganisationName": ["Org 1", "Org 2", "Org X", "Org 3"],
    }
    unsorted_place_df = pd.DataFrame(test_data)

    sorted_place_df = deepcopy(unsorted_place_df)
    sorted_place_df = deepcopy(sort_output_dataframes(sorted_place_df, "PlaceDetails"))

    primary_sort_column = list(sorted_place_df.SubmissionID)
    assert sorted(unsorted_place_df.SubmissionID) == primary_sort_column == sorted(test_data["SubmissionID"])

    assert list(unsorted_place_df.OrganisationName) != list(sorted_place_df.OrganisationName)
    assert list(sorted_place_df.SubmissionID) == ["S-R03-1", "S-R03-2", "S-R03-2", "S-R03-3"]

    secondary_sort_column = list(sorted_place_df.Question)
    assert sorted(unsorted_place_df.Question) != secondary_sort_column
    assert secondary_sort_column == [
        "Programme Senior Responsible Owner",
        "Different Question for duplicate submission:",
        "Grant Recipient:",
        "Grant Recipient's Single Point of Contact",
    ]
    assert list(sorted_place_df.OrganisationName) == ["Org 3", "Org 2", "Org X", "Org 1"]


def test_download_filename(test_client):
    response = test_client.get("/download?file_format=xlsx")

    # Regex pattern for datetime format %Y-%m-%d-%H%M%S
    datetime_pattern = r"^\d{4}-\d{2}-\d{2}-\d{6}$"
    extracted_datetime = re.search(r"\d{4}-\d{2}-\d{2}-\d{6}", response.headers[2][1]).group()

    assert re.match(datetime_pattern, extracted_datetime)
    assert datetime.strptime(extracted_datetime, "%Y-%m-%d-%H%M%S")
