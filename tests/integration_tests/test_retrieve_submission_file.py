import io

import pytest

from config import Config
from data_store.aws import _S3_CLIENT
from data_store.const import EXCEL_MIMETYPE
from data_store.controllers.retrieve_submission_file import retrieve_submission_file
from data_store.db.entities import Submission


@pytest.fixture()
def uploaded_mock_file(seeded_test_client, test_buckets):
    """Uploads a mock generic file and deletes it on tear down."""
    fake_file = io.BytesIO(b"0x01010101")
    uuid = str(
        Submission.query.filter(Submission.submission_id == "S-R03-1").with_entities(Submission.id).distinct().one()[0]
    )
    key = f"HS/{uuid}"
    metadata = {"filename": "fake_file.xlsx"}
    _S3_CLIENT.upload_fileobj(
        fake_file,
        Config.AWS_S3_BUCKET_SUCCESSFUL_FILES,
        key,
        ExtraArgs={"Metadata": metadata, "ContentType": EXCEL_MIMETYPE},
    )
    yield
    _S3_CLIENT.delete_object(Bucket=Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, Key=key)


@pytest.fixture()
def uploaded_mock_file_ingest_spreadsheet_name(seeded_test_client, test_buckets):
    """Uploads a mock generic file and deletes it on tear down."""
    fake_file = io.BytesIO(b"0x01010101")
    uuid = str(
        Submission.query.filter(Submission.submission_id == "S-R03-1").with_entities(Submission.id).distinct().one()[0]
    )
    key = f"HS/{uuid}"
    metadata = {
        "filename": "ingest_spreadsheet",
        "submission_id": "S-R03-1",
        "programme_name": "Leaky Cauldron regeneration",
    }
    _S3_CLIENT.upload_fileobj(
        fake_file,
        Config.AWS_S3_BUCKET_SUCCESSFUL_FILES,
        key,
        ExtraArgs={"Metadata": metadata, "ContentType": EXCEL_MIMETYPE},
    )
    yield
    _S3_CLIENT.delete_object(Bucket=Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, Key=key)


def test_retrieve_submission_file_invalid_id(seeded_test_client):
    invalid_id = "S-R10-10"

    with pytest.raises(RuntimeError) as e:
        retrieve_submission_file(submission_id=invalid_id)

    assert str(e.value) == f"Could not find a submission that matches submission_id {invalid_id}"


def test_retrieve_submission_file(seeded_test_client, uploaded_mock_file):
    submission_id = "S-R03-1"
    file = retrieve_submission_file(submission_id=submission_id)
    assert file.filename == "fake_file.xlsx"
    assert file.content_type == EXCEL_MIMETYPE
    assert file.stream.read() == b"0x01010101"


def test_retrieve_submission_file_ingest_spreadsheet_name(
    seeded_test_client, uploaded_mock_file_ingest_spreadsheet_name
):
    submission_id = "S-R03-1"
    file = retrieve_submission_file(submission_id=submission_id)
    assert file.filename == "Leaky Cauldron regeneration - S-R03-1.xlsx"
    assert file.stream.read() == b"0x01010101"
    assert file.content_type == EXCEL_MIMETYPE


def test_retrieve_submission_file_key_not_found_s3_throws_exception(seeded_test_client, test_buckets):
    submission_id = "S-R03-1"
    uuid = str(
        Submission.query.filter(Submission.submission_id == "S-R03-1").with_entities(Submission.id).distinct().one()[0]
    )
    with pytest.raises(FileNotFoundError) as e:
        retrieve_submission_file(submission_id=submission_id)

    assert str(e.value) == (
        f"Submission {submission_id} exists in the database but could not find the related file HS/{uuid} on S3."
    )
