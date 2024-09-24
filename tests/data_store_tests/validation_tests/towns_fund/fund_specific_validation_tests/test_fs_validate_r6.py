from datetime import datetime, timedelta

import pandas as pd

from data_store.const import StatusEnum
from data_store.messaging.tf_messaging import TFMessages as msgs
from data_store.validation.towns_fund.fund_specific_validation.fs_validate_r6 import (
    validate_project_progress,
)


def test_validate_project_progress_start_date_in_past():
    """Test that validation fails when 'Project Delivery Status' is 'Not yet started' and 'Start Date' is in the
    past."""
    current_date = datetime.now().date()
    past_date = current_date - timedelta(days=1)
    project_progress_df = pd.DataFrame(
        index=[0],
        data=[
            {
                "Project ID": "TD-ABC-01",
                "Project Delivery Status": StatusEnum.NOT_YET_STARTED,
                "Start Date": pd.Timestamp(past_date),
                "Leading Factor of Delay": "Some delay",
                "Current Project Delivery Stage": "Planning",
            }
        ],
    )
    workbook = {"Project Progress": project_progress_df}
    failures = validate_project_progress(workbook)
    assert len(failures) == 1
    failure = failures[0]
    assert failure.table == "Project Progress"
    assert failure.section == "Projects Progress Summary"
    assert failure.column == "Start Date"
    assert failure.message == msgs.DATA_MISMATCH_PROJECT_START
    assert failure.row_index == 0


def test_validate_project_progress_start_date_today():
    """Test that validation fails when 'Project Delivery Status' is 'Not yet started' and 'Start Date' is today."""
    current_date = datetime.now().date()
    project_progress_df = pd.DataFrame(
        index=[0],
        data=[
            {
                "Project ID": "TD-ABC-01",
                "Project Delivery Status": StatusEnum.NOT_YET_STARTED,
                "Start Date": pd.Timestamp(current_date),
                "Leading Factor of Delay": "Some delay",
                "Current Project Delivery Stage": "Planning",
            }
        ],
    )
    workbook = {"Project Progress": project_progress_df}
    failures = validate_project_progress(workbook)
    assert len(failures) == 1
    failure = failures[0]
    assert failure.table == "Project Progress"
    assert failure.section == "Projects Progress Summary"
    assert failure.column == "Start Date"
    assert failure.message == msgs.DATA_MISMATCH_PROJECT_START
    assert failure.row_index == 0


def test_validate_project_progress_start_date_in_future():
    """Test that validation passes when 'Project Delivery Status' is 'Not yet started' and 'Start Date' is in the
    future."""
    current_date = datetime.now().date()
    future_date = current_date + timedelta(days=1)
    project_progress_df = pd.DataFrame(
        index=[0],
        data=[
            {
                "Project ID": "TD-ABC-01",
                "Project Delivery Status": StatusEnum.NOT_YET_STARTED,
                "Start Date": pd.Timestamp(future_date),
                "Leading Factor of Delay": "Some delay",
                "Current Project Delivery Stage": "Planning",
            }
        ],
    )
    workbook = {"Project Progress": project_progress_df}
    failures = validate_project_progress(workbook)
    assert len(failures) == 0


def test_validate_project_progress_status_not_not_yet_started():
    """Test that validation does not trigger when 'Project Delivery Status' is not 'Not yet started'."""
    current_date = datetime.now().date()
    past_date = current_date - timedelta(days=1)
    project_progress_df = pd.DataFrame(
        index=[0],
        data=[
            {
                "Project ID": "TD-ABC-01",
                "Project Delivery Status": StatusEnum.ONGOING_ON_TRACK,
                "Start Date": pd.Timestamp(past_date),
                "Leading Factor of Delay": "No delay",
                "Current Project Delivery Stage": "Planning",
            }
        ],
    )
    workbook = {"Project Progress": project_progress_df}
    failures = validate_project_progress(workbook)
    assert len(failures) == 0


def test_validate_project_progress_start_date_null():
    """Test that validation skips rows where 'Start Date' is null."""
    project_progress_df = pd.DataFrame(
        index=[0],
        data=[
            {
                "Project ID": "TD-ABC-01",
                "Project Delivery Status": StatusEnum.NOT_YET_STARTED,
                "Start Date": pd.NaT,  # Null Start Date
                "Leading Factor of Delay": "Some delay",
                "Current Project Delivery Stage": "Planning",
            }
        ],
    )
    workbook = {"Project Progress": project_progress_df}
    failures = validate_project_progress(workbook)
    assert not any(failure.message == msgs.DATA_MISMATCH_PROJECT_START for failure in failures)


def test_validate_project_progress_multiple_projects():
    """Test validation with multiple projects, ensuring it only fails where appropriate."""
    current_date = datetime.now().date()
    past_date = current_date - timedelta(days=1)
    future_date = current_date + timedelta(days=1)
    project_progress_df = pd.DataFrame(
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
    )
    workbook = {"Project Progress": project_progress_df}
    failures = validate_project_progress(workbook)
    assert len(failures) == 1
    failure = failures[0]
    assert failure.row_index == 0
    assert failure.message == msgs.DATA_MISMATCH_PROJECT_START
