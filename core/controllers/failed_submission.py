from uuid import UUID

from flask import abort, send_file

from core.aws import get_failed_file


def get_failed_submission(failure_uuid: str):
    """Returns a failed submission from S3 storage that matches the provided failure id.

    :param failure_uuid: UUID that matches the submission.
    :return: the failed submission
    """
    try:
        failure_uuid = UUID(failure_uuid, version=4)  # type: ignore # TODO: fixme
    except ValueError:
        return abort(400, "Bad Request: failure_uuid is not a valid UUID.")

    file = get_failed_file(failure_uuid)  # type: ignore # TODO: fixme
    if file:
        return send_file(file.stream, download_name=file.filename, mimetype=file.mimetype, as_attachment=True)  # noqa
    else:
        return abort(404, f"File not found: id={failure_uuid} does not match any stored failed files.")
