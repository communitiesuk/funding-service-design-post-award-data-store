import flask
from flask import abort

from config import Config
from core.aws import get_file
from core.const import EXCEL_MIMETYPE


def retrieve(submission_id):
    """Handle the download request and return the originally submitted spreadsheet.

    Select file by:
    - submission_id

    :return: Flask response object containing the requested spreadsheet.
    """
    if file := get_file(Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, submission_id):
        pass
    else:
        return abort(404, "Could not find a file that matches this submission_id")

    return flask.send_file(file, mimetype=EXCEL_MIMETYPE, download_name=f"{submission_id}.xlsx", as_attachment=True)
