import io
import uuid

import pytest
from botocore.exceptions import ClientError, EndpointConnectionError
from werkzeug.datastructures import FileStorage

from config import Config
from core.aws import _S3_CLIENT, get_failed_file, get_file, upload_file
from core.controllers.ingest import save_failed_submission, save_submission_file_s3
from core.db.entities import Submission
from tests.integration_tests.conftest import create_bucket, delete_bucket

TEST_BUCKET = "test-bucket"


@pytest.fixture(autouse=True, scope="module")
def test_buckets():
    """Sets up and tears down buckets used by this module.
    On set up:
    - creates test-bucket
    - creates data-store-failed-files-unit-tests

    On tear down, deletes all objects stored in the buckets and then the buckets themselves.
    """
    create_bucket(TEST_BUCKET)
    create_bucket(Config.AWS_S3_BUCKET_FAILED_FILES)
    create_bucket(Config.AWS_S3_BUCKET_SUCCESSFUL_FILES)
    yield
    delete_bucket(TEST_BUCKET)
    delete_bucket(Config.AWS_S3_BUCKET_FAILED_FILES)
    delete_bucket(Config.AWS_S3_BUCKET_SUCCESSFUL_FILES)


@pytest.fixture()
def mock_failed_submission():
    """Uploads a mock failed submission and deletes it on tear down."""
    fake_failure_uuid = uuid.uuid4()
    fake_file = io.BytesIO(b"some file")
    fake_key = f"{fake_failure_uuid}.xlsx"
    metadata = {"filename": "fake_file.xlsx"}
    _S3_CLIENT.upload_fileobj(fake_file, Config.AWS_S3_BUCKET_FAILED_FILES, fake_key, ExtraArgs={"Metadata": metadata})
    yield fake_failure_uuid
    _S3_CLIENT.delete_object(Bucket=Config.AWS_S3_BUCKET_FAILED_FILES, Key=fake_key)


@pytest.fixture()
def uploaded_mock_file():
    """Uploads a mock generic file and deletes it on tear down."""
    fake_file = io.BytesIO(b"some file")
    fake_filename = "test-file"
    metadata = {"some_meta": "meta content"}
    _S3_CLIENT.upload_fileobj(fake_file, TEST_BUCKET, fake_filename, ExtraArgs={"Metadata": metadata})
    yield
    _S3_CLIENT.delete_object(Bucket=TEST_BUCKET, Key=fake_filename)


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


def test_save_submission_file_s3(seeded_test_client):
    filename = "example.xlsx"
    filebytes = b"example file contents"
    file = FileStorage(io.BytesIO(filebytes), filename=filename)

    submission_id, uuid = Submission.query.with_entities(Submission.submission_id, Submission.id).distinct().one()

    save_submission_file_s3(file, submission_id)

    response = _S3_CLIENT.get_object(Bucket=Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, Key=f"HS/{uuid}")
    metadata = response["Metadata"]

    assert response["Body"].read() == filebytes
    assert metadata["submission_id"] == submission_id
    assert metadata["filename"] == filename
    assert metadata["programme_name"] == "Leaky Cauldron regeneration"


def test_save_failed_submission_s3(mocker):
    """Asserts that save filed submission uploads a file and returns a valid UUID"""
    mock_upload_file = mocker.patch("core.controllers.ingest.upload_file")
    mock_file = io.BytesIO(b"some file")
    failure_uuid = save_failed_submission(mock_file)
    assert failure_uuid
    assert uuid.UUID(str(failure_uuid), version=4)
    mock_upload_file.assert_called_once()


@pytest.mark.parametrize(
    "raised_exception",
    (
        ClientError({}, "operation_name"),
        EndpointConnectionError(endpoint_url="/"),
    ),
)
def test_get_file_handles_errors(mocker, test_session, raised_exception):
    """
    GIVEN a file retrieval from S3 is attempted
    WHEN an error
    THEN they should raised
    """
    mocker.patch("core.aws._S3_CLIENT.get_object", side_effect=raised_exception)
    with pytest.raises((ClientError, EndpointConnectionError)) as exception:
        get_file("A_MOCKED_BUCKET", "filename")
    assert str(exception.value) == str(raised_exception)


def test_get_file(test_session, uploaded_mock_file):
    """
    GIVEN a file retrieval to S3 is attempted
    WHEN it is successful
    THEN the function should return a file
    """
    downloaded_file, meta_data = get_file(TEST_BUCKET, "test-file")
    assert isinstance(downloaded_file, io.BytesIO)
    assert len(str(downloaded_file.read())) > 0
    assert meta_data["some_meta"] == "meta content"


def test_get_failed_file(mock_failed_submission):
    """
    GIVEN a failed file exists in the FAILED-FILES S3 bucket
    WHEN it is retrieved with a matching UUID
    THEN a file with a matching filename should be returned that contains bytes
    """
    file = get_failed_file(mock_failed_submission)
    assert file, "No file was returned"
    assert file.filename == "fake_file.xlsx", "The files name does not match"
    assert len(str(file.stream.read())) > 0, "The file is empty"
