import io

import pytest

from config import Config
from core.aws import _S3_CLIENT
from core.const import EXCEL_MIMETYPE
from core.db.entities import Submission
from tests.integration_tests.conftest import create_bucket, delete_bucket


@pytest.fixture(autouse=True, scope="module")
def test_buckets():
    """Sets up and tears down buckets used by this module.
    On set up:
    - creates data-store-successful-files-unit-tests
    On tear down, deletes all objects stored in the buckets and then the buckets themselves.
    """

    create_bucket(Config.AWS_S3_BUCKET_SUCCESSFUL_FILES)
    yield
    delete_bucket(Config.AWS_S3_BUCKET_SUCCESSFUL_FILES)


@pytest.fixture()
def uploaded_mock_file(seeded_test_client):
    """Uploads a mock generic file and deletes it on tear down."""
    fake_file = io.BytesIO(b"0x01010101")
    uuid = str(
        Submission.query.filter(Submission.submission_id == "S-R03-1").with_entities(Submission.id).distinct().one()[0]
    )
    key = f"HS/{uuid}"
    metadata = {"filename": "fake_file.xlsx"}
    _S3_CLIENT.upload_fileobj(fake_file, Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, key, ExtraArgs={"Metadata": metadata})
    yield
    _S3_CLIENT.delete_object(Bucket=Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, Key=key)


def test_retrieve_submission_file_invalid_id(seeded_test_client):
    invalid_id = "S-R10-10"
    response = seeded_test_client.get(f"/retrieve_submission_file?submission_id={invalid_id}")
    assert response.status_code == 404


def test_retrieve_submission_file(seeded_test_client, uploaded_mock_file):
    submission_id = "S-R03-1"
    response = seeded_test_client.get(f"/retrieve_submission_file?submission_id={submission_id}")
    assert response.status_code == 200
    assert response.headers.get("Content-Disposition") == "attachment; filename=fake_file.xlsx"
    assert response.data == b"0x01010101"
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response.content_type == EXCEL_MIMETYPE


# TODO: [FMD-227] Remove submission files from db
def test_retrieve_submission_file_db_invalid_id(seeded_test_client):
    invalid_id = "S-R10-10"
    response = seeded_test_client.get(f"/retrieve_submission_file_db?submission_id={invalid_id}")
    assert response.status_code == 404


# TODO: [FMD-227] Remove submission files from db
def test_retrieve_submission_file_db(seeded_test_client):
    submission_id = "S-R03-1"
    response = seeded_test_client.get(f"/retrieve_submission_file_db?submission_id={submission_id}")
    assert response.status_code == 200
    assert response.headers.get("Content-Disposition") == "attachment; filename=test_submission.xlsx"
    assert response.data == b"0x01010101"
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response.content_type == EXCEL_MIMETYPE
