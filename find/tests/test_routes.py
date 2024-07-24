from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup
from flask import url_for

from app.main.download_data import FileMetadata, process_async_download


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


def test_process_async_download_call(flask_test_client, mocked_routes_process_async_download):
    """Test that the download route calls the process_async_download function with the correct parameters,
    including the user email address."""

    flask_test_client.post("/download", data={"file_format": "xlsx"})
    assert mocked_routes_process_async_download.called
    assert mocked_routes_process_async_download.call_args.args[0] == {
        "file_format": "xlsx",
        "email_address": "test-user@example.com",
    }


def test_process_async_download_function(flask_test_client, mocked_download_data_process_async_download):
    """Test that app/main/process_async_download() function returns status code 204 when
    the download request is successful."""

    status_code = process_async_download({"file_format": "xlsx", "email_address": "test-user@example.com"})
    assert status_code == 204


def test_async_download_redirect_OK(flask_test_client, mocked_download_data_process_async_download):
    """Test that the download route redirects to the request-received page after a successful download request."""

    response = flask_test_client.post("/download", data={"file_format": "xlsx"})
    assert response.status_code == 302  # redirect to request-received page
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    expected_location = url_for("main.request_received", _external=False)
    assert response.headers["Location"] == expected_location


def test_async_download_redirect_error(flask_test_client, mocked_failing_download_data_process_async_download):
    """Test that the download route does not redirect, but renders the 500 error page when
    the download request fails."""

    response = flask_test_client.post("/download", data={"file_format": "xlsx"})
    assert response.status_code != 302
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert b"Sorry, there is a problem with the service" in response.data
    assert b"Try again later." in response.data


def test_download_post_unknown_format(flask_test_client, requests_mock):
    requests_mock.get("http://data-store/organisations", json=[])
    requests_mock.get("http://data-store/regions", json=[])
    requests_mock.get("http://data-store/funds", json=[])
    requests_mock.get("http://data-store/outcome-categories", json=[])
    requests_mock.get(
        "http://data-store/reporting-period-range",
        json={"end_date": "2023-02-01T00:00:00Z", "start_date": "2023-02-12T00:00:00Z"},
    )
    response = flask_test_client.post("/download", data={"file_format": "foobar"})
    assert response.status_code == 200

    soup = BeautifulSoup(response.text, "html.parser")
    error_summary = soup.find("p", {"class": "govuk-error-message"})
    assert error_summary is not None
    assert "Select a file format" in error_summary.text


def test_download_post_no_format(flask_test_client, requests_mock):
    requests_mock.get("http://data-store/organisations", json=[])
    requests_mock.get("http://data-store/regions", json=[])
    requests_mock.get("http://data-store/funds", json=[])
    requests_mock.get("http://data-store/outcome-categories", json=[])
    requests_mock.get(
        "http://data-store/reporting-period-range",
        json={"end_date": "2023-02-01T00:00:00Z", "start_date": "2023-02-12T00:00:00Z"},
    )
    response = flask_test_client.post("/download", data={"file_format": " "})
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert response.status_code == 200

    soup = BeautifulSoup(response.text, "html.parser")
    error_summary = soup.find("p", {"class": "govuk-error-message"})
    assert error_summary is not None
    assert "Select a file format" in error_summary.text


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


def test_start_page_redirect(flask_test_client):
    response = flask_test_client.get("/start")
    assert response.status_code == 302
    assert response.location == "/download"

    response = flask_test_client.post("/start")
    assert response.status_code == 302
    assert response.location == "/download"


@pytest.mark.parametrize("url", ["/help", "/data-glossary"])
def test_back_link(flask_test_client, url):
    response = flask_test_client.get(url)
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
def test_pages_we_need_to_make_work(flask_test_client, url):
    response = flask_test_client.get(url)
    assert response.status_code == 200


def test_download_confirmation_page(flask_test_client):
    response = flask_test_client.get("/request-received")
    assert response.status_code == 200


def test_user_not_signed(unauthenticated_flask_test_client):
    response = unauthenticated_flask_test_client.get("/request-received")
    assert response.status_code == 302
    assert (
        response.location
        == "authenticator/sessions/sign-out?return_app=post-award-frontend&return_path=%2Frequest-received"  # noqa: E501
    )


def test_download_file_exist(flask_test_client):
    file_metadata = FileMetadata(200, "06 July 2024", "Microsoft Excel spreadsheet", "1 MB")

    with patch("app.main.routes.get_find_download_file_metadata", return_value=file_metadata):
        response = flask_test_client.get(
            "/retrieve-download/fund-monitoring-data-2024-07-05-11:18:45-e4c77136-18ca-4ba3-9896-0ce572984e72.json"
        )

    assert response.status_code == 200
    page = BeautifulSoup(response.text)
    download_button = page.select_one("button#download")
    assert download_button is not None


def test_file_not_found(flask_test_client):
    file_metadata = FileMetadata(404, None, None, None)

    with patch("app.main.routes.get_find_download_file_metadata", return_value=file_metadata):
        response = flask_test_client.get(
            "/retrieve-download/fund-monitoring-data-2024-07-05-11:18:45-e4c77136-18ca-4ba3-9896-0ce572984e72.json"
        )

    assert response.status_code == 200
    page = BeautifulSoup(response.text)
    download_button = page.select_one("button#download")
    assert download_button is None
    assert b"Your link to download data has expired" in response.data


def test_presigned_url(
    flask_test_client,
):
    presigned_url = "https://example/presigned-url"
    file_metadata = FileMetadata(200, "06 July 2024", "Microsoft Excel spreadsheet", "1 MB")
    with (
        patch("app.main.routes.get_find_download_file_metadata", return_value=file_metadata),
        patch("app.main.routes.get_presigned_url", return_value=presigned_url),
    ):
        response = flask_test_client.post(
            "/retrieve-download/fund-monitoring-data-2024-07-05-11:18:45-e4c77136-18ca-4ba3-9896-0ce572984e72.json"
        )

    assert response.status_code == 302
    assert response.location == presigned_url


def test_file_not_exist(flask_test_client):
    file_metadata = FileMetadata(404, None, None, None)
    with patch("app.main.routes.get_find_download_file_metadata", return_value=file_metadata):
        response = flask_test_client.post(
            "/retrieve-download/fund-monitoring-data-2024-07-05-11:18:45-e4c77136-18ca-4ba3-9896-0ce572984e72.json"
        )

    assert response.status_code == 302
    assert (
        response.location
        == "/retrieve-download/fund-monitoring-data-2024-07-05-11:18:45-e4c77136-18ca-4ba3-9896-0ce572984e72.json"
    )
