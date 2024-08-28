from io import BytesIO, IOBase
from typing import IO, Dict, Union
from uuid import UUID

from boto3 import client
from botocore.exceptions import ClientError
from werkzeug.datastructures import FileStorage

from config import Config
from data_store.const import EXCEL_MIMETYPE

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


def upload_file(file: Union[IO, FileStorage], bucket: str, object_name: str, metadata: dict | None = None) -> bool:
    """Uploads a file to an S3 bucket.

    :param file: a readable file-like object
    :param bucket: bucket to upload to
    :param object_name: S3 object name
    :param metadata: optional dictionary containing metadata for upload
    :return: True if successful else False
    """
    if isinstance(file, FileStorage):
        content_type = file.content_type
    elif isinstance(file, IOBase):
        # Determine content type based on the file extension or default to EXCEL_MIMETYPE
        filename = object_name.split("/")[-1]
        if filename.endswith(".json"):
            content_type = "application/json"
        else:
            content_type = EXCEL_MIMETYPE
    else:
        raise TypeError("Unsupported file type. Expected IO or FileStorage.")

    file.seek(0)
    _S3_CLIENT.upload_fileobj(
        file.stream if isinstance(file, FileStorage) else file,
        bucket,
        object_name,
        ExtraArgs={"Metadata": metadata if metadata else {}, "ContentType": content_type},
    )
    return True


def get_file(bucket: str, object_name: str) -> tuple[BytesIO, dict, str]:
    """Retrieves a file from an S3 bucket.

    :param bucket: bucket to retrieve from
    :param object_name: S3 object name
    :return: retrieved file as a BytesIO
    """
    response = _S3_CLIENT.get_object(Bucket=bucket, Key=object_name)
    return BytesIO(response["Body"].read()), response["Metadata"], response["ContentType"]


def get_failed_file_key(failure_uuid: UUID) -> str:
    """Gets the Key of failed file from S3 via its failure_uuid.

    This "failed file" is an Excel submission file that was being ingested when an uncaught exception occurred during
    ingest. The failure id is logged at the time of ingest failure and is used within the name of the file saved to S3.

    :param failure_uuid: the failure UUID used to identify the failed file
    :return: the full key used in S3 for the failed file
    """
    uuid_str = str(failure_uuid)
    response = _S3_CLIENT.list_objects_v2(Bucket=Config.AWS_S3_BUCKET_FAILED_FILES)
    file_list = response["Contents"]
    file_key = next((file["Key"] for file in file_list if uuid_str in file["Key"]), None)
    if not file_key:
        raise FileNotFoundError(f"File not found: id={failure_uuid} does not match any stored failed files.")
    return file_key


def get_file_metadata(
    bucket_name: str,
    file_key: str,
    return_full_head_data: bool = False,
) -> Dict[str, str]:
    """Get metadata of a file stored in S3.

    :param bucket_name: string
    :param file_key: string
    :param return_full_head_data: bool

    :return: Metadata as a dictionary. Raises an exception if an error occurs.
    """
    try:
        s3_response = _S3_CLIENT.head_object(Bucket=bucket_name, Key=file_key)
    except ClientError as error:
        if error.response["Error"]["Code"] == "404":
            raise FileNotFoundError(
                (f"Could not find file {file_key} in S3."),
            ) from error
        raise error

    if return_full_head_data:
        return s3_response

    return s3_response["Metadata"]


def create_presigned_url(bucket_name: str, file_key: str, filename: str, expiration=600) -> str:
    """Generate a presigned URL to share an S3 object

    :param bucket_name: string
    :param object_name: string
    :param filename: string
    :param expiration: Time in seconds for the presigned URL to remain valid
    :return: Presigned URL as string. If error, returns None.
    """

    try:
        get_file_metadata(bucket_name, file_key)
    except FileNotFoundError as error:
        raise error

    presigned_url = _S3_CLIENT.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": bucket_name,
            "Key": file_key,
            "ResponseContentDisposition": f"attachment; filename = {filename}",
        },
        ExpiresIn=expiration,
    )

    return presigned_url
