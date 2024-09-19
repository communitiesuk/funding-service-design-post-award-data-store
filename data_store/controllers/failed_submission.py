from uuid import UUID

from config import Config
from data_store.aws import create_presigned_url, get_failed_file_key


def get_failed_submission(failure_uuid: UUID) -> str:
    """Returns a presigned ULR to S3 storage to download a submission that
    matches the provided failure id.

    :param failure_uuid: UUID that matches the submission.
    :return: the failed submission
    """

    file_key = get_failed_file_key(failure_uuid)

    presigned_url = create_presigned_url(
        bucket_name=Config.AWS_S3_BUCKET_FAILED_FILES,
        file_key=file_key,
        filename=file_key,
    )

    return presigned_url
