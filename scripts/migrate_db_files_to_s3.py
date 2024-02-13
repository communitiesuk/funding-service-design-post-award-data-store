from io import BytesIO

from sqlalchemy import Select
from werkzeug.datastructures import FileStorage

from app import app
from core.const import EXCEL_MIMETYPE
from core.controllers.ingest import save_submission_file_s3
from core.db import db
from core.db.entities import Submission

# TODO: [FMD-227] Remove submission files from db


def migrate_db_files_to_s3():
    """
    This script will pull all save submission files from the database and upload them to S3
    with the correct naming convention.

    To run locally, a number of environment variables need to be set with the command as
    these are normally pulled in when the Flask app is running. These shouldn't be needed when
    running the script on a deployed environment:

    FLASK_ENV=development
    AWS_S3_BUCKET_SUCCESSFUL_FILES=data-store-successful-files-dev
    AWS_REGION=eu-central-1
    AWS_ACCESS_KEY_ID=test
    AWS_SECRET_ACCESS_KEY=test
    AWS_ENDPOINT_OVERRIDE=http://127.0.0.1:4566/

    To run the script from CLI (along with setting env vars as above):
    python -m scripts.migrate-db-files-to-s3
    """

    query = Select(Submission.submission_id, Submission.submission_file, Submission.submission_filename).where(
        Submission.submission_file != None  # noqa
    )

    submission_files = db.session.execute(query).all()

    for submission_id, filebytes, filename in submission_files:
        file = FileStorage(BytesIO(filebytes), filename, content_type=EXCEL_MIMETYPE)
        try:
            save_submission_file_s3(file, submission_id)
        except Exception as error:
            print(f"{submission_id} upload to S3 failed")
            print(error)
            raise error
        print(f"{submission_id} successfully saved to S3")
    print("All Submission Files successfully uploaded to S3.")


if __name__ == "__main__":
    with app.app_context():
        migrate_db_files_to_s3()
