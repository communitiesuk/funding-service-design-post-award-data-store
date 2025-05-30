import io

import pytest
from bs4 import BeautifulSoup
from werkzeug.datastructures import FileStorage

from submit.main.fund import PATHFINDERS_APP_CONFIG, TOWNS_FUND_APP_CONFIG

TEST_FUND_CODE = "TF"
TEST_ROUND = 4


def test_index_page(submit_test_client):
    response = submit_test_client.get("/")
    assert response.status_code == 302
    assert response.location == "/dashboard"


def test_select_fund_page_with_tf_role(submit_test_client, mocker):
    mocker.patch.object(TOWNS_FUND_APP_CONFIG, "active", True)
    response = submit_test_client.get("/dashboard")
    page_html = BeautifulSoup(response.data, "html.parser")
    assert response.status_code == 200
    assert '<a class="govuk-heading-m govuk-link--no-visited-state" href="/upload/TF/7" id="TF"> Towns Fund</a>' in str(
        page_html
    )
    assert (
        '<a class="govuk-heading-m govuk-link--no-visited-state" href="/upload/PF/1" id="PF"> Pathfinders</a>'
        not in str(page_html)
    )


@pytest.mark.xfail(reason="Pathfinders is not active")
def test_select_fund_page_with_pf_role(submit_test_client, mocked_pf_auth):
    response = submit_test_client.get("/dashboard")
    assert response.status_code == 200
    page_html = BeautifulSoup(response.data, "html.parser")
    assert (
        '<a class="govuk-heading-m govuk-link--no-visited-state" href="/upload/TF/5" id="TF"> Towns Fund</a>'
        not in page_html
    )
    assert (
        '<a class="govuk-heading-m govuk-link--no-visited-state" href="/upload/PF/1" id="PF"> Pathfinders</a>'
        in str(page_html)
    )


@pytest.mark.xfail(reason="Pathfinders is not active")
def test_select_fund_page_with_tf_and_pf_roles(submit_test_client, mocked_pf_and_tf_auth, monkeypatch):
    monkeypatch.setattr(TOWNS_FUND_APP_CONFIG, "active", True)
    response = submit_test_client.get("/dashboard")
    page_html = BeautifulSoup(response.data, "html.parser")
    assert response.status_code == 200
    assert '<a class="govuk-heading-m govuk-link--no-visited-state" href="/upload/TF/5" id="TF"> Towns Fund</a>' in str(
        page_html
    )
    assert (
        '<a class="govuk-heading-m govuk-link--no-visited-state" href="/upload/PF/1" id="PF"> Pathfinders</a>'
        in str(page_html)
    )


def test_inactive_fund_not_accessible_on_dashboard(submit_test_client, mocked_pf_and_tf_auth, monkeypatch):
    monkeypatch.setattr(PATHFINDERS_APP_CONFIG, "active", True)
    monkeypatch.setattr(TOWNS_FUND_APP_CONFIG, "active", False)
    response = submit_test_client.get("/dashboard")
    page_html = BeautifulSoup(response.data, "html.parser")
    assert response.status_code == 200
    assert "Towns Fund" not in str(page_html)


def test_inactive_fund_not_accessible_on_route(submit_test_client, mocked_pf_and_tf_auth, monkeypatch):
    monkeypatch.setattr(TOWNS_FUND_APP_CONFIG, "active", False)
    response = submit_test_client.get(
        f"/upload/{TOWNS_FUND_APP_CONFIG.fund_code}/{TOWNS_FUND_APP_CONFIG.current_reporting_round}"
    )
    assert response.status_code == 401


def test_towns_fund_role(submit_test_client, mocked_auth, monkeypatch):
    monkeypatch.setattr(TOWNS_FUND_APP_CONFIG, "active", True)
    response = submit_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")
    page_html = BeautifulSoup(response.data, "html.parser")
    assert response.status_code == 200
    # Assert the Towns Fund view is displayed
    assert "Towns Fund" in str(page_html)


def test_pathfinders_role(submit_test_client, mocked_pf_auth, monkeypatch):
    monkeypatch.setattr(PATHFINDERS_APP_CONFIG, "active", True)
    response = submit_test_client.get("/upload/PF/1")
    page_html = BeautifulSoup(response.data, "html.parser")
    assert response.status_code == 200
    # Assert the Pathfinders view is displayed instead of Towns Fund
    assert "Pathfinders" in str(page_html)


def test_upload_page(submit_test_client, mocker):
    mocker.patch.object(TOWNS_FUND_APP_CONFIG, "active", True)
    response = submit_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")
    page_html = BeautifulSoup(response.data, "html.parser")
    assert response.status_code == 200
    assert "Upload your data return" in str(page_html)
    assert "When you upload your return, we’ll check it for missing data and formatting errors." in str(page_html)


def test_upload_xlsx_successful(submit_test_client, example_pre_ingest_data_file, mocker):
    mocker.patch.object(TOWNS_FUND_APP_CONFIG, "active", True)
    send_la_confirmation_emails = mocker.patch("submit.main.routes.send_la_confirmation_emails")
    send_fund_confirmation_email = mocker.patch("submit.main.routes.send_fund_confirmation_email")
    mocker.patch(
        "submit.main.data_requests.ingest",
        return_value=(
            {"detail": "Spreadsheet successfully uploaded", "status": 200, "title": "success", "loaded": True},
            200,
        ),
    )
    response = submit_test_client.post(
        f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": example_pre_ingest_data_file}
    )
    page_html = BeautifulSoup(response.data, "html.parser")
    assert response.status_code == 200
    assert "Return submitted" in str(page_html)
    assert "We’ll do this using the email you’ve provided." in str(page_html)
    assert "Service desk" in str(page_html)
    assert "Arrange a callback" in str(page_html)
    send_la_confirmation_emails.assert_called_once()
    send_fund_confirmation_email.assert_called_once()


def test_upload_xlsx_successful_correct_filename(submit_test_client, mocker):
    mocker.patch.object(TOWNS_FUND_APP_CONFIG, "active", True)
    filename = "example.xlsx"
    filebytes = b"example file contents"
    content_type = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    file = FileStorage(io.BytesIO(filebytes), filename=filename, content_type=content_type)

    mocker.patch("submit.main.routes.send_la_confirmation_emails")
    mocker.patch("submit.main.routes.send_fund_confirmation_email")
    mock_post_ingest = mocker.patch(
        "submit.main.data_requests.ingest",
        return_value=(
            {"detail": "Spreadsheet successfully uploaded", "status": 200, "title": "success", "loaded": True},
            200,
        ),
    )

    submit_test_client.post(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": file})
    assert mock_post_ingest.call_args_list[0].kwargs["excel_file"].filename == file.filename


def test_upload_xlsx_successful_no_load(submit_test_client, example_pre_ingest_data_file, mocker):
    """Returns 500 if ingest does not load data to DB."""
    mocker.patch.object(TOWNS_FUND_APP_CONFIG, "active", True)
    mocker.patch(
        "submit.main.data_requests.ingest",
        return_value=(
            {"detail": "Spreadsheet successfully uploaded", "status": 200, "title": "success", "do_load": False},
            200,
        ),
    )
    response = submit_test_client.post(
        f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": example_pre_ingest_data_file}
    )
    assert response.status_code == 500


def test_upload_xlsx_prevalidation_errors(example_pre_ingest_data_file, submit_test_client, mocker):
    mocker.patch.object(TOWNS_FUND_APP_CONFIG, "active", True)
    mocker.patch(
        "submit.main.data_requests.ingest",
        return_value=(
            {
                "detail": "Workbook validation failed",
                "status": 400,
                "title": "Bad Request",
                "pre_transformation_errors": ["The selected file must be an Excel file"],
            },
            400,
        ),
    )
    response = submit_test_client.post(
        f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": example_pre_ingest_data_file}
    )
    page_html = BeautifulSoup(response.data, "html.parser")
    assert response.status_code == 200
    assert "The selected file must be an Excel file" in str(page_html)


def test_upload_xlsx_validation_errors(example_pre_ingest_data_file, submit_test_client, mocker):
    mocker.patch.object(TOWNS_FUND_APP_CONFIG, "active", True)
    mocker.patch(
        "submit.main.data_requests.ingest",
        return_value=(
            {
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
            400,
        ),
    )
    response = submit_test_client.post(
        f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": example_pre_ingest_data_file}
    )
    page_html = BeautifulSoup(response.data, "html.parser")
    assert response.status_code == 200
    assert "There are errors in your return" in str(page_html)
    assert "Project admin" in str(page_html)
    assert "You are missing project locations. Please enter a project location." in str(page_html)
    assert "Start date in an incorrect format. Please enter a dates in the format 'Dec-22'" in str(page_html)


def test_upload_ingest_generic_bad_request(example_pre_ingest_data_file, submit_test_client, mocker):
    mocker.patch.object(TOWNS_FUND_APP_CONFIG, "active", True)
    mocker.patch(
        "submit.main.data_requests.ingest",
        return_value=(
            {"detail": "Wrong file format", "status": 400, "title": "Bad Request", "type": "about:blank"},
            400,
        ),
    )
    response = submit_test_client.post(
        f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": example_pre_ingest_data_file}
    )
    page_html = BeautifulSoup(response.data, "html.parser")
    assert response.status_code == 500
    assert "Sorry, there is a problem with the service" in str(page_html)
    assert "Try again later." in str(page_html)


def test_upload_xlsx_uncaught_validation_error(example_pre_ingest_data_file, submit_test_client, caplog, mocker):
    mocker.patch.object(TOWNS_FUND_APP_CONFIG, "active", True)
    mocker.patch(
        "submit.main.data_requests.ingest",
        return_value=(
            {
                "detail": "Uncaught workbook validation failure",
                "id": "12345",
                "status": 500,
                "title": "Bad Request",
            },
            500,
        ),
    )
    response = submit_test_client.post(
        f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": example_pre_ingest_data_file}
    )
    page_html = BeautifulSoup(response.data, "html.parser")

    assert response.status_code == 500
    assert "Sorry, there is a problem with the service" in str(page_html)

    # caplog doesn't format log messages so let's make sure it has the string+data we expect
    assert "Ingest failed for an unknown reason - failure_id={failure_id}" in caplog.records[1].message
    assert caplog.records[1].failure_id == "12345"


def test_upload_wrong_format(submit_test_client, example_ingest_wrong_format, mocker):
    mocker.patch.object(TOWNS_FUND_APP_CONFIG, "active", True)
    response = submit_test_client.post(
        f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": example_ingest_wrong_format}
    )
    page_html = BeautifulSoup(response.data, "html.parser")
    assert response.status_code == 200
    assert "The selected file must be an XLSX" in str(page_html)


def test_upload_no_file(submit_test_client, example_ingest_wrong_format, mocker):
    mocker.patch.object(TOWNS_FUND_APP_CONFIG, "active", True)
    response = submit_test_client.post(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}", data={"ingest_spreadsheet": None})
    page_html = BeautifulSoup(response.data, "html.parser")
    assert response.status_code == 200
    assert "Select your returns template" in str(page_html)


def test_unauthenticated_upload(unauthenticated_submit_test_client):
    response = unauthenticated_submit_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")
    # Assert redirect to authenticator
    assert response.status_code == 302
    assert response.location == (
        "http://authenticator.communities.gov.localhost:4004"
        "/sessions/sign-out?return_app=post-award-submit&return_path=%2Fupload%2FTF%2F4"
    )


def test_not_signed_in(unauthenticated_submit_test_client):
    response = unauthenticated_submit_test_client.get("/")
    assert response.status_code == 302
    assert response.location == "/login"


def test_unauthorised_user_without_valid_email_cannot_access_upload(submit_test_client, mocker):
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

    response = submit_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")
    assert response.status_code == 401
    assert b"Sorry, you don't currently have permission to access this service" in response.data


def test_unauthorised_user_without_valid_role_cannot_access_upload(submit_test_client, mocker):
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

    response = submit_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")
    assert response.status_code == 401
    assert b"Sorry, you don't currently have permission to access this service" in response.data


def test_user_without_role_cannot_access_upload(submit_test_client, mocker):
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

    response = submit_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")
    assert response.status_code == 401
    assert b"Sorry, you don't currently have permission to access this service" in response.data


@pytest.fixture
def inactive_fund():
    """Sets the towns fund config as inactive"""
    TOWNS_FUND_APP_CONFIG.active = False
    yield
    TOWNS_FUND_APP_CONFIG.active = True


def test_inactive_fund(submit_test_client, inactive_fund):
    """
    GIVEN a user is accessing /upload
    WHEN the fund they are permitted to submit for is inactive
    THEN the user should be redirected to the 401 unauthorised error page
    """
    response = submit_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")
    assert response.status_code == 401
    assert b"Sorry, you don't currently have permission to access this service" in response.data


def test_future_deadline_view_not_shown(submit_test_client, mocker):
    """Do not display the deadline notification if over 7 days away."""
    mocker.patch("submit.main.routes.days_between_dates", return_value=8)

    response = submit_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")

    # The normal banner should be displayed if submission is not overdue
    assert b"govuk-notification-banner__heading" not in response.data
    assert b"Your data return is due in 8 days." not in response.data


def test_future_deadline_view_shown(submit_test_client, mocker):
    """Display the deadline notification if 7 or fewer days away."""
    mocker.patch("submit.main.routes.days_between_dates", return_value=6)

    response = submit_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")

    # The normal banner should be displayed if submission is not overdue
    assert b"govuk-notification-banner__heading" in response.data
    assert b"Your data return is due in 6 days." in response.data


def test_overdue_deadline_view(submit_test_client, mocker):
    # Set submit deadline to 10 days in the past
    mocker.patch("submit.main.routes.days_between_dates", return_value=-10)

    response = submit_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")

    # The red version of the banner should be displayed if submission is overdue
    assert b"overdue-notification-banner" in response.data

    assert b"Your data return is 10 days late." in response.data
    assert b"Submit your return as soon as possible to avoid delays in your funding." in response.data


def test_single_local_authorities_view(submit_test_client):
    response = submit_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")

    assert b"Wigan Council" in response.data
    assert b"('Wigan Council')" not in response.data


def test_multiple_local_authorities_view(submit_test_client, mocker):
    mocker.patch(
        "fsd_utils.authentication.decorators._check_access_token",
        return_value={
            "accountId": "test-user",
            "roles": [TOWNS_FUND_APP_CONFIG.user_role],
            # in config.unit_test.py this email is set to map to the below councils
            "email": "multiple_orgs@contractor.com",
        },
    )

    response = submit_test_client.get(f"/upload/{TEST_FUND_CODE}/{TEST_ROUND}")

    assert b"Rotherham Metropolitan Borough Council, Another Council" in response.data
    assert b"('Rotherham Metropolitan Borough Council', 'Another Council')" not in response.data


def test_known_http_error_redirect(submit_test_client):
    # induce a known error
    response = submit_test_client.get("/unknown-page")

    assert response.status_code == 404
    # 404.html template should be rendered
    assert b"Page not found" in response.data
    assert b"If you typed the web address, check it is correct." in response.data


def test_http_error_unknown_redirects(submit_test_client):
    # induce a 405 error
    response = submit_test_client.post("/?g=obj_app_upfile")

    assert response.status_code == 405
    # generic error template should be rendered
    assert b"Sorry, there is a problem with the service" in response.data
    assert b"Try again later." in response.data
