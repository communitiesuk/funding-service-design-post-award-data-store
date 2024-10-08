from sqlalchemy import func
from werkzeug.datastructures import FileStorage

from data_store.const import EXCEL_MIMETYPE
from data_store.controllers.ingest import ingest
from data_store.db.entities import Submission


class TestReingestFile:
    def test_success(
        self,
        test_client_reset,
        towns_fund_round_3_success_file_path,
        test_buckets,
        mock_sentry_metrics,
        admin_test_client,
    ):
        with open(towns_fund_round_3_success_file_path, "rb") as tf_r3:
            ingest(
                fund_name="Towns Fund",
                reporting_round=3,
                do_load=True,
                excel_file=FileStorage(tf_r3, content_type=EXCEL_MIMETYPE),
            )
        submitted_at_before = Submission.query.with_entities(func.max(Submission.submission_date)).one()

        with open(towns_fund_round_3_success_file_path, "rb") as tf_r3:
            resp = admin_test_client.post(
                "/admin/reingest_file/",
                data={
                    "submission_id": "s-r03-1",  # also sneakily testing case-insensitivity
                    "excel_file": FileStorage(tf_r3, content_type=EXCEL_MIMETYPE),
                },
                follow_redirects=True,
            )
        assert resp.status_code == 200

        submitted_at_after = Submission.query.with_entities(func.max(Submission.submission_date)).one()
        assert submitted_at_before < submitted_at_after  # NS precision so shouldn't need to freeze time

    def test_no_matching_submission(
        self,
        test_client_reset,
        towns_fund_round_3_success_file_path,
        test_buckets,
        mock_sentry_metrics,
        admin_test_client,
    ):
        with open(towns_fund_round_3_success_file_path, "rb") as tf_r3:
            resp = admin_test_client.post(
                "/admin/reingest_file/",
                data={
                    "submission_id": "S-R03-999",
                    "excel_file": FileStorage(tf_r3, content_type=EXCEL_MIMETYPE),
                },
                follow_redirects=True,
            )
        assert resp.status_code == 200
        assert "Could not find a matching submission with ID S-R03-999" in resp.text
