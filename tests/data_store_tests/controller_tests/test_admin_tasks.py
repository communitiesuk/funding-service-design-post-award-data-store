from pathlib import Path

import pandas as pd
import pytest
from pandas.testing import assert_frame_equal
from werkzeug.datastructures import FileStorage

from config import Config
from data_store.aws import _S3_CLIENT
from data_store.const import EXCEL_MIMETYPE
from data_store.controllers.admin_tasks import reingest_file, reingest_files
from data_store.controllers.ingest import ingest
from data_store.db import db
from data_store.db.entities import Submission


@pytest.fixture(scope="module")
def reingest_submission_ids_file_path():
    """Filepath to text file with line-separated submission IDs for reingesting."""
    filepath = Path(__file__).parent / "mock_admin_tasks_files" / "mock_reingest_submission_ids.txt"
    yield filepath


def test_reingest_file(
    test_client_reset, test_buckets, towns_fund_round_3_file_success, towns_fund_round_3_success_file_path, capfd
):
    """
    Tests successful reingestion of a single local submission file.
    """
    ingest(
        fund_name="Towns Fund",
        reporting_round=3,
        do_load=True,
        excel_file=FileStorage(towns_fund_round_3_file_success, content_type=EXCEL_MIMETYPE),
    )
    db.session.close()  # Close the existing db session before re-ingesting the file

    reingest_file(towns_fund_round_3_success_file_path, "S-R03-1")
    out, error = capfd.readouterr()
    assert out.strip() == ("Successfully re-ingested submission S-R03-1")


def test_reingest_files(
    test_client_reset,
    test_buckets,
    pathfinders_round_1_file_success,
    towns_fund_round_3_file_success,
    reingest_submission_ids_file_path,
):
    """
    Tests reingestiong of multiple submission files stored in S3, the submission_ids of which are
    provided by a line-separated list in a text file.

    The test mocks 3 potential scenarios in the reingestion - a successful reingestion, an instance of a submission
    existing in the database but not in s3, and a failed reingestion due to a submission not existing in the database.

    The expected output is a DataFrame with the submission_id, reporting_round, success status, and the
    errors encountered.
    """
    ingest(
        fund_name="Towns Fund",
        reporting_round=3,
        do_load=True,
        excel_file=FileStorage(towns_fund_round_3_file_success, content_type=EXCEL_MIMETYPE),
    )
    ingest(
        fund_name="Pathfinders",
        reporting_round=1,
        do_load=True,
        excel_file=FileStorage(pathfinders_round_1_file_success, content_type=EXCEL_MIMETYPE),
    )

    # Delete the Pathfinders submission in S3 in order to simulate case where submission exists in DB but not in S3
    pf_submission_uuid = str(
        Submission.query.filter(Submission.submission_id == "S-PF-R01-1")
        .with_entities(Submission.id)
        .distinct()
        .one()[0]
    )
    _S3_CLIENT.delete_object(Bucket=Config.AWS_S3_BUCKET_SUCCESSFUL_FILES, Key=f"PF/{pf_submission_uuid}")

    db.session.close()  # Close the existing db session before re-ingesting the file

    with open(reingest_submission_ids_file_path, "r") as file:
        output_df = reingest_files(file)
        expected_output_df = pd.DataFrame(
            {
                "submission_id": ["S-R03-1", "S-PF-R01-1", "S-R04-1"],
                "reporting_round": [3, 1, 4],
                "Success": [True, False, False],
                "Errors": [
                    "",
                    {
                        "Error": "Submission S-PF-R01-1 exists in the database but could not find "
                        f"the related file PF/{pf_submission_uuid} on S3."
                    },
                    {"Error": "Submission S-R04-1 not found in the database."},
                ],
            }
        )
        assert_frame_equal(output_df, expected_output_df)
