import io
import logging
import uuid

import pytest
from botocore.exceptions import ClientError, EndpointConnectionError

from config import Config
from core.aws import _S3_CLIENT, get_failed_file, get_file, upload_file
from tests.integration_tests.conftest import TEST_BUCKET


@pytest.fixture()
def mock_failed_submission():
    """Uploads a mock failed submission and deletes it on tear down."""
    fake_failure_uuid = uuid.uuid4()
    fake_file = io.BytesIO(b"some file")
    fake_filename = f"{fake_failure_uuid}.xlsx"
    _S3_CLIENT.upload_fileobj(fake_file, Config.AWS_S3_BUCKET_FAILED_FILES, fake_filename)
    yield fake_failure_uuid, fake_filename
    _S3_CLIENT.delete_object(Bucket=Config.AWS_S3_BUCKET_FAILED_FILES, Key=fake_filename)


@pytest.fixture()
def uploaded_mock_file():
    """Uploads a mock generic file and deletes it on tear down."""
    fake_file = io.BytesIO(b"some file")
    fake_filename = "test-file"
    _S3_CLIENT.upload_fileobj(fake_file, TEST_BUCKET, fake_filename)
    yield
    _S3_CLIENT.delete_object(Bucket=TEST_BUCKET, Key=fake_filename)


@pytest.mark.parametrize(
    "raised_exception",
    (
        ClientError({}, "operation_name"),
        EndpointConnectionError(endpoint_url="/"),
    ),
)
def test_upload_file_handles_errors(mocker, test_session, caplog, raised_exception):
    """
    GIVEN a file upload to S3 is attempted
    WHEN a ClientError or an EndpointConnectionError occurs
    THEN they should be handled by being logged and the service continuing
    """
    mocker.patch("core.aws._S3_CLIENT.upload_fileobj", side_effect=raised_exception)
    with caplog.at_level(logging.ERROR):
        upload_success = upload_file(io.BytesIO(b"some file"), "A_MOCKED_BUCKET", "filename")
    assert not upload_success
    assert caplog.messages[0] == str(raised_exception)


def test_upload_file(test_session):
    """
    GIVEN a file upload to S3 is attempted
    WHEN it is successful
    THEN the function should return True
    """
    uploaded_file = io.BytesIO(b"some file")
    upload_success = upload_file(uploaded_file, TEST_BUCKET, "test-upload-file")
    assert upload_success
    _S3_CLIENT.delete_object(Bucket=TEST_BUCKET, Key="test-upload-file")  # tear down


@pytest.mark.parametrize(
    "raised_exception",
    (
        ClientError({}, "operation_name"),
        EndpointConnectionError(endpoint_url="/"),
    ),
)
def test_get_file_handles_errors(mocker, test_session, caplog, raised_exception):
    """
    GIVEN a file retrieval from S3 is attempted
    WHEN a ClientError or an EndpointConnectionError occurs
    THEN they should be handled by being logged and the service continuing
    """
    mocker.patch("core.aws._S3_CLIENT.download_fileobj", side_effect=raised_exception)
    with caplog.at_level(logging.ERROR):
        get_file("A_MOCKED_BUCKET", "filename")
    assert caplog.messages[0] == str(raised_exception)


def test_get_file(test_session, uploaded_mock_file):
    """
    GIVEN a file retrieval to S3 is attempted
    WHEN it is successful
    THEN the function should return a file
    """
    downloaded_file = get_file(TEST_BUCKET, "test-file")
    assert isinstance(downloaded_file, io.BytesIO)
    assert len(str(downloaded_file.read())) > 0


def test_get_failed_file(mock_failed_submission):
    """
    GIVEN a failed file exists in the FAILED-FILES S3 bucket
    WHEN it is retrieved with a matching UUID
    THEN a file with a matching filename should be returned that contains bytes
    """
    failure_uuid, filename = mock_failed_submission
    file = get_failed_file(failure_uuid)
    assert file, "No file was returned"
    assert file.filename == filename, "The files name does not match"
    assert len(str(file.stream.read())) > 0, "The file is empty"
