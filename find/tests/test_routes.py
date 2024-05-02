import re
from datetime import datetime
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup


def test_index_page_redirect(flask_test_client):
    response = flask_test_client.get("/")
    assert response.status_code == 302
    assert response.location == "/download"


def test_unauthenticated_download(unauthenticated_flask_test_client):
    response = unauthenticated_flask_test_client.get("/")
    assert response.status_code == 200
    assert b"Log in" in response.data


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

    page = BeautifulSoup(response.text)
    assert page.select_one(".govuk-back-link") is None


@pytest.mark.usefixtures("mock_get_response_json")
def test_download_post_json(flask_test_client):
    response = flask_test_client.post("/download", data={"file_format": "json"})
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert response.data == b'{"data": "test"}'


@pytest.mark.usefixtures("mock_get_response_xlsx")
def test_download_post_xlsx(flask_test_client):
    response = flask_test_client.post("/download", data={"file_format": "xlsx"})
    assert response.status_code == 200
    assert response.mimetype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response.data == b"xlsx data"


def test_download_post_unknown_format(flask_test_client):
    response = flask_test_client.post("/download", data={"file_format": "foobar"})
    assert response.status_code == 500


def test_download_post_no_format(flask_test_client):
    response = flask_test_client.post("/download")
    assert response.status_code == 500


@patch("app.main.download_data.get_response")
def test_download_post_unknown_format_from_api(mock_get_response, flask_test_client):
    mock_response = mock_get_response.return_value
    mock_response.headers = {"content-type": "InvalidType"}

    response = flask_test_client.post("/download?file_format=anything")
    assert response.status_code == 500


@pytest.mark.usefixtures("mock_get_response_xlsx")
def test_download_fails_csrf(flask_test_client):
    flask_test_client.application.config["WTF_CSRF_ENABLED"] = True
    response = flask_test_client.post("/download", data={"file_format": "json"})
    assert response.status_code == 302


@pytest.mark.usefixtures("mock_get_response_xlsx")
def test_download_filename_date(flask_test_client):
    response = flask_test_client.post("/download", data={"file_format": "xlsx"})

    # Regex pattern for datetime format %Y-%m-%d-%H%M%S
    datetime_pattern = r"^\d{4}-\d{2}-\d{2}-\d{6}$"
    extracted_datetime = re.search(r"\d{4}-\d{2}-\d{2}-\d{6}", response.headers["Content-Disposition"]).group()

    # Assert datetime stamp on file is in correct format
    assert re.match(datetime_pattern, extracted_datetime)
    assert datetime.strptime(extracted_datetime, "%Y-%m-%d-%H%M%S")


def test_known_http_error_redirect(flask_test_client):
    # induce a known error
    response = flask_test_client.get("/unknown-page")

    assert response.status_code == 404
    # 404.html template should be rendered
    assert b"Page not found" in response.data
    assert b"If you typed the web address, check it is correct." in response.data


def test_http_error_unknown_redirects(flask_test_client):
    # induce a 405 error
    response = flask_test_client.post("/?g=obj_app_upfile")

    assert response.status_code == 405
    # generic error template should be rendered
    assert b"Sorry, there is a problem with the service" in response.data
    assert b"Try again later." in response.data


def test_start_page_get(flask_test_client):
    response = flask_test_client.get("/start")
    assert response.status_code == 200


@pytest.mark.usefixtures("mock_get_response_json")
def test_start_page_post_json(flask_test_client, mocker):
    response = flask_test_client.post("/start", data={"file_format": "json"})
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert response.data == b'{"data": "test"}'


@pytest.mark.usefixtures("mock_get_response_xlsx")
def test_start_page_post_xlsx(flask_test_client):
    response = flask_test_client.post("/start", data={"file_format": "xlsx"})
    assert response.status_code == 200
    assert response.mimetype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response.data == b"xlsx data"


def test_start_page_post_unknown_format(flask_test_client):
    response = flask_test_client.post("/start", data={"file_format": "foobar"})
    assert response.status_code == 400


def test_start_page_post_no_format(flask_test_client):
    response = flask_test_client.post("/start")
    assert response.status_code == 400


@pytest.mark.usefixtures("mock_get_response_json")
def test_start_page_fails_csrf(flask_test_client):
    flask_test_client.application.config["WTF_CSRF_ENABLED"] = True
    response = flask_test_client.post("/start", data={"file_format": "json"})
    assert response.status_code == 302


@pytest.mark.usefixtures("mock_get_response_xlsx")
def test_start_page_filename_date(flask_test_client):
    response = flask_test_client.post("/start", data={"file_format": "xlsx"})

    # Regex pattern for datetime format %Y-%m-%d-%H%M%S
    datetime_pattern = r"^\d{4}-\d{2}-\d{2}-\d{6}$"
    extracted_datetime = re.search(r"\d{4}-\d{2}-\d{2}-\d{6}", response.headers["Content-Disposition"]).group()

    # Assert datetime stamp on file is in correct format
    assert re.match(datetime_pattern, extracted_datetime)
    assert datetime.strptime(extracted_datetime, "%Y-%m-%d-%H%M%S")


@pytest.mark.parametrize(
    "url",
    ["/help", "/privacy", "/data-glossary", "/cookies", "/accessibility"],
)
def test_back_link(flask_test_client, url):
    response = flask_test_client.get(url)
    assert response.status_code == 200

    page = BeautifulSoup(response.text)
    back_links = page.select(".govuk-back-link")
    assert len(back_links) == 1
    assert back_links[0].text.strip() == "Back"
