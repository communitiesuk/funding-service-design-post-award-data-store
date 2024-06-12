from uuid import UUID

from core.aws import get_failed_file


def get_failed_submission(failure_uuid: str):
    """Returns a failed submission from S3 storage that matches the provided failure id.

    :param failure_uuid: UUID that matches the submission.
    :return: the failed submission
    """
    try:
        failure_uuid = UUID(failure_uuid, version=4)
    except ValueError as error:
        raise ValueError(f"{failure_uuid} is not a valid UUID.") from error

    file = get_failed_file(failure_uuid)
    filename = file.filename
    content_type = file.mimetype
    if file:
        return file, filename, content_type
    else:
        raise FileNotFoundError(f"File not found: id={failure_uuid} does not match any stored failed files.")
