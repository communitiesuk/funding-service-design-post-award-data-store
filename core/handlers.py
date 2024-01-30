import uuid
from datetime import datetime
from typing import BinaryIO

from werkzeug.exceptions import HTTPException

from config import Config
from core.aws import upload_file
from core.const import DATETIME_ISO_8601, FAILED_FILE_S3_NAME_FORMAT


def handle_exception(uncaught_exception: Exception) -> Exception | tuple[dict, int]:
    # pass through HTTP errors
    if isinstance(uncaught_exception, HTTPException):
        return uncaught_exception

    # return {
    #     "detail": f"Uncaught exception: {uncaught_exception}",
    #     "status": 500,
    #     "title": "Internal Server Error",
    #     "internal_errors": None,
    # }, 500
    return uncaught_exception


def get_failure_uuid():
    failure_uuid = uuid.uuid4()
    return failure_uuid


def save_failed_submission(file: BinaryIO):
    """Saves the failing file to S3 with a UUID

    :return: the UUID of the failed file
    """
    failure_uuid = get_failure_uuid()
    s3_object_name = FAILED_FILE_S3_NAME_FORMAT.format(failure_uuid, datetime.now().strftime(DATETIME_ISO_8601))
    upload_file(file=file, bucket=Config.AWS_S3_BUCKET_FAILED_FILES, object_name=s3_object_name)
    return failure_uuid
