import io

import pytest
from bs4 import BeautifulSoup
from werkzeug.datastructures import FileStorage

from app.main.fund import TOWNS_FUND_APP_CONFIG

TEST_FUND_CODE = "TF"
TEST_ROUND = 4


def test_index_page(flask_test_client):
    response = flask_test_client.get("/")
    assert response.status_code == 302
    assert response.location == "/dashboard"


def test_select_fund_page_with_tf_role(flask_test_client):
    response = flask_test_client.get("/dashboard")
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert '<a class="govuk-heading-m govuk-link--no-visited-state" href="/upload/TF/4"> Towns Fund</a>' in str(
        page_html
    )
    assert '<a class="govuk-heading-m govuk-link--no-visited-state" href="/upload/PF/1"> Pathfinders</a>' not in str(
        page_html
    )


def test_select_fund_page_with_pf_role(flask_test_client, mocked_pf_auth):
    response = flask_test_client.get("/dashboard")
    assert response.status_code == 200
    page_html = BeautifulSoup(response.data)
    assert (
        '<a class="govuk-heading-m govuk-link--no-visited-state" href="/upload/TF/4"> Towns Fund</a>' not in page_html
    )
    assert '<a class="govuk-heading-m govuk-link--no-visited-state" href="/upload/PF/1"> Pathfinders</a>' in str(
        page_html
    )


def test_select_fund_page_with_tf_and_pf_roles(flask_test_client, mocked_pf_and_tf_auth):
    response = flask_test_client.get("/dashboard")
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert '<a class="govuk-heading-m govuk-link--no-visited-state" href="/upload/TF/4"> Towns Fund</a>' in str(
        page_html
    )
    assert '<a class="govuk-heading-m govuk-link--no-visited-state" href="/upload/PF/1"> Pathfinders</a>' in str(
        page_html
    )


def test_towns_fund_role(flask_test_client, mocked_auth):
    response = flask_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    # Assert the Towns Fund view is displayed
    assert "Towns Fund" in str(page_html)


def test_pathfinders_role(flask_test_client, mocked_pf_auth):
    response = flask_test_client.get("/upload/PF/1")
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    # Assert the Pathfinders view is displayed instead of Towns Fund
    assert "Pathfinders" in str(page_html)


def test_upload_page(flask_test_client):
    response = flask_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert "Upload your data return" in str(page_html)
    assert "When you upload your return, we’ll check it for missing data and formatting errors." in str(page_html)


def test_upload_xlsx_successful(flask_test_client, example_pre_ingest_data_file, mocker, requests_mock):
    send_confirmation_emails = mocker.patch("app.main.routes.send_confirmation_emails")
    requests_mock.post(
        "http://data-store/ingest",
        json={"detail": "Spreadsheet successfully uploaded", "status": 200, "title": "success", "loaded": True},
        status_code=200,
    )
    response = flask_test_client.post(
        f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": example_pre_ingest_data_file}
    )
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert "Return submitted" in str(page_html)
    assert "We’ll do this using the email you’ve provided." in str(page_html)
    assert "Service desk" in str(page_html)
    assert "Arrange a callback" in str(page_html)
    send_confirmation_emails.assert_called_once()


def test_upload_xlsx_successful_correct_filename(flask_test_client, mocker, requests_mock):
    filename = "example.xlsx"
    filebytes = b"example file contents"
    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    file = FileStorage(io.BytesIO(filebytes), filename=filename, content_type=content_type)

    mocker.patch("app.main.routes.send_confirmation_emails")
    request = requests_mock.post(
        "http://data-store/ingest",
        json={"detail": "Spreadsheet successfully uploaded", "status": 200, "title": "success", "loaded": True},
        status_code=200,
    )
    flask_test_client.post(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": file})
    last_request = request.last_request.text
    assert f'filename="{file.filename}"' in last_request


def test_upload_xlsx_successful_no_load(flask_test_client, example_pre_ingest_data_file, requests_mock):
    """Returns 500 if ingest does not load data to DB."""
    requests_mock.post(
        "http://data-store/ingest",
        json={"detail": "Spreadsheet successfully uploaded", "status": 200, "title": "success", "do_load": False},
        status_code=200,
    )
    response = flask_test_client.post(
        f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": example_pre_ingest_data_file}
    )
    assert response.status_code == 500


def test_upload_xlsx_prevalidation_errors(requests_mock, example_pre_ingest_data_file, flask_test_client):
    requests_mock.post(
        "http://data-store/ingest",
        json={
            "detail": "Workbook validation failed",
            "status": 400,
            "title": "Bad Request",
            "pre_transformation_errors": ["The selected file must be an Excel file"],
        },
        status_code=400,
    )
    response = flask_test_client.post(
        f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": example_pre_ingest_data_file}
    )
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert "The selected file must be an Excel file" in str(page_html)


def test_upload_xlsx_validation_errors(requests_mock, example_pre_ingest_data_file, flask_test_client):
    requests_mock.post(
        "http://data-store/ingest",
        json={
            "detail": "Workbook validation failed",
            "status": 400,
            "title": "Bad Request",
            "pre_transformation_errors": [],
            "validation_errors": [
                {
                    "sheet": "Project Admin",
                    "section": "section1",
                    "cell_index": "A1",
                    "description": "You are missing project locations. Please enter a project location.",
                    "error_type": "NonNullableConstraintFailure",
                },
                {
                    "sheet": "Tab2",
                    "section": "section2",
                    "cell_index": "B2-Y2",
                    "description": "Start date in an incorrect format. Please enter a dates in the format 'Dec-22'",
                    "error_type": "TownsFundRoundFourValidationFailure",
                },
            ],
        },
        status_code=400,
    )
    response = flask_test_client.post(
        f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": example_pre_ingest_data_file}
    )
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert "There are errors in your return" in str(page_html)
    assert "Project admin" in str(page_html)
    assert "You are missing project locations. Please enter a project location." in str(page_html)
    assert "Start date in an incorrect format. Please enter a dates in the format 'Dec-22'" in str(page_html)


def test_upload_ingest_generic_bad_request(requests_mock, example_pre_ingest_data_file, flask_test_client):
    requests_mock.post(
        "http://data-store/ingest",
        json={"detail": "Wrong file format", "status": 400, "title": "Bad Request", "type": "about:blank"},
        status_code=400,
    )
    response = flask_test_client.post(
        f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": example_pre_ingest_data_file}
    )
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 500
    assert "Sorry, there is a problem with the service" in str(page_html)
    assert "Try again later." in str(page_html)


def test_upload_xlsx_uncaught_validation_error(requests_mock, example_pre_ingest_data_file, flask_test_client, caplog):
    requests_mock.post(
        "http://data-store/ingest",
        json={
            "detail": "Uncaught workbook validation failure",
            "id": "12345",
            "status": 500,
            "title": "Bad Request",
        },
        status_code=500,
    )
    response = flask_test_client.post(
        f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": example_pre_ingest_data_file}
    )
    page_html = BeautifulSoup(response.data)

    assert response.status_code == 500
    assert "Sorry, there is a problem with the service" in str(page_html)
    assert "Ingest failed for an unknown reason - failure_id=12345" in caplog.text


def test_upload_wrong_format(flask_test_client, example_ingest_wrong_format):
    response = flask_test_client.post(
        f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": example_ingest_wrong_format}
    )
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert "The selected file must be an XLSX" in str(page_html)


def test_upload_no_file(flask_test_client, example_ingest_wrong_format):
    response = flask_test_client.post(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": None})
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert "Select your returns template" in str(page_html)


def test_unauthenticated_upload(unauthenticated_flask_test_client):
    response = unauthenticated_flask_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")
    # Assert redirect to /login
    assert response.status_code == 302
    assert response.location == "/login"


def test_not_signed_in(unauthenticated_flask_test_client):
    response = unauthenticated_flask_test_client.get("/")
    assert response.status_code == 302
    assert response.location == "/login"


def test_unauthorised_user_without_valid_email_cannot_access_upload(flask_test_client, mocker):
    """Tests scenario for an authenticated user that is unauthorized to submit."""
    # mock unauthorised user
    mocker.patch(
        "fsd_utils.authentication.decorators._check_access_token",
        return_value={
            "accountId": "test-user",
            "roles": [TOWNS_FUND_APP_CONFIG.user_role],
            "email": "madeup@madeup.gov.uk",
        },
    )

    response = flask_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")
    assert response.status_code == 401
    assert b"Sorry, you don't currently have permission to access this service" in response.data


def test_unauthorised_user_without_valid_role_cannot_access_upload(flask_test_client, mocker):
    """Tests scenario for an authenticated user that is unauthorized to submit."""
    # mock unauthorised user
    mocker.patch(
        "fsd_utils.authentication.decorators._check_access_token",
        return_value={
            "accountId": "test-user",
            "roles": ["INVALID_ROLE"],
            "email": "valid_email@communities.gov.uk",
        },
    )

    response = flask_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")
    assert response.status_code == 401
    assert b"Sorry, you don't currently have permission to access this service" in response.data


def test_user_without_role_cannot_access_upload(flask_test_client, mocker):
    """Tests scenario for an authenticated user that is does not have the required role."""
    # mock user without role
    mocker.patch(
        "fsd_utils.authentication.decorators._check_access_token",
        return_value={
            "accountId": "test-user",
            "roles": [],
            "email": "user@wigan.gov.uk",
        },
    )

    response = flask_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")
    assert response.status_code == 401
    assert b"Sorry, you don't currently have permission to access this service" in response.data


@pytest.fixture
def inactive_fund():
    """Sets the towns fund config as inactive"""
    TOWNS_FUND_APP_CONFIG.active = False
    yield
    TOWNS_FUND_APP_CONFIG.active = True


def test_inactive_fund(flask_test_client, inactive_fund):
    """
    GIVEN a user is accessing /upload
    WHEN the fund they are permitted to submit for is inactive
    THEN the user should be redirected to the 401 unauthorised error page
    """
    response = flask_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")
    assert response.status_code == 401
    assert b"Sorry, you don't currently have permission to access this service" in response.data


def test_future_deadline_view_not_shown(flask_test_client, mocker):
    """Do not display the deadline notification if over 7 days away."""
    mocker.patch("app.main.routes.days_between_dates", return_value=8)

    response = flask_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")

    # The normal banner should be displayed if submission is not overdue
    assert b"govuk-notification-banner__heading" not in response.data
    assert b"Your data return is due in 8 days." not in response.data


def test_future_deadline_view_shown(flask_test_client, mocker):
    """Display the deadline notification if 7 or fewer days away."""
    mocker.patch("app.main.routes.days_between_dates", return_value=6)

    response = flask_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")

    # The normal banner should be displayed if submission is not overdue
    assert b"govuk-notification-banner__heading" in response.data
    assert b"Your data return is due in 6 days." in response.data


def test_overdue_deadline_view(flask_test_client, mocker):
    # Set submit deadline to 10 days in the past
    mocker.patch("app.main.routes.days_between_dates", return_value=-10)

    response = flask_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")

    # The red version of the banner should be displayed if submission is overdue
    assert b"overdue-notification-banner" in response.data

    assert b"Your data return is 10 days late." in response.data
    assert b"Submit your return as soon as possible to avoid delays in your funding." in response.data


def test_single_local_authorities_view(flask_test_client):
    response = flask_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")

    assert b"Wigan Council" in response.data
    assert b"('Wigan Council')" not in response.data


def test_multiple_local_authorities_view(flask_test_client, mocker):
    mocker.patch(
        "fsd_utils.authentication.decorators._check_access_token",
        return_value={
            "accountId": "test-user",
            "roles": [TOWNS_FUND_APP_CONFIG.user_role],
            # in config.unit_test.py this email is set to map to the below councils
            "email": "multiple_orgs@contractor.com",
        },
    )

    response = flask_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")

    assert b"Rotherham Metropolitan Borough Council, Another Council" in response.data
    assert b"('Rotherham Metropolitan Borough Council', 'Another Council')" not in response.data


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
