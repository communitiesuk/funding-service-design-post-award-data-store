import uuid
from io import BytesIO

from core.handlers import handle_exception, save_failed_submission


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
