import enum
import functools
from collections import Counter

import sentry_sdk.metrics
from flask import g
from werkzeug.datastructures import FileStorage


class FundingMetrics(enum.StrEnum):
    """Tracks all the metrics that we track/emit from this app.

    Every metric defined here should have a corresponding method on the MetricsReporter class below so that
    we keep a central view of all metrics we emit and what tags/etc they take.
    """

    SUBMISSION = "submission"
    SUBMISSION_INGEST_RESULT = "submission-ingest-result"
    SUBMISSION_VALIDATION_ERRORS = "submission-validation-errors"
    SUBMISSION_VALIDATION_ERRORS_TOTAL = "submission-validation-errors-total"


class MetricsReporter:
    def __init__(self):
        self.logger = None

    def init_app(self, app):
        self.logger = app.logger

    def track_report_submission(self, fund: str, reporting_round: int, organisation_name: str):
        sentry_sdk.metrics.incr(
            FundingMetrics.SUBMISSION,
            1,
            tags={"fund": fund, "reporting_round": reporting_round, "organisation": organisation_name},
        )

    def track_report_submission_ingest_result(
        self, fund: str, reporting_round: int, organisation_name: str, result: str
    ):
        if result not in {"success", "invalid", "error"}:
            self.logger.warning(
                "Rejecting metric `%(metric_name)s` with invalid result: %(result)s",
                dict(metric_name=FundingMetrics.SUBMISSION_INGEST_RESULT, result=result),
            )
            return

        sentry_sdk.metrics.incr(
            FundingMetrics.SUBMISSION_INGEST_RESULT,
            1,
            tags={
                "fund": fund,
                "reporting_round": reporting_round,
                "organisation": organisation_name,
                "result": result,
            },
        )

    def track_report_submission_validation_errors_total(
        self, fund: str, reporting_round: int, organisation_name: str, num_validation_errors: int
    ):
        sentry_sdk.metrics.distribution(
            FundingMetrics.SUBMISSION_VALIDATION_ERRORS_TOTAL,
            num_validation_errors,
            tags={"fund": fund, "reporting_round": reporting_round, "organisation": organisation_name},
        )

    def track_report_submission_validation_errors(
        self, fund: str, reporting_round: int, organisation_name: str, validation_error_counts: Counter
    ):
        for validation_error, count in validation_error_counts.items():
            sentry_sdk.metrics.distribution(
                FundingMetrics.SUBMISSION_VALIDATION_ERRORS,
                count,
                tags={
                    "fund": fund,
                    "reporting_round": reporting_round,
                    "organisation": organisation_name,
                    "validation_error": validation_error,
                },
            )


metrics_reporter = MetricsReporter()


def capture_ingest_metrics(view_func):
    """Decorator for the `core.controllers.ingest` function below to track the outcome of a spreadsheet ingest.

    Reports on whether the submission succeeded, raised validation errors, or had some other kind of (probably internal)
    server error. Tracks the number of validation errors raised, if any, and splits to track each kind of validation
    error too.

    There's a risk of this being too many dimensions for Sentry when we're mega-multi-fund and have lots of reporting
    rounds, but that'll be a nice problem to have. If it happens we'll have to deal with it.
    See also: https://docs.sentry.io/product/metrics/#cardinality
    """

    @functools.wraps(view_func)
    def decorator(
        excel_file: FileStorage,
        fund_name: str,
        reporting_round: int,
        do_load: bool = True,
        submitting_account_id: str | None = None,
        submitting_user_email: str | None = None,
        auth: dict[str, tuple[str, ...]] | None = None,
    ):
        # `ingest` function should set correct values of these three dimensions as part of processing
        g.fund_name = "unknown"
        g.reporting_round = -1
        g.organisation_name = "unknown"

        retval: tuple[dict, int] = view_func(
            excel_file=excel_file,
            fund_name=fund_name,
            reporting_round=reporting_round,
            do_load=do_load,
            submitting_account_id=submitting_account_id,
            submitting_user_email=submitting_user_email,
            auth=auth,
        )

        try:
            metrics_reporter.track_report_submission(
                fund=g.fund_name, reporting_round=g.reporting_round, organisation_name=g.organisation_name
            )
            metrics_reporter.track_report_submission_ingest_result(
                fund=g.fund_name,
                reporting_round=g.reporting_round,
                organisation_name=g.organisation_name,
                result="success" if retval[1] == 200 else "invalid" if retval[1] == 400 else "error",
            )
            validation_errors = retval[0].get("validation_errors", [])
            error_counts = Counter(
                [
                    error
                    for error, cells in map(
                        lambda error_dict: (error_dict["description"], (error_dict["cell_index"] or "").split(", ")),
                        validation_errors,
                    )
                    for _ in cells
                ]
            )
            metrics_reporter.track_report_submission_validation_errors_total(
                fund=g.fund_name,
                reporting_round=g.reporting_round,
                organisation_name=g.organisation_name,
                num_validation_errors=sum(error_counts.values()),
            )
            metrics_reporter.track_report_submission_validation_errors(
                fund=g.fund_name,
                reporting_round=g.reporting_round,
                organisation_name=g.organisation_name,
                validation_error_counts=error_counts,
            )
        except Exception:  # noqa
            # If some error happens logging sentry metrics, let's not die - we still want to respond to the request.
            pass

        return retval

    return decorator
