from typing import Optional

from config import Config
from data_store.aws import create_presigned_url, get_file_header
from data_store.db.entities import Fund, Organisation, Programme, ProgrammeJunction, ReportingRound, Submission


def retrieve_submission_file(submission_id) -> str:
    """Handle the download request and return a presigned S3 URL to the originally submitted spreadsheet.

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

    file_header = get_file_header(
        bucket_name=Config.AWS_S3_BUCKET_SUCCESSFUL_FILES,
        file_key=object_name,
    )

    metadata = file_header["metadata"]
    filename = metadata["filename"]

    # Check against Round 4 submission files which were all saved with 'ingest_spreadsheet' as the submission_filename
    if filename == "ingest_spreadsheet":
        filename = f"{get_custom_file_name(uuid)}.xlsx"

    presigned_url = create_presigned_url(
        bucket_name=Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, file_key=object_name, filename=filename
    )

    return presigned_url


def get_custom_file_name(
    submission_id: str,
    fallback_date: Optional[str] = None,
    fallback_fund_code: Optional[str] = None,
    fallback_org_name: Optional[str] = None,
) -> str:
    submission_info = (
        Programme.query.join(ProgrammeJunction)
        .join(Submission)
        .join(Fund)
        .join(Organisation)
        .join(ReportingRound, Submission.reporting_round_id == ReportingRound.id)
        .filter(Submission.id == submission_id)
        .with_entities(
            Submission.submission_id,
            Fund.fund_code,
            Submission.submission_date,
            ReportingRound.observation_period_start,
            ReportingRound.observation_period_end,
            Organisation.organisation_name,
        )
        .one_or_none()
    )

    if submission_info:
        date = submission_info.submission_date.strftime("%Y-%m-%d")
        start_date = submission_info.observation_period_start.strftime("%b%Y")
        end_date = submission_info.observation_period_end.strftime("%b%Y")

        file_name = f"{date}-{submission_info.fund_code}-{submission_info.organisation_name}-{start_date}-{end_date}"
    else:
        date = fallback_date
        fund_code = fallback_fund_code
        org_name = fallback_org_name
        file_name = f"{date}-{fund_code}-{org_name}-{submission_id}"

    return file_name.replace(" ", "-").lower()
