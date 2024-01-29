import flask
from flask import abort

from config import Config
from core.aws import get_file
from core.const import EXCEL_MIMETYPE
from core.db.entities import Programme, Project, Submission


def retrieve(submission_id):
    """Handle the download request and return the originally submitted spreadsheet.

    Select file by:
    - submission_id

    :return: Flask response object containing the requested spreadsheet.
    """
    submission_meta = (
        Programme.query.join(Project)
        .join(Submission)
        .filter(Submission.submission_id == submission_id)
        .with_entities(Submission.id, Programme.fund_type_id)
        .distinct()
    ).all()[0]
    object_name = f"{submission_meta.fund_type_id}/{str(submission_meta.id)}"

    if file_meta := get_file(Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, object_name):
        file, meta_data = file_meta
    else:
        return abort(404, "Could not find a file that matches this submission_id")

    return flask.send_file(file, mimetype=EXCEL_MIMETYPE, download_name=meta_data["filename"], as_attachment=True)
