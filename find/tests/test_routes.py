import re
from datetime import datetime
from unittest.mock import patch

from app.const import MIMETYPE


def test_index_page(flask_test_client):
    response = flask_test_client.get("/")
    assert response.status_code == 302


def test_download_get(requests_mock, flask_test_client):
    requests_mock.get("http://data-store/organisations", json=[])
    requests_mock.get("http://data-store/regions", json=[])
    requests_mock.get("http://data-store/funds", json=[])
    requests_mock.get("http://data-store/outcome-categories", json=[])
    requests_mock.get(
        "http://data-store/reporting-period-range",
        json={"end_date": "2023-02-01T00:00:00Z", "start_date": "2023-02-12T00:00:00Z"},
    )
    response = flask_test_client.get("/download")
    assert response.status_code == 200


@patch("app.main.routes.get_response")
def test_download_post_json(mock_get_response, flask_test_client, mocker):
    mock_response = mock_get_response.return_value
    mock_response.json.return_value = {"data": "test"}
    mock_response.headers = {"content-type": MIMETYPE.JSON}
    mocker.patch(
        "app.main.routes.quarter_to_date", return_value="2020-01-01T00:00:00Z"
    )  # this mocks the function return value

    response = flask_test_client.post("/download", data={"file_format": "json"})
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert response.data == b'{"data": "test"}'


@patch("app.main.routes.get_response")
def test_download_post_xlsx(mock_get_response, mocker, flask_test_client):
    mock_response = mock_get_response.return_value
    mock_response.content = b"xlsx data"
    mock_response.headers = {"content-type": MIMETYPE.XLSX}

    mocker.patch(
        "app.main.routes.quarter_to_date", return_value="2020-01-01T00:00:00Z"
    )  # this mocks the function return value

    response = flask_test_client.post("/download", data={"file_format": "xlsx"})
    assert response.status_code == 200
    assert (
        response.mimetype
        == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
    assert response.data == b"xlsx data"


def test_download_post_unknown_format(flask_test_client):
    response = flask_test_client.post("/download", data={"file_format": "foobar"})
    assert response.status_code == 500


def test_download_post_no_format(flask_test_client):
    response = flask_test_client.post("/download")
    assert response.status_code == 500


@patch("app.main.routes.get_response")
def test_download_post_unknown_format_from_api(mock_get_response, flask_test_client):
    mock_response = mock_get_response.return_value
    mock_response.headers = {"content-type": "InvalidType"}

    response = flask_test_client.post("/download?file_format=anything")
    assert response.status_code == 500


@patch("app.main.routes.get_response")
def test_download_fails_csrf(mock_get_response, flask_test_client):
    flask_test_client.application.config["WTF_CSRF_ENABLED"] = True
    response = flask_test_client.post("/download", data={"file_format": "json"})
    assert response.status_code == 302


@patch("app.main.routes.get_response")
def test_download_filename_date(mock_get_response, mocker, flask_test_client):
    mock_response = mock_get_response.return_value
    mock_response.content = b"xlsx data"
    mock_response.headers = {"content-type": MIMETYPE.XLSX}

    mocker.patch(
        "app.main.routes.quarter_to_date", return_value="2020-01-01T00:00:00Z"
    )  # this mocks the function return value

    response = flask_test_client.post("/download", data={"file_format": "xlsx"})

    # Regex pattern for datetime format %Y-%m-%d-%H%M%S
    datetime_pattern = r"^\d{4}-\d{2}-\d{2}-\d{6}$"
    extracted_datetime = re.search(
        r"\d{4}-\d{2}-\d{2}-\d{6}", response.headers["Content-Disposition"]
    ).group()

    # Assert datetime stamp on file is in correct format
    assert re.match(datetime_pattern, extracted_datetime)
    assert datetime.strptime(extracted_datetime, "%Y-%m-%d-%H%M%S")
