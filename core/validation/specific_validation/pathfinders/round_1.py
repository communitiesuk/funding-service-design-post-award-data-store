"""
Module for performing cross-table validation checks on the input DataFrames extracted from the original Excel file.
These are checks that require data from multiple tables to be compared against each other. The checks are specific to
the Pathfinders round 1 reporting template.
"""

import pandas as pd

from core.exceptions import ValidationError
from core.messaging import Message
from core.table_configs.pathfinders.round_1 import PFErrors
from core.transformation.pathfinders.consts import PF_REPORTING_PERIOD_TO_DATES_PFCS
from core.transformation.pathfinders.round_1.control_mappings import (
    create_control_mappings,
)


def cross_table_validation(extracted_table_dfs: dict[str, pd.DataFrame]) -> None:
    """
    Perform cross-table validation checks on the input DataFrames extracted from the original Excel file. These are
    checks that require data from multiple tables to be compared against each other.

    :param extracted_table_dfs: Dictionary of DataFrames representing tables extracted from the original Excel file
    :raises ValidationError: If any of the cross-table validation checks fail
    :return: None
    """
    mappings = create_control_mappings(extracted_table_dfs)
    error_messages = []
    error_messages.extend(_check_projects(extracted_table_dfs, mappings))
    error_messages.extend(_check_standard_outputs_outcomes(extracted_table_dfs, mappings))
    error_messages.extend(_check_bespoke_outputs_outcomes(extracted_table_dfs, mappings))
    error_messages.extend(_check_credible_plan_fields(extracted_table_dfs))
    error_messages.extend(_check_actual_forecast_reporting_period(extracted_table_dfs))
    if error_messages:
        raise ValidationError(error_messages)


def _check_projects(
    extracted_table_dfs: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> list[Message]:
    """
    Check that the project names in the Project progress and Project location tables match those allowed for the
    organisation.

    :param extracted_table_dfs: Dictionary of DataFrames representing tables extracted from the original Excel file
    :param control_mappings: Dictionary of control mappings extracted from the original Excel file. These mappings are
    used to validate the data in the DataFrames
    :return: List of error messages
    """
    worksheets = ["Progress", "Project location"]
    table_names = ["Project progress", "Project location"]
    organisation_name = extracted_table_dfs["Organisation name"].iloc[0, 0]
    project_code = control_mappings["programme_name_to_id"][organisation_name]
    allowed_project_ids = control_mappings["programme_id_to_project_ids"][project_code]
    error_messages = []
    for worksheet, table_name in zip(worksheets, table_names):
        extracted_table_df = extracted_table_dfs[table_name]
        for _, row in extracted_table_df.iterrows():
            project_name = row["Project name"]
            project_id = control_mappings["project_name_to_id"].get(project_name)
            if project_id is None or project_id not in allowed_project_ids:
                error_messages.append(
                    Message(
                        sheet=worksheet,
                        section=table_name,
                        cell_index=None,
                        description=PFErrors.PROJECT_NOT_ALLOWED.format(project_name=project_name),
                        error_type=None,
                    )
                )
    return error_messages


def _check_standard_outputs_outcomes(
    extracted_table_dfs: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> list[Message]:
    """
    Check that the standard outputs and outcomes in the Outputs and Outcomes tables are in the allowed values.

    :param extracted_table_dfs: Dictionary of DataFrames representing tables extracted from the original Excel file
    :param control_mappings: Dictionary of control mappings extracted from the original Excel file. These mappings are
    used to validate the data in the DataFrames
    :return: List of error messages
    """
    allowed_values = (control_mappings["standard_outputs"], control_mappings["standard_outcomes"])
    worksheets = ["Outputs", "Outcomes"]
    table_names = ["Outputs", "Outcomes"]
    columns = ("Output", "Outcome")
    error_messages = []
    for table_name, worksheet, column, allowed_values in zip(table_names, worksheets, columns, allowed_values):
        extracted_table_df = extracted_table_dfs[table_name]
        for _, row in extracted_table_df.iterrows():
            value = row[column]
            if value not in allowed_values:
                error_messages.append(
                    Message(
                        sheet=worksheet,
                        section=table_name,
                        cell_index=None,
                        description=PFErrors.STANDARD_OUTPUT_OUTCOME_NOT_ALLOWED.format(value=value),
                        error_type=None,
                    )
                )
    return error_messages


def _check_bespoke_outputs_outcomes(
    extracted_table_dfs: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> list[Message]:
    """
    Check that the bespoke outputs and outcomes in the Bespoke outputs and Bespoke outcomes tables are in the allowed
    values.

    :param extracted_table_dfs: Dictionary of DataFrames representing tables extracted from the original Excel file
    :param control_mappings: Dictionary of control mappings extracted from the original Excel file. These mappings are
    used to validate the data in the DataFrames
    :return: List of error messages
    """
    organisation_name = extracted_table_dfs["Organisation name"].iloc[0, 0]
    programme_id = control_mappings["programme_name_to_id"][organisation_name]
    allowed_values = (
        control_mappings["programme_id_to_allowed_bespoke_outputs"][programme_id],
        control_mappings["programme_id_to_allowed_bespoke_outcomes"][programme_id],
    )
    worksheets = ["Outputs", "Outcomes"]
    table_names = ["Bespoke outputs", "Bespoke outcomes"]
    columns = ("Output", "Outcome")
    error_messages = []
    for table_name, worksheet, column, allowed_values in zip(table_names, worksheets, columns, allowed_values):
        extracted_table_df = extracted_table_dfs[table_name]
        for _, row in extracted_table_df.iterrows():
            value = row[column]
            if value not in allowed_values:
                error_messages.append(
                    Message(
                        sheet=worksheet,
                        section=table_name,
                        cell_index=None,
                        description=PFErrors.BESPOKE_OUTPUT_OUTCOME_NOT_ALLOWED.format(value=value),
                        error_type=None,
                    )
                )
    return error_messages


def _check_credible_plan_fields(extracted_table_dfs: dict[str, pd.DataFrame]) -> list[Message]:
    """
    Check that the fields in the Total underspend, Proposed underspend use and Credible plan summary tables are
    completed correctly based on the value of the Credible plan field. If the Credible plan field is Yes, then the
    fields in these tables must be completed; if No, then they must be left blank.

    :param extracted_table_dfs: Dictionary of DataFrames representing tables extracted from the original Excel file
    :param control_mappings: Dictionary of control mappings extracted from the original Excel file. These mappings are
    used to validate the data in the DataFrames
    :return: List of error messages
    """
    credible_plan = extracted_table_dfs["Credible plan"].iloc[0, 0]
    error_messages = []
    worksheet = "Finances"
    table_names = ["Total underspend", "Proposed underspend use", "Credible plan summary"]
    if credible_plan == "Yes":
        for table_name in table_names:
            extracted_table_df = extracted_table_dfs[table_name]
            for _, row in extracted_table_df.iterrows():
                # Column names are identical to table names and so can be used interchangeably
                if pd.isna(row[table_name]):
                    error_messages.append(
                        Message(
                            sheet=worksheet,
                            section=table_name,
                            cell_index=None,
                            description=PFErrors.CREDIBLE_PLAN_YES,
                            error_type=None,
                        )
                    )
    elif credible_plan == "No":
        for table_name in table_names:
            extracted_table_df = extracted_table_dfs[table_name]
            for _, row in extracted_table_df.iterrows():
                if not pd.isna(row[table_name]):
                    error_messages.append(
                        Message(
                            sheet=worksheet,
                            section=table_name,
                            cell_index=None,
                            description=PFErrors.CREDIBLE_PLAN_NO,
                            error_type=None,
                        )
                    )
    return error_messages


def _check_actual_forecast_reporting_period(extracted_table_dfs: dict[str, pd.DataFrame]) -> list[Message]:
    reporting_period = extracted_table_dfs["Reporting period"].iloc[0, 0]
    submission_reporting_period_start_date = PF_REPORTING_PERIOD_TO_DATES_PFCS[reporting_period]["start"]
    pfcs_df = extracted_table_dfs["Project finance changes"]
    error_messages = []
    for _, row in pfcs_df.iterrows():
        change_reporting_period_start_date = PF_REPORTING_PERIOD_TO_DATES_PFCS[
            row["Reporting period change takes place"]
        ]["start"]
        actual_forecast_cancelled = row["Actual, forecast or cancelled"]
        if actual_forecast_cancelled == "Actual":
            if change_reporting_period_start_date > submission_reporting_period_start_date:
                error_messages.append(
                    Message(
                        sheet="Finances",
                        section="Project finance changes",
                        cell_index=None,
                        description=PFErrors.ACTUAL_REPORTING_PERIOD,
                        error_type=None,
                    )
                )
        elif actual_forecast_cancelled == "Forecast":
            if change_reporting_period_start_date <= submission_reporting_period_start_date:
                error_messages.append(
                    Message(
                        sheet="Finances",
                        section="Project finance changes",
                        cell_index=None,
                        description=PFErrors.FORECAST_REPORTING_PERIOD,
                        error_type=None,
                    )
                )
    return error_messages
