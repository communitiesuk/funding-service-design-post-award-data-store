import io

import pytest

from config import Config
from core.aws import _S3_CLIENT
from core.const import EXCEL_MIMETYPE
from tests.integration_tests.test_aws import create_bucket, delete_bucket


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
def uploaded_mock_file():
    """Uploads a mock generic file and deletes it on tear down."""
    fake_file = io.BytesIO(b"0x01010101")
    fake_filename = "S-R03-1"
    _S3_CLIENT.upload_fileobj(fake_file, Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, fake_filename)
    yield
    _S3_CLIENT.delete_object(Bucket=Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, Key=fake_filename)


def test_retrieve_invalid_id(seeded_test_client):
    invalid_id = "S-R10-10"
    response = seeded_test_client.get(f"/retrieve?submission_id={invalid_id}")
    assert response.status_code == 404


def test_retrieve(seeded_test_client, uploaded_mock_file):
    submission_id = "S-R03-1"
    response = seeded_test_client.get(f"/retrieve?submission_id={submission_id}")
    assert response.status_code == 200
    assert response.headers.get("Content-Disposition") == "attachment; filename=S-R03-1.xlsx"
    assert response.data == b"0x01010101"
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response.content_type == EXCEL_MIMETYPE


def test_retrieve_db_invalid_id(seeded_test_client):
    invalid_id = "S-R10-10"
    response = seeded_test_client.get(f"/retrieve_db?submission_id={invalid_id}")
    assert response.status_code == 404


def test_retrieve_db(seeded_test_client):
    submission_id = "S-R03-1"
    response = seeded_test_client.get(f"/retrieve_db?submission_id={submission_id}")
    assert response.status_code == 200
    assert response.headers.get("Content-Disposition") == "attachment; filename=test_submission.xlsx"
    assert response.data == b"0x01010101"
    assert response.headers["content-type"] == "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    assert response.content_type == EXCEL_MIMETYPE
