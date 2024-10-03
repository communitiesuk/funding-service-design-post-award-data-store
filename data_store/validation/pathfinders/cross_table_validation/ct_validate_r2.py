"""
Module for performing cross-table validation checks on the input DataFrames extracted from the original Excel file.
These are checks that require data from multiple tables to be compared against each other. The checks are specific to
the Pathfinders round 2 reporting template.

Note: when creating error messages, the cell_index in the error message is calculated by adding 1 to the row index of
the breaching cell. This is because DataFrames are 0-indexed and Excel is not.
"""

import typing
from collections import namedtuple

import pandas as pd

from data_store.messaging import Message
from data_store.validation.pathfinders.consts import PFErrors
from data_store.validation.pathfinders.cross_table_validation import common
from data_store.validation.pathfinders.cross_table_validation.consts import PFC_REPORTING_PERIOD_LABELS_TO_DATES


def cross_table_validate(extracted_table_dfs: dict[str, pd.DataFrame]) -> list[Message]:
    """
    Perform cross-table validation checks on the input DataFrames extracted from the original Excel file. These are
    checks that require data from multiple tables to be compared against each other.

    :param extracted_table_dfs: Dictionary of DataFrames representing tables extracted from the original Excel file
    :return: List of error messages
    """
    error_messages = []
    error_messages.extend(_check_projects(extracted_table_dfs))
    error_messages.extend(_check_current_underspend(extracted_table_dfs))
    error_messages.extend(_check_intervention_themes_in_pfcs(extracted_table_dfs))
    error_messages.extend(_check_actual_forecast_reporting_period(extracted_table_dfs))
    return error_messages


def _check_projects(extracted_table_dfs: dict[str, pd.DataFrame]) -> list[Message]:
    """
    Check that the project names in the "Project progress", "Project location" and "Project finance changes" tables
    match those allowed for the organisation.

    :param extracted_table_dfs: Dictionary of DataFrames representing tables extracted from the original Excel file
    :return: List of error messages
    """
    project_details_df = extracted_table_dfs["Project details control"]
    programme_to_projects = {
        programme: project_details_df.loc[project_details_df["Local Authority"] == programme, "Full name"].tolist()
        for programme in project_details_df["Local Authority"].unique()
    }
    column_name_to_cell_indexes_letter = {
        "Project name": "B",
        "Project funding moved from": "C",
        "Project funding moved to": "G",
    }
    error_messages = []
    ProjectCheckConfig = namedtuple("ProjectCheckConfig", ["worksheet", "table_name", "project_name_column"])
    check_configs = [
        ProjectCheckConfig(worksheet="Progress", table_name="Project progress", project_name_column="Project name"),
        ProjectCheckConfig(
            worksheet="Project location", table_name="Project location", project_name_column="Project name"
        ),
        ProjectCheckConfig(
            worksheet="Finances", table_name="Project finance changes", project_name_column="Project funding moved from"
        ),
        ProjectCheckConfig(
            worksheet="Finances", table_name="Project finance changes", project_name_column="Project funding moved to"
        ),
    ]
    for check_config in check_configs:
        organisation_name = extracted_table_dfs["Organisation name"].iloc[0, 0]
        allowed_project_names = programme_to_projects[organisation_name]
        extracted_table_df = extracted_table_dfs[check_config.table_name]
        breaching_row_indices = common.check_values_against_allowed(
            df=extracted_table_df,
            value_column=check_config.project_name_column,
            allowed_values=allowed_project_names,
        )
        breaching_project_names = extracted_table_df.loc[
            breaching_row_indices, check_config.project_name_column
        ].tolist()
        error_messages.extend(
            [
                common.error_message(
                    sheet=check_config.worksheet,
                    section=check_config.table_name,
                    description=PFErrors.PROJECT_NOT_ALLOWED.format(project_name=project_name),
                    cell_index=f"{column_name_to_cell_indexes_letter[check_config.project_name_column]}"
                    f"{int(breaching_row_indices.pop(0)) + 1}",
                )
                for project_name in breaching_project_names
            ]
        )
    return error_messages


def _check_current_underspend(extracted_table_dfs: dict[str, pd.DataFrame]) -> list[Message]:
    """
    Check that the "Current underspend" is filled in if the reporting period is not Q4.

    :param extracted_table_dfs: Dictionary of DataFrames representing tables extracted from the original Excel file
    :return: List of error messages
    """
    reporting_period = typing.cast(str, extracted_table_dfs["Reporting period"].iloc[0, 0])  # probably a string
    if not reporting_period.startswith("Q4"):
        current_underspend_df = extracted_table_dfs["Current underspend"]
        current_underspend = current_underspend_df.iloc[0, 0]
        if pd.isna(current_underspend):
            row_index = current_underspend_df.index[0]
            return [
                common.error_message(
                    sheet="Finances",
                    section="Current underspend",
                    description=PFErrors.CURRENT_UNDERSPEND,
                    cell_index=f"B{typing.cast(int, row_index) + 1}",  # safe to assume idx is an int
                )
            ]
    return []


def _check_intervention_themes_in_pfcs(extracted_table_dfs: dict[str, pd.DataFrame]) -> list[Message]:
    """
    Check that the “Intervention theme moved from” and “Intervention theme moved to” in the table "Project finance
    changes" belong to the list of available intervention themes.

    :param extracted_table_dfs: Dictionary of DataFrames representing tables extracted from the original Excel file
    :return: List of error messages
    """
    allowed_themes = extracted_table_dfs["Intervention themes control"]["Intervention theme"].tolist()
    columns = [
        ("E", "Intervention theme moved from"),
        ("I", "Intervention theme moved to"),
    ]
    error_messages: list = []
    for col_letter, col_name in columns:
        breaching_indices = common.check_values_against_allowed(
            df=extracted_table_dfs["Project finance changes"], value_column=col_name, allowed_values=allowed_themes
        )
        breaching_themes = extracted_table_dfs["Project finance changes"].loc[breaching_indices, col_name].tolist()
        error_messages.extend(
            common.error_message(
                sheet="Finances",
                section="Project finance changes",
                cell_index=f"{col_letter}{int(row) + 1}",  # +1 because DataFrames are 0-indexed and Excel is not
                description=PFErrors.INTERVENTION_THEME_NOT_ALLOWED.format(intervention_theme=theme),
            )
            for row, theme in zip(breaching_indices, breaching_themes, strict=False)
        )
    return error_messages


def _check_actual_forecast_reporting_period(extracted_table_dfs: dict[str, pd.DataFrame]) -> list[Message]:
    """
    Check that the reporting period for actuals and forecasts in the "Project finance changes" table is consistent with
    the reporting period of the submission.

    :param extracted_table_dfs: Dictionary of DataFrames representing tables extracted from the original Excel file
    :return: List of error messages
    """
    reporting_period = extracted_table_dfs["Reporting period"].iloc[0, 0]
    submission_reporting_period_start_date = PFC_REPORTING_PERIOD_LABELS_TO_DATES[reporting_period]["start"]
    pfcs_df = extracted_table_dfs["Project finance changes"]
    error_messages = []
    for idx, row in pfcs_df.iterrows():
        change_reporting_period_start_date = PFC_REPORTING_PERIOD_LABELS_TO_DATES[
            row["Reporting period change takes place"]
        ]["start"]
        actual_forecast_cancelled = row["Actual, forecast or cancelled"]
        if actual_forecast_cancelled == "Actual":
            if change_reporting_period_start_date > submission_reporting_period_start_date:
                error_messages.append(
                    common.error_message(
                        sheet="Finances",
                        section="Project finance changes",
                        description=PFErrors.ACTUAL_REPORTING_PERIOD,
                        cell_index=f"P{typing.cast(int, idx) + 1}",  # safe to assume idx is an int
                    )
                )
        elif actual_forecast_cancelled == "Forecast":
            if change_reporting_period_start_date <= submission_reporting_period_start_date:
                error_messages.append(
                    common.error_message(
                        sheet="Finances",
                        section="Project finance changes",
                        description=PFErrors.FORECAST_REPORTING_PERIOD,
                        cell_index=f"P{typing.cast(int, idx) + 1}",  # safe to assume idx is an int
                    )
                )
    return error_messages
