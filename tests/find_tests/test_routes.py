import re
from datetime import datetime

import pytest
from bs4 import BeautifulSoup


def test_index_page_redirect(find_test_client):
    response = find_test_client.get("/")
    assert response.status_code == 302
    assert response.location == "/download"


def test_unauthenticated_download(unauthenticated_find_test_client):
    response = unauthenticated_find_test_client.get("/")
    assert response.status_code == 200
    assert b"Log in" in response.data


def test_download_get(mocker, find_test_client):
    mocker.patch("find.main.download_data.get_organisation_names", return_value=[])
    mocker.patch("find.main.download_data.get_geospatial_regions", return_value=[])
    mocker.patch("find.main.download_data.get_funds", return_value=[])
    mocker.patch("find.main.download_data.get_outcome_categories", return_value=[])
    mocker.patch(
        "find.main.download_data.get_reporting_period_range",
        return_value={
            "end_date": datetime.fromisoformat("2023-02-01T00:00:00Z"),
            "start_date": datetime.fromisoformat("2023-02-12T00:00:00Z"),
        },
    )
    response = find_test_client.get("/download")
    assert response.status_code == 200

    page = BeautifulSoup(response.text)
    assert page.select_one(".govuk-back-link") is None


@pytest.mark.usefixtures("mock_get_response_json")
def test_download_post_json(find_test_client):
    response = find_test_client.post("/download", data={"file_format": "json"})
    assert response.status_code == 200
    assert response.mimetype == "application/json"
    assert response.data == b'{"data": "test"}'


@pytest.mark.usefixtures("mock_get_response_xlsx")
def test_download_post_xlsx(find_test_client):
    response = find_test_client.post("/download", data={"file_format": "xlsx"})
    assert response.status_code == 200
    assert response.mimetype == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response.data == b"xlsx data"


def test_download_post_unknown_format(find_test_client):
    response = find_test_client.post("/download", data={"file_format": "foobar"})
    assert response.status_code == 500


def test_download_post_no_format(find_test_client):
    response = find_test_client.post("/download")
    assert response.status_code == 500


def test_download_post_unknown_format_from_api(mocker, find_test_client):
    mocker.patch("find.main.routes.api_download", side_effect=ValueError("Unknown file format: anything"))

    response = find_test_client.post("/download?file_format=anything")
    assert response.status_code == 500


@pytest.mark.usefixtures("mock_get_response_xlsx")
def test_download_fails_csrf(find_test_client):
    find_test_client.application.config["WTF_CSRF_ENABLED"] = True
    response = find_test_client.post("/download", data={"file_format": "json"})
    assert response.status_code == 302


@pytest.mark.usefixtures("mock_get_response_xlsx")
def test_download_filename_date(find_test_client):
    response = find_test_client.post("/download", data={"file_format": "xlsx"})

    # Regex pattern for datetime format %Y-%m-%d-%H%M%S
    datetime_pattern = r"^\d{4}-\d{2}-\d{2}-\d{6}$"
    extracted_datetime = re.search(r"\d{4}-\d{2}-\d{2}-\d{6}", response.headers["Content-Disposition"]).group()

    # Assert datetime stamp on file is in correct format
    assert re.match(datetime_pattern, extracted_datetime)
    assert datetime.strptime(extracted_datetime, "%Y-%m-%d-%H%M%S")


def test_known_http_error_redirect(find_test_client):
    # induce a known error
    response = find_test_client.get("/unknown-page")

    assert response.status_code == 404
    # 404.html template should be rendered
    assert b"Page not found" in response.data
    assert b"If you typed the web address, check it is correct." in response.data


def test_http_error_unknown_redirects(find_test_client):
    # induce a 405 error
    response = find_test_client.post("/?g=obj_app_upfile")

    assert response.status_code == 405
    # generic error template should be rendered
    assert b"Sorry, there is a problem with the service" in response.data
    assert b"Try again later." in response.data


def test_start_page_redirect(find_test_client):
    response = find_test_client.get("/start")
    assert response.status_code == 302
    assert response.location == "/download"

    response = find_test_client.post("/start")
    assert response.status_code == 302
    assert response.location == "/download"


@pytest.mark.parametrize("url", ["/help", "/data-glossary"])
def test_back_link(find_test_client, url):
    response = find_test_client.get(url)
    assert response.status_code == 200

    page = BeautifulSoup(response.text)
    back_links = page.select(".govuk-back-link")
    assert len(back_links) == 1
    assert back_links[0].text.strip() == "Back"


@pytest.mark.parametrize(
    "url",
    [
        pytest.param("/privacy", marks=pytest.mark.xfail(reason="we need to build this page")),
        pytest.param("/accessibility", marks=pytest.mark.xfail(reason="we need to build this page")),
        pytest.param("/cookies", marks=pytest.mark.xfail(reason="we need to build this page")),
    ],
)
def test_pages_we_need_to_make_work(find_test_client, url):
    response = find_test_client.get(url)
    assert response.status_code == 200


def test_download_confirmation_page(find_test_client):
    response = find_test_client.get("/request-received")
    assert response.status_code == 200


def test_user_not_signed(unauthenticated_find_test_client):
    response = unauthenticated_find_test_client.get("/request-received")
    assert response.status_code == 302
    assert response.location == "/login"
