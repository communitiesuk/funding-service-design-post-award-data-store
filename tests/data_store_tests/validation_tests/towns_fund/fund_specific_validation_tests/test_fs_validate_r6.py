from datetime import date

import pandas as pd
import pytest

from data_store.const import StatusEnum
from data_store.messaging.tf_messaging import TFMessages as msgs
from data_store.validation.towns_fund.fund_specific_validation.fs_validate_r6 import (
    validate_project_progress,
)


@pytest.mark.parametrize(
    "project_delivery_status, start_date, expected_failures",
    [
        (StatusEnum.NOT_YET_STARTED, date(2024, 9, 29), 1),  # Before end of reporting period
        (StatusEnum.NOT_YET_STARTED, date(2024, 9, 30), 1),  # At end of reporting period
        (StatusEnum.NOT_YET_STARTED, date(2024, 10, 1), 0),  # After end of reporting period
        (StatusEnum.NOT_YET_STARTED, None, 0),  # No start date
        (StatusEnum.ONGOING_ON_TRACK, date(2024, 9, 29), 0),  # Project not marked as not yet started
    ],
)
def test_validate_project_progress(
    project_delivery_status: StatusEnum,
    start_date: date,
    expected_failures: int,
):
    workbook = {
        "Place Details": pd.DataFrame(
            {
                "question": ["Are you filling this in for a Town Deal or Future High Street Fund?"],
                "answer": ["Town_Deal"],
            },
        ),
        "Project Progress": pd.DataFrame(
            index=[0],
            data=[
                {
                    "project_id": "TD-ABC-01",
                    "delivery_status": project_delivery_status,
                    "start_date": pd.Timestamp(start_date),
                    "leading_factor_of_delay": "Some delay",
                    "delivery_stage": "Planning",
                }
            ],
        ),
    }
    failures = validate_project_progress(workbook, reporting_round=6)
    assert len(failures) == expected_failures
    if expected_failures > 0:
        failure = failures[0]
        assert failure.table == "Project Progress"
        assert failure.section == "Projects Progress Summary"
        assert failure.column == "start_date"
        assert failure.message == msgs.DATA_MISMATCH_PROJECT_START
        assert failure.row_index == 0


def test_validate_project_progress_multiple_projects():
    """Test validation with multiple projects, ensuring it only fails where appropriate."""
    past_date = date(2024, 9, 29)
    future_date = date(2024, 10, 1)
    workbook = {
        "Place Details": pd.DataFrame(
            {
                "question": ["Are you filling this in for a Town Deal or Future High Street Fund?"],
                "answer": ["Town_Deal"],
            },
        ),
        "Project Progress": pd.DataFrame(
            index=[0, 1, 2],
            data=[
                {
                    "project_id": "TD-ABC-01",
                    "delivery_status": StatusEnum.NOT_YET_STARTED,
                    "start_date": pd.Timestamp(past_date),
                    "leading_factor_of_delay": "Some delay",
                    "delivery_stage": "Planning",
                },
                {
                    "project_id": "TD-ABC-02",
                    "delivery_status": StatusEnum.NOT_YET_STARTED,
                    "start_date": pd.Timestamp(future_date),
                    "leading_factor_of_delay": "Some delay",
                    "delivery_stage": "Planning",
                },
                {
                    "project_id": "TD-ABC-03",
                    "delivery_status": StatusEnum.ONGOING_ON_TRACK,
                    "start_date": pd.Timestamp(past_date),
                    "leading_factor_of_delay": "No delay",
                    "delivery_stage": "Planning",
                },
            ],
        ),
    }
    failures = validate_project_progress(workbook, reporting_round=6)
    assert len(failures) == 1
    failure = failures[0]
    assert failure.row_index == 0
    assert failure.message == msgs.DATA_MISMATCH_PROJECT_START
