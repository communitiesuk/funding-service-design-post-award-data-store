from datetime import datetime
from unittest.mock import patch

import pytest
from bs4 import BeautifulSoup
from flask import url_for


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

    page = BeautifulSoup(response.text, "html.parser")
    assert page.select_one(".govuk-back-link") is None


def test_process_async_download_call(find_test_client, mocked_routes_trigger_async_download):
    """Test that the download route calls the process_async_download function with the correct parameters,
    including the user email address."""

    find_test_client.post("/download", data={"file_format": "xlsx"})
    assert mocked_routes_trigger_async_download.called
    assert mocked_routes_trigger_async_download.call_args.args[0] == {
        "file_format": "xlsx",
        "email_address": "user@wigan.gov.uk",
    }


def test_async_download_redirect_OK(find_test_client, mocked_routes_trigger_async_download):
    """Test that the download route redirects to the request-received page after a successful download request."""

    response = find_test_client.post("/download", data={"file_format": "xlsx"})
    assert response.status_code == 302  # redirect to request-received page
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    expected_location = url_for("find.request_received", _external=False)
    assert response.headers["Location"] == expected_location


def test_async_download_redirect_error(find_test_client, mocker):
    """Test that the download route does not redirect, but renders the 500 error page when
    the download request fails."""
    mocker.patch("find.main.routes.trigger_async_download", side_effect=ValueError("I can't talk to Redis"))
    response = find_test_client.post("/download", data={"file_format": "xlsx"})
    assert response.status_code == 500
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert b"Sorry, there is a problem with the service" in response.data
    assert b"Try again later." in response.data


@pytest.mark.parametrize(
    "fileformat",
    ["foobar", ""],
)
def test_download_post_bad_file_formats(find_test_client, mock_download_checkbox_data, fileformat):
    response = find_test_client.post("/download", data={"file_format": fileformat})
    assert response.headers["Content-Type"] == "text/html; charset=utf-8"
    assert response.status_code == 200

    soup = BeautifulSoup(response.text, "html.parser")
    error_summary = soup.find("p", {"class": "govuk-error-message"})
    assert error_summary is not None
    assert "Select a file format" in error_summary.text


def test_download_fails_csrf(find_test_client):
    find_test_client.application.config["WTF_CSRF_ENABLED"] = True
    response = find_test_client.post("/download", data={"file_format": "json"})
    assert response.status_code == 302


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

    page = BeautifulSoup(response.text, "html.parser")
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
    assert (
        response.location
        == "authenticator/sessions/sign-out?return_app=post-award-frontend&return_path=%2Frequest-received"
    )


def test_download_file_exist(find_test_client):
    file_metadata = {"created_at": "06 July 2024", "file_format": "Microsoft Excel spreadsheet", "file_size": "1 MB"}

    with patch("find.main.routes.get_find_download_file_metadata", return_value=file_metadata):
        response = find_test_client.get(
            "/retrieve-download/fund-monitoring-data-2024-07-05-11:18:45-e4c77136-18ca-4ba3-9896-0ce572984e72.json"
        )

    assert response.status_code == 200
    page = BeautifulSoup(response.text, "html.parser")
    download_button = page.select_one("button#download")
    assert download_button is not None


def test_file_not_found(find_test_client):
    with patch("find.main.routes.get_find_download_file_metadata", side_effect=FileNotFoundError()):
        response = find_test_client.get(
            "/retrieve-download/fund-monitoring-data-2024-07-05-11:18:45-e4c77136-18ca-4ba3-9896-0ce572984e72.json"
        )

    assert response.status_code == 200
    page = BeautifulSoup(response.text, "html.parser")
    download_button = page.select_one("button#download")
    assert download_button is None
    assert b"Your link to download data has expired" in response.data


def test_presigned_url(
    find_test_client,
):
    presigned_url = "https://example/presigned-url"
    file_metadata = {"created_at": "06 July 2024", "file_format": "Microsoft Excel spreadsheet", "file_size": "1 MB"}
    with (
        patch("find.main.routes.get_find_download_file_metadata", return_value=file_metadata),
        patch("find.main.routes.get_presigned_url", return_value=presigned_url),
    ):
        response = find_test_client.post(
            "/retrieve-download/fund-monitoring-data-2024-07-05-11:18:45-e4c77136-18ca-4ba3-9896-0ce572984e72.json"
        )

    assert response.status_code == 302
    assert response.location == presigned_url


def test_file_not_exist(find_test_client):
    with patch("find.main.routes.get_find_download_file_metadata", side_effect=FileNotFoundError()):
        response = find_test_client.post(
            "/retrieve-download/fund-monitoring-data-2024-07-05-11:18:45-e4c77136-18ca-4ba3-9896-0ce572984e72.json"
        )

    assert response.status_code == 302
    assert (
        response.location
        == "/retrieve-download/fund-monitoring-data-2024-07-05-11:18:45-e4c77136-18ca-4ba3-9896-0ce572984e72.json"
    )
