import logging
from io import BytesIO

from flask import g

from core.handlers import handle_exception


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


def test_handle_exception(test_client):
    """If not ingest endpoint, then exception should pass through handler."""
    with test_client.application.test_request_context(path="/some-other-route"):
        pass_through_exception = handle_exception(KeyError())
    assert isinstance(pass_through_exception, KeyError)
