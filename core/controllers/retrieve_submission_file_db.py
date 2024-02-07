from io import BytesIO

import flask
from flask import abort
from sqlalchemy import select
from sqlalchemy.exc import NoResultFound

from core.const import EXCEL_MIMETYPE
from core.db import db
from core.db.entities import Submission

# TODO: [FMD-227] Remove submission files from db


def retrieve_submission_file_db(submission_id):
    """Handle the download request and return the originally submitted spreadsheet.

    TODO: This end point is deprecated, as files are intended to be saved in S3 from now on. The functionality to
    retrieve from db will be removed once all existing files are migrated onto S3 for storage.

    Select file by:
    - submission_id

    :return: Flask response object containing the requested spreadsheet.
    """
    query = select(Submission.submission_file, Submission.submission_filename, Submission.reporting_round).where(
        Submission.submission_id == submission_id
    )

    try:
        file_bytes, file_name, reporting_round = db.session.execute(query).one()
    except NoResultFound:
        return abort(404, "Could not find a file that matches this submission_id")

    return flask.send_file(BytesIO(file_bytes), mimetype=EXCEL_MIMETYPE, download_name=file_name, as_attachment=True)
