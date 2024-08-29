import io
from urllib.parse import parse_qs, unquote, urlparse

import pytest

from config import Config
from data_store.aws import _S3_CLIENT
from data_store.const import EXCEL_MIMETYPE
from data_store.controllers.retrieve_submission_file import get_custom_file_name, retrieve_submission_file
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
    """
    Uploads a mock generic file with a specific incorrect filename to match R4 ingest bug
    and deletes it on tear down.
    """
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
    presigned_s3_url = retrieve_submission_file(submission_id=submission_id)

    parsed_url = urlparse(presigned_s3_url)
    path_segments = parsed_url.path.split("/")
    query_params = parse_qs(parsed_url.query)
    filename_param = query_params.get("response-content-disposition", [""])[0]
    filename = unquote(filename_param.split("filename = ")[-1])

    assert "fake_file.xlsx" in filename
    assert "data-store-successful-files-unit-tests" in path_segments
    assert filename.endswith(".xlsx")


def test_retrieve_submission_file_ingest_spreadsheet_name(
    seeded_test_client, uploaded_mock_file_ingest_spreadsheet_name
):
    submission_id = "S-R03-1"
    presigned_s3_url = retrieve_submission_file(submission_id=submission_id)

    parsed_url = urlparse(presigned_s3_url)
    path_segments = parsed_url.path.split("/")
    query_params = parse_qs(parsed_url.query)
    filename_param = query_params.get("response-content-disposition", [""])[0]
    filename = unquote(filename_param.split("filename = ")[-1])

    assert "1955-03-12-hs-a-district-council-from-hogwarts-feb2023-feb2023.xlsx" in filename
    assert "data-store-successful-files-unit-tests" in path_segments
    assert filename.endswith(".xlsx")


def test_get_custom_file_name(seeded_test_client):
    submission = Submission.query.filter(Submission.submission_id == "S-R03-1").one()

    custom_file_name = get_custom_file_name(submission.id)

    assert custom_file_name == "1955-03-12-hs-a-district-council-from-hogwarts-feb2023-feb2023"
