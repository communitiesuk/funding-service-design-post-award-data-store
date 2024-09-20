import json

import pandas as pd
import requests
from botocore.exceptions import ClientError
from sqlalchemy.orm.exc import NoResultFound
from werkzeug.datastructures import FileStorage

from config import Config
from data_store.aws import get_file
from data_store.const import EXCEL_MIMETYPE
from data_store.controllers.ingest import ingest
from data_store.db import db
from data_store.db.entities import Submission


def reingest_file(filepath, submission_id):
    """
    Re-ingests a submission file saved locally eg. in the case of a manual data correction.

    :param filepath (str): The path to the file to be re-ingested.
    :param submission_id (int): The ID of the submission.

    :raises NoResultFound: If no submission is found in the database with the given submission ID.

    :return: No return type - result of reingest operation (success or failure with associated response data
    which may include validation errors or other errors) instead printed to the console as this function
    is only called by a Flask CLI command which is executed manually in a terminal.
    """
    with open(filepath, "rb") as file:
        filename = str(filepath).split("/")[-1]
        file_storage = FileStorage(stream=file, filename=filename, content_type=EXCEL_MIMETYPE)

        try:
            submission = Submission.query.filter_by(submission_id=submission_id).one()
        except NoResultFound as error:
            raise error

        if submission:
            fund_name = (
                "Pathfinders" if submission.programme_junction.programme_ref.fund.fund_code == "PF" else "Towns Fund"
            )
            reporting_round = submission.reporting_round.round_number
            account_id, user_email = submission.submitting_account_id, submission.submitting_user_email
            db.session.close()  # ingest (specifically `populate_db`) wants to start a new clean session/transaction

            response_data, status_code = ingest(
                dict(
                    fund_name=fund_name,
                    reporting_round=reporting_round,
                    auth=None,  # Don't run any auth checks because we're admins
                    do_load=True,
                    submitting_account_id=account_id,
                    submitting_user_email=user_email,
                ),
                file_storage,
            )
            if status_code == 200:
                print(f"Successfully re-ingested submission {submission.submission_id}")
            else:
                print(f"Issues re-ingesting submission {submission.submission_id}: {status_code} {response_data}")


def reingest_files(file):
    """
    Re-ingests one or more files that are stored in the 'sucessful files' S3 bucket.

    :param file: A text file containing one or more line-separated submission IDs.

    :return pandas.DataFrame: A DataFrame containing the re-ingestion results, including submission ID,
    reporting round, success status, and any errors encountered during re-ingestion.
    """
    output_df = pd.DataFrame(columns=["submission_id", "reporting_round", "Success", "Errors"])
    for submission_id in file:
        submission_id = submission_id.strip()
        reporting_round = int(submission_id.split("-")[-2].strip("R"))
        print(f"Re-ingesting Submission {submission_id}")

        # Initialise variables at the start of each loop to prevent bleeding over from previous iterations
        submission_file = None
        submission = None
        errors = ""
        success = False
        try:
            submission = Submission.query.filter_by(submission_id=submission_id).one()
        except NoResultFound as error:
            print(error)
            errors = {"Error": f"Submission {submission_id} not found in the database."}

        if submission:
            submission_uuid = submission.id
            fund_type = submission.programme_junction.programme_ref.fund.fund_code
            object_name = f"{fund_type}/{str(submission_uuid)}"

            try:
                submission_file, metadata, content_type = get_file(Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, object_name)
            except ClientError as error:
                print(error, error.response)
                if error.response["Error"]["Code"] == "NoSuchKey":
                    errors = {
                        "Error": f"Submission {submission_id} exists in the database "
                        f"but could not find the related file {object_name} on S3."
                    }
                else:
                    errors = json.dumps(error.response)
            if submission_file:
                file_storage = FileStorage(
                    stream=submission_file, filename=metadata["filename"], content_type=content_type
                )
                fund_name = (
                    "Pathfinders"
                    if submission.programme_junction.programme_ref.fund.fund_code == "PF"
                    else "Towns Fund"
                )
                reporting_round = submission.reporting_round.round_number
                account_id, user_email = submission.submitting_account_id, submission.submitting_user_email
                db.session.close()  # ingest (specifically `populate_db`) wants to start a new clean session/transaction

                response_data, status_code = ingest(
                    dict(
                        fund_name=fund_name,
                        reporting_round=reporting_round,
                        auth=None,  # Don't run any auth checks because we're admins
                        do_load=True,
                        submitting_account_id=account_id,
                        submitting_user_email=user_email,
                    ),
                    file_storage,
                )
                if status_code == 200:
                    print(f"Successfully re-ingested submission {submission.submission_id}")
                    success = status_code == requests.codes.ok
                    errors = ""
                else:
                    print(f"Issues re-ingesting submission {submission.submission_id}: {response_data}")
                    success = False
                    errors = json.dumps(response_data)

        output_df.loc[len(output_df)] = {
            "submission_id": submission_id,
            "reporting_round": reporting_round,
            "Success": success,
            "Errors": errors,
        }
    return output_df
