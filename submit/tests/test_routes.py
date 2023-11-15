from datetime import datetime, timedelta

from bs4 import BeautifulSoup

from config import Config


def test_index_page(flask_test_client):
    response = flask_test_client.get("/")
    assert response.status_code == 302
    assert response.location == "/upload"


def test_upload_page(flask_test_client):
    response = flask_test_client.get("/upload")
    assert response.status_code == 200
    assert b"Upload your data return" in response.data
    assert (
        b"When you upload your return, we\xe2\x80\x99ll check it for missing data and formatting errors."
        in response.data
    )


def test_upload_xlsx_successful(flask_test_client, example_pre_ingest_data_file, mocker, requests_mock):
    send_confirmation_emails = mocker.patch("app.main.routes.send_confirmation_emails")
    requests_mock.post(
        "http://data-store/ingest",
        json={"detail": "Spreadsheet successfully uploaded", "status": 200, "title": "success", "loaded": True},
        status_code=200,
    )
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_pre_ingest_data_file})
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert "Return submitted" in str(page_html)
    assert "We’ll do this using the email you’ve provided." in str(page_html)
    assert "Service desk" in str(page_html)
    assert "Arrange a callback" in str(page_html)
    send_confirmation_emails.assert_called_once()


def test_upload_xlsx_successful_no_load(flask_test_client, example_pre_ingest_data_file, requests_mock):
    """Returns 500 if ingest does not load data to DB."""
    requests_mock.post(
        "http://data-store/ingest",
        json={"detail": "Spreadsheet successfully uploaded", "status": 200, "title": "success", "do_load": False},
        status_code=200,
    )
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_pre_ingest_data_file})
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
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_pre_ingest_data_file})
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
                    "cell": "A1",
                    "description": "You are missing project locations. Please enter a project location.",
                },
                {
                    "sheet": "Tab2",
                    "section": "section2",
                    "cell": "B2-Y2",
                    "description": "Start date in an incorrect format. Please enter a dates in the format 'Dec-22'",
                },
            ],
        },
        status_code=400,
    )
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_pre_ingest_data_file})
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
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_pre_ingest_data_file})
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
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_pre_ingest_data_file})
    page_html = BeautifulSoup(response.data)

    assert response.status_code == 500
    assert "Sorry, there is a problem with the service" in str(page_html)
    assert "Ingest failed for an unknown reason - failure_id=12345" in caplog.text


def test_upload_wrong_format(flask_test_client, example_ingest_wrong_format):
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_ingest_wrong_format})
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert "The selected file must be an XLSX" in str(page_html)


def test_upload_no_file(flask_test_client, example_ingest_wrong_format):
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": None})
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert "Select your returns template" in str(page_html)


def test_unauthenticated_upload(unauthenticated_flask_test_client):
    response = unauthenticated_flask_test_client.get("/upload")
    # Assert redirect to /login
    assert response.status_code == 302
    assert response.location == "/login"


def test_not_signed_in(unauthenticated_flask_test_client):
    response = unauthenticated_flask_test_client.get("/")
    assert response.status_code == 302
    assert response.location == "/login"


def test_unauthorised_user(flask_test_client, mocker):
    """Tests scenario for an authenticated user that is unauthorized to submit."""
    # mock unauthorised user
    mocker.patch(
        "fsd_utils.authentication.decorators._check_access_token",
        return_value={
            "accountId": "test-user",
            "roles": [Config.TF_SUBMITTER_ROLE],
            "email": "madeup@madeup.gov.uk",
        },
    )

    response = flask_test_client.get("/upload")
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

    response = flask_test_client.get("/upload")
    assert response.status_code == 302
    assert response.location == "authenticator/service/user?roles_required=TF_MONITORING_RETURN_SUBMITTER"


def test_future_deadline_view_not_shown(flask_test_client):
    """Do not display the deadline notification if over 7 days away."""
    # Set submit deadline to 10 days in the future
    submit_deadline = datetime.now() + timedelta(days=8)
    Config.SUBMIT_DEADLINE = submit_deadline.strftime("%d/%m/%Y")

    response = flask_test_client.get("/upload")

    # The normal banner should be displayed if submission is not overdue
    assert b"govuk-notification-banner__heading" not in response.data
    assert b"Your data return is due in 8 days." not in response.data


def test_future_deadline_view_shown(flask_test_client):
    """Display the deadline notification if 7 or fewer days away."""
    # Set submit deadline to 10 days in the future
    submit_deadline = datetime.now() + timedelta(days=6)
    Config.SUBMIT_DEADLINE = submit_deadline.strftime("%d/%m/%Y")

    response = flask_test_client.get("/upload")

    # The normal banner should be displayed if submission is not overdue
    assert b"govuk-notification-banner__heading" in response.data
    assert b"Your data return is due in 6 days." in response.data


def test_overdue_deadline_view(flask_test_client):
    # Set submit deadline to 10 days in the past
    submit_deadline = datetime.now() - timedelta(days=10)
    Config.SUBMIT_DEADLINE = submit_deadline.strftime("%d/%m/%Y")

    response = flask_test_client.get("/upload")

    # The red version of the banner should be displayed if submission is overdue
    assert b"overdue-notification-banner" in response.data

    assert b"Your data return is 10 days late." in response.data
    assert b"Submit your return as soon as possible to avoid delays in your funding." in response.data


def test_single_local_authorities_view(flask_test_client, mocker):
    # Ensure contents of tuples are displayed correctly on front end
    mocker.patch("app.main.routes.check_authorised", return_value=(("Council 1",), ("test",)))

    response = flask_test_client.get("/upload")

    assert b"Council 1" in response.data
    assert b"('Council 1')" not in response.data


def test_multiple_local_authorities_view(flask_test_client, mocker):
    mocker.patch(
        "app.main.routes.check_authorised",
        return_value=(
            (
                "Council 1",
                "Council 2",
                "Council 3",
            ),
            ("test",),
        ),
    )

    response = flask_test_client.get("/upload")

    assert b"Council 1, Council 2, Council 3" in response.data
    assert b"('Council 1', 'Council 2', 'Council 3')" not in response.data
