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
    assert b"You are uploading for" in response.data
    assert b"Wigan Metropolitan Borough Council" in response.data


def test_upload_xlsx_successful(requests_mock, example_pre_ingest_data_file, flask_test_client):
    requests_mock.post(
        "http://data-store/ingest",
        content=b"{"
        b'    "detail": "Spreadsheet successfully uploaded",'
        b'    "status": 200,'
        b'    "title": "success",'
        b'    "validation_errors": {'
        b'        "TabErrors": {}'
        b"    }"
        b"}",
        status_code=200,
    )
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_pre_ingest_data_file})
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert "Return submitted" in str(page_html)
    assert "We will only contact you using the email you’ve provided, if we need to:" in str(page_html)


def test_upload_xlsx_prevalidation_errors(requests_mock, example_pre_ingest_data_file, flask_test_client):
    requests_mock.post(
        "http://data-store/ingest",
        content=(
            b"{"
            b'    "detail": "Workbook validation failed",'
            b'    "status": 400,'
            b'    "title": "Bad Request",'
            b'    "validation_errors": {'
            b'        "PreTransformationErrors": ['
            b'            "The selected file must be a CSV"'
            b"        ]"
            b"    }"
            b"}"
        ),
        status_code=400,
    )
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_pre_ingest_data_file})
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert "The selected file must be a CSV" in str(page_html)


def test_upload_xlsx_validation_errors(requests_mock, example_pre_ingest_data_file, flask_test_client):
    requests_mock.post(
        "http://data-store/ingest",
        content=(
            b"{"
            b'    "detail": "Workbook validation failed",'
            b'    "status": 400,'
            b'    "title": "Bad Request",'
            b'    "validation_errors": {'
            b'        "TabErrors": {'
            b'            "Project Admin": {'
            b'                "Place details": ["You are missing project locations. Please enter a project location.",'
            b'                                  "Another error message"]'
            b"            },"
            b'            "Programme Progress": {'
            b'                "Projects Progress Summary": ["Start date in an incorrect format. Please enter a dates '
            b"in the format 'Dec-22'\"]"
            b"            }"
            b"        }"
            b"    }"
            b"}"
        ),
        status_code=400,
    )
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_pre_ingest_data_file})
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert "There are errors in your return" in str(page_html)
    assert "Project Admin" in str(page_html)
    assert "You are missing project locations. Please enter a project location." in str(page_html)
    assert "Start date in an incorrect format. Please enter a dates in the format 'Dec-22'" in str(page_html)


def test_upload_ingest_generic_bad_request(requests_mock, example_pre_ingest_data_file, flask_test_client):
    requests_mock.post(
        "http://data-store/ingest",
        content=(
            b"{"
            b'    "detail": "Wrong file format",'
            b'    "status": 400,'
            b'    "title": "Bad Request",'
            b'    "type": "about:blank"'
            b"}"
        ),
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
        content=b'{"detail": "Uncaught workbook validation failure", '
        b'"id": "12345", '
        b'"status": 500, '
        b'"title": "Bad Request"}',
        status_code=500,
    )
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_pre_ingest_data_file})
    page_html = BeautifulSoup(response.data)
    service_email = flask_test_client.application.config["CONTACT_EMAIL"]

    assert response.status_code == 200
    assert (
        f'Your error code is [XXXX]. Please email us on <a href="mailto:{service_email}">{service_email}</a> and '
        f"include this error code, so we can investigate this issue and complete your submission"
    ) in str(page_html)
    assert "Ingest failed for an unknown reason - failure_id=12345" in caplog.text


def test_upload_wrong_format(flask_test_client, example_ingest_wrong_format):
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_ingest_wrong_format})
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert "The file selected must be an Excel file" in str(page_html)


def test_unauthenticated_upload(unauthenticated_flask_test_client):
    response = unauthenticated_flask_test_client.get("/")
    assert response.status_code == 200
    assert b"Sign in" in response.data


def test_unauthorised_user(flask_test_client, mocker):
    """Tests scenario for an authenticated user that is unauthorized to submit."""
    # mock unauthorised user
    mocker.patch(
        "fsd_utils.authentication.decorators._check_access_token",
        return_value={"accountId": "test-user", "roles": [], "email": "madeup@madeup.gov.uk"},
    )

    response = flask_test_client.get("/upload")
    assert response.status_code == 401
    assert b"Sorry, you don't currently have permission to access this service" in response.data


def test_future_deadline_view(flask_test_client):
    # Set submit deadline to 10 days in the future
    submit_deadline = datetime.now() + timedelta(days=10)
    Config.SUBMIT_DEADLINE = submit_deadline.strftime("%d/%m/%Y")

    response = flask_test_client.get("/upload")

    # The normal banner should be displayed if submission is not overdue
    assert b"overdue-notification-banner" not in response.data
    assert b"You have 10 days left to submit your April to September 2023 return" in response.data


def test_overdue_deadline_view(flask_test_client):
    # Set submit deadline to 10 days in the past
    submit_deadline = datetime.now() - timedelta(days=10)
    Config.SUBMIT_DEADLINE = submit_deadline.strftime("%d/%m/%Y")

    response = flask_test_client.get("/upload")

    # The red version of the banner should be displayed if submission is overdue
    assert b"overdue-notification-banner" in response.data

    assert b"Your data return is 10 late." in response.data
    assert b"Submit your return as soon as possible to avoid delays in your funding." in response.data
