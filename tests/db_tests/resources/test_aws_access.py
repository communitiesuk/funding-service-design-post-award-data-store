import io

import boto3
import pandas as pd
import pytest

from config.envs.development import DevelopmentConfig as Config

AWS_REGION = Config.AWS_REGION
AWS_ACCESS_KEY_ID = Config.AWS_ACCESS_KEY_ID
AWS_SECRET_ACCESS_KEY = Config.AWS_SECRET_ACCESS_KEY
ENDPOINT_URL = Config.ENDPOINT_URL

client = boto3.client("s3", aws_access_key_id="test", aws_secret_access_key="test", endpoint_url=ENDPOINT_URL)


@pytest.mark.skip(reason="Test should only be run locally in dev environment")
def test_list_buckets():
    """
    List S3 buckets.
    """
    response = client.list_buckets()

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    assert "data-store-failed-files-dev" in response["Buckets"][0]["Name"]
    assert "data-store-file-assets-dev" in response["Buckets"][1]["Name"]


@pytest.mark.skip(reason="Test should only be run locally in dev environment")
def test_extract_file_from_bucket():
    obj = client.get_object(Bucket="data-store-file-assets-dev", Key="example-template.xlsx")
    data = obj["Body"].read()

    df = pd.read_excel(io.BytesIO(data))

    assert "Example sheet 1" in df.columns
