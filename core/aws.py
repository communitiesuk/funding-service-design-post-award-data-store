from io import FileIO

from boto3 import client
from botocore.exceptions import ClientError, EndpointConnectionError
from flask import current_app

from config import Config

if hasattr(Config, "AWS_ACCESS_KEY_ID") and hasattr(Config, "AWS_SECRET_ACCESS_KEY"):
    _S3_CLIENT = client(
        "s3",
        aws_access_key_id=Config.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=Config.AWS_SECRET_ACCESS_KEY,
        region_name=Config.AWS_REGION,
        endpoint_url=Config.AWS_ENDPOINT_OVERRIDE,
        config=Config.AWS_CONFIG if hasattr(Config, "AWS_CONFIG") else None,
    )
else:
    # boto gets access keys from the environment directly in AWS
    _S3_CLIENT = client(
        "s3",
        region_name=Config.AWS_REGION,
        endpoint_url=Config.AWS_ENDPOINT_OVERRIDE,
    )


def upload_file(file: FileIO, bucket: str, object_name: str):
    """Uploads a file to an S3 bucket.

    :param file: a readable file-like object
    :param bucket: bucket to upload to
    :param object_name: S3 object name
    """
    try:
        _S3_CLIENT.upload_fileobj(file, bucket, object_name)
    except (ClientError, EndpointConnectionError) as bucket_error:
        current_app.logger.error(bucket_error)
