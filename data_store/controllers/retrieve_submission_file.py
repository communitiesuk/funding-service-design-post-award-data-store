from botocore.exceptions import ClientError
from werkzeug.datastructures import FileStorage

from config import Config
from data_store.aws import get_file
from data_store.db.entities import Fund, Programme, ProgrammeJunction, Submission


def retrieve_submission_file(submission_id) -> FileStorage:
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
        raise RuntimeError(f"Could not find a submission that matches submission_id {submission_id}")

    try:
        file, meta_data, content_type = get_file(Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, object_name)
    except ClientError as error:
        if error.response["Error"]["Code"] == "NoSuchKey":
            raise FileNotFoundError(
                (
                    f"Submission {submission_id} exists in the database "
                    f"but could not find the related file {object_name} on S3."
                ),
            ) from error
        raise error

    filename = meta_data["filename"]
    # Check against Round 4 submission files which were all saved with 'ingest_spreadsheet' as the submission_filename
    if filename == "ingest_spreadsheet":
        filename = f'{meta_data["programme_name"]} - {meta_data["submission_id"]}.xlsx'

    return FileStorage(file, content_type=content_type, filename=filename)
