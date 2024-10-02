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
                "Question": ["Are you filling this in for a Town Deal or Future High Street Fund?"],
                "Answer": ["Town_Deal"],
            },
        ),
        "Project Progress": pd.DataFrame(
            index=[0],
            data=[
                {
                    "Project ID": "TD-ABC-01",
                    "Project Delivery Status": project_delivery_status,
                    "Start Date": pd.Timestamp(start_date),
                    "Leading Factor of Delay": "Some delay",
                    "Current Project Delivery Stage": "Planning",
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
        assert failure.column == "Start Date"
        assert failure.message == msgs.DATA_MISMATCH_PROJECT_START
        assert failure.row_index == 0


def test_validate_project_progress_multiple_projects():
    """Test validation with multiple projects, ensuring it only fails where appropriate."""
    past_date = date(2024, 9, 29)
    future_date = date(2024, 10, 1)
    workbook = {
        "Place Details": pd.DataFrame(
            {
                "Question": ["Are you filling this in for a Town Deal or Future High Street Fund?"],
                "Answer": ["Town_Deal"],
            },
        ),
        "Project Progress": pd.DataFrame(
            index=[0, 1, 2],
            data=[
                {
                    "Project ID": "TD-ABC-01",
                    "Project Delivery Status": StatusEnum.NOT_YET_STARTED,
                    "Start Date": pd.Timestamp(past_date),
                    "Leading Factor of Delay": "Some delay",
                    "Current Project Delivery Stage": "Planning",
                },
                {
                    "Project ID": "TD-ABC-02",
                    "Project Delivery Status": StatusEnum.NOT_YET_STARTED,
                    "Start Date": pd.Timestamp(future_date),
                    "Leading Factor of Delay": "Some delay",
                    "Current Project Delivery Stage": "Planning",
                },
                {
                    "Project ID": "TD-ABC-03",
                    "Project Delivery Status": StatusEnum.ONGOING_ON_TRACK,
                    "Start Date": pd.Timestamp(past_date),
                    "Leading Factor of Delay": "No delay",
                    "Current Project Delivery Stage": "Planning",
                },
            ],
        ),
    }
    failures = validate_project_progress(workbook, reporting_round=6)
    assert len(failures) == 1
    failure = failures[0]
    assert failure.row_index == 0
    assert failure.message == msgs.DATA_MISMATCH_PROJECT_START
