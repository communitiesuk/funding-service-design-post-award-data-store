import datetime

from data_store.db.entities import Fund, ReportingRound


class TestReportingRound:
    def test_create_reporting_round(self, seeded_test_client, admin_test_client):
        fund = Fund.query.first()

        data = {
            "fund": str(fund.id),
            "round_number": "999",
            "observation_period_start": "2024-01-01",
            "observation_period_end": "2024-01-31",
            "submission_period_start": "2024-02-01",
            "submission_period_end": "2024-02-29",
        }

        resp = admin_test_client.post("/admin/reportinground/new/?url=/admin/reportinground/", data=data)

        assert resp.status_code == 302
        assert resp.location == "/admin/reportinground/"

        rr = ReportingRound.query.join(Fund).filter(Fund.id == fund.id, ReportingRound.round_number == 999).one()
        assert rr.observation_period_start == datetime.datetime(2024, 1, 1, 0, 0, 0)
        assert rr.submission_period_start == datetime.datetime(2024, 2, 1, 0, 0, 0)

        # End dates should be set to 23:59:59 automatically
        assert rr.observation_period_end == datetime.datetime(2024, 1, 31, 23, 59, 59)
        assert rr.submission_period_end == datetime.datetime(2024, 2, 29, 23, 59, 59)
