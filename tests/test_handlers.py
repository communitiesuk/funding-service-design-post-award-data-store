import logging
from io import BytesIO

from flask import g

from core.handlers import handle_exception
from core.validation.failures import ExtraSheetFailure


def test_handle_exception_ingest_endpoint(test_client, mocker, caplog):
    """If ingest endpoint then assert that the uncaught ingest exception is handled correctly."""
    mocked_upload_file = mocker.patch("core.handlers.upload_file")

    with caplog.at_level(logging.ERROR) and test_client.application.test_request_context(path="/ingest"):
        file = BytesIO(b"mock file")
        g.excel_file = file
        response, status_code = handle_exception(KeyError())

    assert status_code == 500
    assert response.json["detail"] == "Uncaught ingest exception."
    assert "id" in response.json
    assert "ERROR" in caplog.text
    assert "Uncaught ingest exception - failure_id=" in caplog.text
    mocked_upload_file.assert_called_once()


def test_handle_exception_ingest_endpoint_unimplemented_failure(test_client, mocker, example_data_model_file):
    """If an unimplemented failure message exception is raised during validation message creation, then it should be
    handled as an uncaught exception and a file should be saved to S3 etc."""
    # mock saving to S3
    mocked_upload_file = mocker.patch("core.handlers.upload_file")
    # mock validation to return a Failure that does not have a message implementation
    mocker.patch("core.validation.validate_workbook", return_value=[ExtraSheetFailure("test")])

    test_client.post(
        "/ingest",
        data={
            "excel_file": example_data_model_file,
        },
    )

    mocked_upload_file.assert_called_once()


def test_handle_exception(test_client):
    """If not ingest endpoint, then exception should pass through handler."""
    with test_client.application.test_request_context(path="/some-other-route"):
        pass_through_exception = handle_exception(KeyError())
    assert isinstance(pass_through_exception, KeyError)
