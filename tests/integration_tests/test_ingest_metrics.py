import json
from unittest import mock

from werkzeug.datastructures import FileStorage

from core.const import EXCEL_MIMETYPE
from core.controllers.ingest import ingest
from core.db import db
from core.metrics import FundingMetrics


def test_sentry_metrics_emitted_from_ingest_endpoint(
    test_client_reset,
    towns_fund_round_3_file_success,
    towns_fund_round_4_round_agnostic_failures,
    pathfinders_round_1_file_success,
    test_buckets,
    mock_sentry_metrics,
):
    """Runs some ingest cycles across different funds and asserts that the expected sentry metrics have been
    generated for them, so that we can get reporting on successful/failed uploads and the kind of failures that were
    hit.
    """

    ingest(
        body={
            "fund_name": "Towns Fund",
            "reporting_round": 3,
            "do_load": True,
        },
        excel_file=FileStorage(towns_fund_round_3_file_success, content_type=EXCEL_MIMETYPE),
    )

    ingest(
        body={
            "fund_name": "Towns Fund",
            "reporting_round": 4,
            "auth": json.dumps(
                {
                    "Place Names": ["Blackfriars - Northern City Centre"],
                    "Fund Types": ["Town_Deal", "Future_High_Street_Fund"],
                }
            ),
            "do_load": False,
        },
        excel_file=FileStorage(towns_fund_round_4_round_agnostic_failures, content_type=EXCEL_MIMETYPE),
    )

    ingest(
        body={
            "fund_name": "Pathfinders",
            "reporting_round": 1,
            "auth": json.dumps(
                {
                    "Programme": [
                        "Bolton Council",
                    ],
                    "Fund Types": [
                        "Pathfinders",
                    ],
                }
            ),
            "do_load": True,
        },
        excel_file=FileStorage(pathfinders_round_1_file_success, content_type=EXCEL_MIMETYPE),
    )

    db.session.commit()

    # Validate sentry metrics have been collected
    assert mock_sentry_metrics.incr.call_args_list == [
        mock.call(
            FundingMetrics.SUBMISSION,
            1,
            tags={"fund": "Towns Fund", "reporting_round": 3, "organisation": "USS Enterprise"},
        ),
        mock.call(
            FundingMetrics.SUBMISSION_INGEST_RESULT,
            1,
            tags={"fund": "Towns Fund", "reporting_round": 3, "organisation": "USS Enterprise", "result": "success"},
        ),
        mock.call(
            FundingMetrics.SUBMISSION,
            1,
            tags={"fund": "Towns Fund", "reporting_round": 4, "organisation": "Worcester City Council"},
        ),
        mock.call(
            FundingMetrics.SUBMISSION_INGEST_RESULT,
            1,
            tags={
                "fund": "Towns Fund",
                "reporting_round": 4,
                "organisation": "Worcester City Council",
                "result": "invalid",
            },
        ),
        mock.call(
            FundingMetrics.SUBMISSION,
            1,
            tags={"fund": "Pathfinders", "reporting_round": 1, "organisation": "Bolton Council"},
        ),
        mock.call(
            FundingMetrics.SUBMISSION_INGEST_RESULT,
            1,
            tags={"fund": "Pathfinders", "reporting_round": 1, "organisation": "Bolton Council", "result": "success"},
        ),
    ]
    assert mock_sentry_metrics.distribution.call_args_list == [
        mock.call(
            FundingMetrics.SUBMISSION_VALIDATION_ERRORS_TOTAL,
            0,
            tags={"fund": "Towns Fund", "reporting_round": 3, "organisation": "USS Enterprise"},
        ),
        mock.call(
            FundingMetrics.SUBMISSION_VALIDATION_ERRORS_TOTAL,
            4,
            tags={"fund": "Towns Fund", "reporting_round": 4, "organisation": "Worcester City Council"},
        ),
        mock.call(
            FundingMetrics.SUBMISSION_VALIDATION_ERRORS,
            1,
            tags={
                "fund": "Towns Fund",
                "reporting_round": 4,
                "organisation": "Worcester City Council",
                "validation_error": (
                    "You’ve entered your own content, instead of selecting from the dropdown list provided. Select "
                    + "an option from the dropdown list."
                ),
            },
        ),
        mock.call(
            FundingMetrics.SUBMISSION_VALIDATION_ERRORS,
            1,
            tags={
                "fund": "Towns Fund",
                "reporting_round": 4,
                "organisation": "Worcester City Council",
                "validation_error": "The cell is blank but is required. Enter a value, even if it’s zero.",
            },
        ),
        mock.call(
            FundingMetrics.SUBMISSION_VALIDATION_ERRORS,
            1,
            tags={
                "fund": "Towns Fund",
                "reporting_round": 4,
                "organisation": "Worcester City Council",
                "validation_error": (
                    "You entered text instead of a number. Remove any units of measurement and only use numbers, "
                    + "for example, 9."
                ),
            },
        ),
        mock.call(
            FundingMetrics.SUBMISSION_VALIDATION_ERRORS,
            1,
            tags={
                "fund": "Towns Fund",
                "reporting_round": 4,
                "organisation": "Worcester City Council",
                "validation_error": "You entered duplicate data. Remove or replace the duplicate data.",
            },
        ),
        mock.call(
            FundingMetrics.SUBMISSION_VALIDATION_ERRORS_TOTAL,
            0,
            tags={"fund": "Pathfinders", "reporting_round": 1, "organisation": "Bolton Council"},
        ),
    ]
