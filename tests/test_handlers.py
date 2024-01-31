import uuid
from io import BytesIO

from core.handlers import save_failed_submission


def test_save_failed_submission(mocker):
    """Asserts that save filed submission uploads a file and returns a valid UUID"""
    mock_upload_file = mocker.patch("core.handlers.upload_file")
    mock_file = BytesIO(b"some file")
    failure_uuid = save_failed_submission(mock_file)
    assert failure_uuid
    assert uuid.UUID(str(failure_uuid), version=4)
    mock_upload_file.assert_called_once()
