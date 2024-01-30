import logging
import uuid
from io import BytesIO

from flask import g

from core.handlers import handle_exception, save_failed_submission


def test_handle_exception_ingest_endpoint(test_session, mocker, caplog):
    """If ingest endpoint then assert that the uncaught ingest exception is handled correctly."""
    # TODO rewrite this test for error handling within ingest function
    mock_save_failed_submission = mocker.patch("core.handlers.save_failed_submission", return_value="AN ID")

    with caplog.at_level(logging.ERROR) and test_session.application.test_request_context(path="/ingest"):
        file = BytesIO(b"mock file")
        g.excel_file = file
        response, status_code = handle_exception(KeyError())

    assert status_code == 500
    assert "id" in response
    assert "ERROR" in caplog.text
    assert "Uncaught ingest exception - failure_id=" in caplog.text
    mock_save_failed_submission.assert_called_once()


def test_handle_exception(test_session):
    """If not ingest endpoint, then exception should pass through handler."""
    with test_session.application.test_request_context(path="/some-other-route"):
        pass_through_exception = handle_exception(KeyError())
    assert isinstance(pass_through_exception, KeyError)


def test_save_failed_submission(mocker):
    """Asserts that save filed submission uploads a file and returns a valid UUID"""
    mock_upload_file = mocker.patch("core.handlers.upload_file")
    mock_file = BytesIO(b"some file")
    failure_uuid = save_failed_submission(mock_file)
    assert failure_uuid
    assert uuid.UUID(str(failure_uuid), version=4)
    mock_upload_file.assert_called_once()
