from uuid import UUID

from werkzeug.datastructures import FileStorage

from core.aws import get_failed_file


def get_failed_submission(failure_uuid: str) -> FileStorage:
    """Returns a failed submission from S3 storage that matches the provided failure id.

    :param failure_uuid: UUID that matches the submission.
    :return: the failed submission
    """
    try:
        failure_uuid = UUID(failure_uuid, version=4)
    except ValueError as e:
        raise ValueError("failure_uuid is not a valid UUID.") from e

    file = get_failed_file(failure_uuid)
    if not file:
        raise FileNotFoundError(f"File not found: id={failure_uuid} does not match any stored failed files.")

    return file
