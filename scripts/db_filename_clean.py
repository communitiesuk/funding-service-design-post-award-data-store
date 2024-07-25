from sqlalchemy import Select  # type: ignore

from app import app
from data_store.db import db
from data_store.db.entities import Submission


def db_filename_clean():
    """
    We found some submissions where the submission_filename was erroneously saved with URL encoded characters.

    This script will tidy up any submissions where the submission_filename starts and/or ends with '%22',
    which would affect the user experience when downloading the file.

    To run the script from CLI, run the following (if running locally you'll need to add FLASK_ENV=development):
    python -m scripts.db_filename_clean
    """

    query = Select(Submission.id, Submission.submission_filename).filter(
        Submission.submission_filename.contains("%22", autoescape=True)
    )
    submissions = db.session.execute(query).all()
    print(str(query))
    print(submissions)

    for id, submission_filename in submissions:
        clean_filename = submission_filename.lstrip("%2").rstrip("%2")
        print(f"Updating submission {id} with filename {submission_filename} to {clean_filename}")
        db.session.query(Submission).filter(Submission.id == id).update({"submission_filename": clean_filename})
    db.session.commit()
    print("Update complete")


if __name__ == "__main__":
    with app.app_context():
        db_filename_clean()
