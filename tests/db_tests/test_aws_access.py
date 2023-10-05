import io

import pandas as pd
import pytest

from core.aws import _S3_CLIENT


@pytest.mark.skip(reason="Test should only be run locally in dev environment")
def test_list_buckets():
    """
    List S3 buckets.
    """
    response = _S3_CLIENT.list_buckets()

    assert response["ResponseMetadata"]["HTTPStatusCode"] == 200
    assert "data-store-failed-files-dev" in response["Buckets"][0]["Name"]
    assert "data-store-file-assets-dev" in response["Buckets"][1]["Name"]


@pytest.mark.skip(reason="Test should only be run locally in dev environment")
def test_extract_file_from_bucket():
    obj = _S3_CLIENT.get_object(Bucket="data-store-file-assets-dev", Key="example-template.xlsx")
    data = obj["Body"].read()

    df = pd.read_excel(io.BytesIO(data))

    assert "Example sheet 1" in df.columns
