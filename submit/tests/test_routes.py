from bs4 import BeautifulSoup


def test_index_page(flask_test_client):
    response = flask_test_client.get("/")
    assert response.status_code == 302


def test_upload_page(flask_test_client):
    response = flask_test_client.get("/upload")
    assert response.status_code == 200


def test_upload_xlsx_successful(requests_mock, example_pre_ingest_data_file, flask_test_client):
    requests_mock.post(
        "http://data-store/ingest",
        content=b'"Success: Spreadsheet data ingested"\n',
    )
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_pre_ingest_data_file})
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert "Success: Spreadsheet data ingested" in str(page_html)


def test_upload_xlsx_errors(requests_mock, example_pre_ingest_data_file, flask_test_client):
    requests_mock.post(
        "http://data-store/ingest",
        content=b'{\n "validation_errors": [\n    "Wrong '
        b'Type Failure: Sheet \\"Funding\\" column \\"Spend for Reporting '
        b'Period\\" expected type \\"float64\\", got type \\"object\\"",\n'
        b'"Enum Value Failure: Sheet \\"RiskRegister\\" Column '
        b'\\"Pre-mitigatedImpact\\" Row 5 Value \\"Error\\" is not a valid '
        b'enum value."]\n}\n',
    )
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_pre_ingest_data_file})
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert (
        'Wrong Type Failure: Sheet "Funding" column "Spend for Reporting '
        'Period" expected type "float64", got type "object'
    ) in str(page_html)
    assert (
        'Enum Value Failure: Sheet "RiskRegister" Column '
        '"Pre-mitigatedImpact" Row 5 Value "Error" is not a valid enum value.'
    ) in str(page_html)


def test_upload_wrong_format(flask_test_client, example_ingest_wrong_format):
    response = flask_test_client.post("/upload", data={"ingest_spreadsheet": example_ingest_wrong_format})
    page_html = BeautifulSoup(response.data)
    assert response.status_code == 200
    assert ("Unexpected file format:") in str(page_html)
