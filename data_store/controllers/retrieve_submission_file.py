from config import Config
from data_store.aws import create_presigned_url, get_file_metadata
from data_store.db.entities import Fund, Programme, ProgrammeJunction, Submission


def retrieve_submission_file(submission_id) -> str:
    """Handle the download request and return the originally submitted spreadsheet.

    Select file by:
    - submission_id

    :return: Presigned URL to the file as string. This can easily be reverted to returning a
    Flask response object containing the requested spreadsheet on the introduction of an admin interface.

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
        metadata = get_file_metadata(Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, object_name)
    except FileNotFoundError as error:
        raise FileNotFoundError(
            (
                f"Submission {submission_id} exists in the database "
                f"but could not find the related file {object_name} on S3."
            ),
        ) from error

    filename = metadata["filename"]
    # Check against Round 4 submission files which were all saved with 'ingest_spreadsheet' as the submission_filename
    if filename == "ingest_spreadsheet":
        filename = f'{metadata["programme_name"]} - {metadata["submission_id"]}.xlsx'

    presigned_url = create_presigned_url(
        bucket_name=Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, file_key=object_name, filename=filename
    )
    return presigned_url
