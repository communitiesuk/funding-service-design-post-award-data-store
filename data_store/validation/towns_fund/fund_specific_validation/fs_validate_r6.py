from datetime import datetime

import pandas as pd

from data_store.const import StatusEnum
from data_store.messaging.tf_messaging import TFMessages as msgs
from data_store.transformation.towns_fund import common
from data_store.validation.towns_fund.failures.user import GenericFailure
from data_store.validation.towns_fund.fund_specific_validation.fs_validate_r4 import (
    validate as validate_r4,
)


def validate(
    data_dict: dict[str, pd.DataFrame],
    original_workbook: dict[str, pd.DataFrame],
    reporting_round: int,
) -> list[GenericFailure]:
    """Top-level Towns Fund Round 6 specific validation."""
    # Start with validations from Round 4
    validation_failures = validate_r4(data_dict, original_workbook, reporting_round)

    # Add new validations specific to Round 6
    project_progress_failures = validate_project_progress(data_dict, reporting_round)
    validation_failures.extend(project_progress_failures)

    return validation_failures


def validate_project_progress(data_dict: dict[str, pd.DataFrame], reporting_round: int) -> list[GenericFailure]:
    """Validates the Project Progress table for Round 6 submissions."""
    project_progress_df = data_dict["Project Progress"]
    not_started_mask = project_progress_df["Project Delivery Status"] == StatusEnum.NOT_YET_STARTED
    not_started_rows = project_progress_df[not_started_mask]
    _, observation_period_end_date = common.get_reporting_period_start_end(reporting_round)
    failures = []
    for idx, row in not_started_rows.iterrows():
        start_date = row["Start Date"]
        if pd.isnull(start_date) or not isinstance(start_date, datetime):
            continue
        if start_date.date() <= observation_period_end_date.date():
            failures.append(
                GenericFailure(
                    table="Project Progress",
                    section="Projects Progress Summary",
                    column="Start Date",
                    message=msgs.DATA_MISMATCH_PROJECT_START,
                    row_index=idx,  # type: ignore[arg-type]
                )
            )
    return failures
