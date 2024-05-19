from botocore.exceptions import ClientError

from config import Config
from core.aws import get_file
from core.db.entities import Fund, Programme, ProgrammeJunction, Submission


def retrieve_submission_file(submission_id):
    """Handle the download request and return the originally submitted spreadsheet.

    Select file by:
    - submission_id

    :return: Flask response object containing the requested spreadsheet.
    """

    submission_meta = (
        (
            Programme.query.join(ProgrammeJunction)
            .join(Submission)
            .join(Fund)
            .filter(Submission.submission_id == submission_id)
            .with_entities(Submission.id, Fund.fund_code)
            .distinct()
        )
        .distinct()
        .one_or_none()
    )

    if submission_meta:
        uuid, fund_type = submission_meta
        object_name = f"{fund_type}/{str(uuid)}"
    else:
        raise LookupError(f"could not find submission {submission_id} in database")

    try:
        file, meta_data, content_type = get_file(Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, object_name)
    except ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchKey":
            raise FileNotFoundError(f"could not find file for submission {submission_id} in s3") from error
        raise error

    filename = meta_data["filename"]
    # Check against Round 4 submission files which were all saved with 'ingest_spreadsheet' as the submission_filename
    if filename == "ingest_spreadsheet":
        filename = f'{meta_data["programme_name"]} - {meta_data["submission_id"]}.xlsx'

    return file, filename, content_type
