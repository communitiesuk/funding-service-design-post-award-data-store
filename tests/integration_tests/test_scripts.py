from config import Config
from core.aws import _S3_CLIENT
from core.db.entities import Submission
from scripts.migrate_db_files_to_s3 import migrate_db_files_to_s3


def test_migrate_db_files_to_s3(seeded_test_client, test_buckets):
    """
    First runs mirror_db_to_s3 to upload all files in the db to S3 then checks that the file stored in S3 is identical
    to the one in the db
    """
    migrate_db_files_to_s3()

    uuid, submission_id, filename, filebytes = Submission.query.with_entities(
        Submission.id, Submission.submission_id, Submission.submission_filename, Submission.submission_file
    ).one()

    response = _S3_CLIENT.get_object(Bucket=Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, Key=f"HS/{uuid}")
    metadata = response["Metadata"]

    assert response["Body"].read() == filebytes
    assert metadata["submission_id"] == submission_id
    assert metadata["filename"] == filename
    assert metadata["programme_name"] == "Leaky Cauldron regeneration"
