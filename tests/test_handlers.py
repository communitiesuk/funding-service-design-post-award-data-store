import logging
import uuid
from io import BytesIO

from flask import g

from core.exceptions import ValidationError
from core.handlers import (
    handle_exception,
    handle_validation_error,
    save_failed_submission,
)
from core.validation.failures import internal, user


def test_handle_validation_error_internal(test_client, mocker, caplog):
    mock_save_failed_submission = mocker.patch("core.handlers.save_failed_submission", return_value="AN ID")

    failures = [internal.ExtraTableFailure(extra_table="Test Table")]
    with caplog.at_level(logging.ERROR) and test_client.application.test_request_context():
        file = BytesIO(b"mock file")
        g.excel_file = file
        response, status_code = handle_validation_error(ValidationError(validation_failures=failures))

    assert status_code == 500
    assert response == {
        "detail": "Internal ingest exception.",
        "id": "AN ID",
        "status": 500,
        "title": "Internal Server Error",
        "internal_errors": failures,
    }
    assert "failure_id" in caplog.text
    assert "internal_failures" in caplog.text
    mock_save_failed_submission.assert_called_once()


def test_handle_validation_error_user(test_client, mocker):
    failures = [user.GenericFailure(sheet="Test Sheet", section="Test Section", cell_index="A1", message="Test")]
    with test_client.application.test_request_context():
        file = BytesIO(b"mock file")
        g.excel_file = file
        response, status_code = handle_validation_error(ValidationError(validation_failures=failures))

    assert status_code == 400
    assert "detail" in response
    assert "status" in response
    assert "title" in response
    assert "pre_transformation_errors" in response
    assert "validation_errors" in response
    assert response["validation_errors"]  # truthy assertion, ignore content


def test_handle_exception_ingest_endpoint(test_client, mocker, caplog):
    """If ingest endpoint then assert that the uncaught ingest exception is handled correctly."""
    mock_save_failed_submission = mocker.patch("core.handlers.save_failed_submission", return_value="AN ID")

    with caplog.at_level(logging.ERROR) and test_client.application.test_request_context(path="/ingest"):
        file = BytesIO(b"mock file")
        g.excel_file = file
        response, status_code = handle_exception(KeyError())

    assert status_code == 500
    assert "id" in response
    assert "ERROR" in caplog.text
    assert "Uncaught ingest exception - failure_id=" in caplog.text
    mock_save_failed_submission.assert_called_once()


def test_handle_exception(test_client):
    """If not ingest endpoint, then exception should pass through handler."""
    with test_client.application.test_request_context(path="/some-other-route"):
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
