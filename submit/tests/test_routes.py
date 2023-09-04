from bs4 import BeautifulSoup


def test_index_page(flask_test_client):
    response = flask_test_client.get("/")
    assert response.status_code == 302
    assert response.location == "/upload"


def test_upload_page(flask_test_client):
    response = flask_test_client.get("/upload")
    assert response.status_code == 200


def test_unauthenticated_upload(unauthenticated_flask_test_client):
    response = unauthenticated_flask_test_client.get("/")
    assert response.status_code == 200
    assert b"Sign in" in response.data


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


def test_upload_xlsx_uncaught_validation_error(requests_mock, example_pre_ingest_data_file, flask_test_client):
    requests_mock.post(
        "http://data-store/ingest",
        content=b'"detail": "Uncaught workbook validation failure", "status": 500, "title": "Bad Request"',
        status_code=500,
    )
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_pre_ingest_data_file})
    page_html = BeautifulSoup(response.data)
    service_email = flask_test_client.application.config["CONTACT_EMAIL"]

    assert response.status_code == 200
    assert (
        f'Contact us at <a href="mailto:{service_email}">{service_email}</a>. Do not '
        "send your return or any attachments using the help email."
    ) in str(page_html)


def test_upload_wrong_format(flask_test_client, example_ingest_wrong_format):
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_ingest_wrong_format})
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert "Unexpected file format:" in str(page_html)
