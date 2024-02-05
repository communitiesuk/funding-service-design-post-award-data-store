from io import BytesIO
from typing import IO
from uuid import UUID

from boto3 import client
from botocore.exceptions import ClientError, EndpointConnectionError
from flask import current_app
from werkzeug.datastructures import FileStorage

from config import Config
from core.const import EXCEL_MIMETYPE

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
    )


def upload_file(file: IO, bucket: str, object_name: str, metadata: dict = None) -> bool:
    """Uploads a file to an S3 bucket.

    :param file: a readable file-like object
    :param bucket: bucket to upload to
    :param object_name: S3 object name
    :param metadata: optional dictionary containing metadata for upload
    :return: True if successful else False
    """
    file.seek(0)
    _S3_CLIENT.upload_fileobj(file, bucket, object_name, ExtraArgs={"Metadata": metadata if metadata else {}})
    return True


def get_file(bucket: str, object_name: str) -> tuple[BytesIO, dict] | None:
    """Retrieves a file from an S3 bucket.

    :param bucket: bucket to retrieve from
    :param object_name: S3 object name
    :return: retrieved file as a BytesIO
    """
    try:
        response = _S3_CLIENT.get_object(Bucket=bucket, Key=object_name)
    except (ClientError, EndpointConnectionError) as bucket_error:
        current_app.logger.error(bucket_error)
        return None

    return BytesIO(response["Body"].read()), response["Metadata"]


def get_failed_file(failure_uuid: UUID) -> FileStorage | None:
    """Gets a failed file from S3 via its failure_uuid.

    This "failed file" is an Excel submission file that was being ingested when an uncaught exception occurred during
    ingest. The failure id is logged at the time of ingest failure and is used within the name of the file saved to S3.

    :param failure_uuid: the failure UUID used to identify the failed file
    :return: the failed file's name and contents as a BytesIO
    """
    uuid_str = str(failure_uuid)
    response = _S3_CLIENT.list_objects_v2(Bucket=Config.AWS_S3_BUCKET_FAILED_FILES)
    file_list = response["Contents"]
    filename = next((file["Key"] for file in file_list if uuid_str in file["Key"]), None)
    if not filename:
        return None

    file, meta_data = get_file(Config.AWS_S3_BUCKET_FAILED_FILES, filename)
    if "filename" in meta_data:
        filename = meta_data["filename"]
    return FileStorage(
        stream=file,
        filename=filename,
        content_type=EXCEL_MIMETYPE,
    )
