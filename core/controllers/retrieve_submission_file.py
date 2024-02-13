import flask
from botocore.exceptions import ClientError
from flask import abort

from config import Config
from core.aws import get_file
from core.db.entities import Programme, Project, Submission


def retrieve_submission_file(submission_id):
    """Handle the download request and return the originally submitted spreadsheet.

    Select file by:
    - submission_id

    :return: Flask response object containing the requested spreadsheet.
    """

    submission_meta = (
        (
            Programme.query.join(Project)
            .join(Submission)
            .filter(Submission.submission_id == submission_id)
            .with_entities(Submission.id, Programme.fund_type_id)
            .distinct()
        )
        .distinct()
        .one_or_none()
    )

    if submission_meta:
        uuid, fund_type = submission_meta
        object_name = f"{fund_type}/{str(uuid)}"
    else:
        return abort(404, f"Could not find a submission that matches submission_id {submission_id}")

    try:
        file, meta_data, content_type = get_file(Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, object_name)
    except ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchKey":
            return abort(
                404,
                (
                    f"Submission {submission_id} exists in the database "
                    f"but could not find the related file {object_name} on S3."
                ),
            )
        raise error

    return flask.send_file(file, mimetype=content_type, download_name=meta_data["filename"], as_attachment=True)
