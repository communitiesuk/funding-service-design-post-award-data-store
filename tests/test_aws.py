import io
import uuid

import pandas as pd
import pytest
from botocore.exceptions import ClientError, EndpointConnectionError

from config import Config
from core.aws import _S3_CLIENT, get_failed_file, upload_file

try:
    _S3_CLIENT.list_buckets()
    S3_NOT_ACCESSIBLE = False
except (ClientError, EndpointConnectionError):
    S3_NOT_ACCESSIBLE = True


@pytest.fixture()
def fake_failed_submission():
    fake_failure_uuid = uuid.uuid4()
    fake_file = io.BytesIO(b"some file")
    fake_filename = f"{fake_failure_uuid}.xlsx"
    upload_file(fake_file, Config.AWS_S3_BUCKET_FAILED_FILES, fake_filename)
    yield fake_failure_uuid, fake_filename
    _S3_CLIENT.delete_object(Bucket=Config.AWS_S3_BUCKET_FAILED_FILES, Key=fake_filename)


@pytest.mark.skipif(S3_NOT_ACCESSIBLE, reason="Cannot access S3.")
def test_get_failed_file(fake_failed_submission):
    failure_uuid, filename = fake_failed_submission
    file = get_failed_file(failure_uuid)
    assert file
    assert file.filename == filename


@pytest.mark.skipif(S3_NOT_ACCESSIBLE, reason="Cannot access S3.")
def test_list_buckets():
    """
    List S3 buckets.
    """
    response = _S3_CLIENT.list_buckets()

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    assert "data-store-failed-files-dev" in response["Buckets"][0]["Name"]
    assert "data-store-file-assets-dev" in response["Buckets"][1]["Name"]


@pytest.mark.skipif(S3_NOT_ACCESSIBLE, reason="Cannot access S3.")
def test_extract_file_from_bucket():
    obj = _S3_CLIENT.get_object(Bucket="data-store-file-assets-dev", Key="TF-grant-awarded.csv")
    data = obj["Body"].read()

    df = pd.read_csv(io.BytesIO(data))

    assert "Grant Awarded" in df.columns
