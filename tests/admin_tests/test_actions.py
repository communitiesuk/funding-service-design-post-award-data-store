from sqlalchemy import func
from werkzeug.datastructures import FileStorage

from data_store.const import EXCEL_MIMETYPE
from data_store.controllers.ingest import ingest
from data_store.db.entities import Submission


class TestReingestS3AdminView:
    # TODO: add some tests
    ...


class TestReingestFileAdminView:
    # NOTE[RESP_CLOSE]
    # Flask's test client sometimes does not close large files passed to it correctly, so we force them to close
    # here. Not doing this manually can make pytest throw a ResourceWarning, which gets flagged as an error.
    # See also:
    #    https://github.com/pallets/werkzeug/issues/1785
    #    https://github.com/pallets/werkzeug/pull/2041

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

        resp.close()  # See note `RESP_CLOSE` near top of class

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

            resp.close()  # See note `RESP_CLOSE` near top of class

        assert resp.status_code == 200
        assert "Could not find a matching submission with ID S-R03-999" in resp.text


class TestRetrieveSubmissionAdminView:
    # TODO: add some tests
    ...


class TestRetrieveFailedSubmissionAdminView:
    # TODO: add some tests
    ...
