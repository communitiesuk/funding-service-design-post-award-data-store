"""
Module for performing cross-table validation checks on the input DataFrames extracted from the original Excel file.
These are checks that require data from multiple tables to be compared against each other. The checks are specific to
the Pathfinders round 1 reporting template.
"""

from collections import namedtuple

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
    # TODO: https://dluhcdigital.atlassian.net/browse/SMD-745
    # mismatch in names between spreadsheet dropdown & control mapping requires standardisation of name
    mappings["intervention_theme_to_standard_outcomes"]["Enhancing subregional and regional connectivity"] = mappings[
        "intervention_theme_to_standard_outcomes"
    ].pop("Enhancing sub-regional and regional connectivity")
    mappings["intervention_theme_to_standard_outputs"]["Enhancing subregional and regional connectivity"] += mappings[
        "intervention_theme_to_standard_outputs"
    ].pop("Enhancing sub-regional and regional connectivity")
    error_messages = []
    error_messages.extend(_check_projects(extracted_table_dfs, mappings))
    error_messages.extend(_check_standard_outputs(extracted_table_dfs, mappings))
    error_messages.extend(_check_standard_outcomes(extracted_table_dfs, mappings))
    error_messages.extend(_check_bespoke_outputs(extracted_table_dfs, mappings))
    error_messages.extend(_check_bespoke_outcomes(extracted_table_dfs, mappings))
    error_messages.extend(_check_credible_plan_fields(extracted_table_dfs))
    error_messages.extend(_check_intervention_themes_in_pfcs(extracted_table_dfs, mappings))
    error_messages.extend(_check_actual_forecast_reporting_period(extracted_table_dfs))
    if error_messages:
        raise ValidationError(error_messages)


def _error_message(sheet: str, section: str, description: str) -> Message:
    """
    Create an error message object.

    :param sheet: Name of the sheet
    :param section: Name of the section
    :param description: Description of the error
    :return: Message object
    """
    return Message(sheet=sheet, section=section, cell_index=None, description=description, error_type=None)


def _check_values_against_allowed(df: pd.DataFrame, value_column: str, allowed_values: list[str]) -> list[str]:
    """
    Check that the values in the specified column of the DataFrame are within the list of allowed values.

    :param df: DataFrame to check
    :param value_column: Name of the column containing the values to check
    :param allowed_values: List of allowed values
    :return: List of row indices with breaching values
    """
    breaching_row_indices = []
    for index, row in df.iterrows():
        value = row[value_column]
        if value not in allowed_values:
            breaching_row_indices.append(index)
    return breaching_row_indices


def _check_values_against_mapped_allowed(
    df: pd.DataFrame, value_column: str, allowed_values_key_column: str, allowed_values_map: dict[str, list[str]]
) -> list[str]:
    """
    Check that the values in the specified column of the DataFrame are within the list of allowed values determined by
    another column.

    :param df: DataFrame to check
    :param value_column: Name of the column containing the values to check
    :param allowed_values_key_column: Name of the column used to determine the list of allowed values
    :param allowed_values_map: Dictionary mapping themes to their respective lists of allowed values
    :return: List of row indices with breaching values
    """
    breaching_row_indices = []
    for index, row in df.iterrows():
        value = row[value_column]
        allowed_values_key = row[allowed_values_key_column]
        allowed_values = allowed_values_map.get(allowed_values_key, [])
        if value not in allowed_values:
            breaching_row_indices.append(index)
    return breaching_row_indices


def _check_projects(
    extracted_table_dfs: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> list[Message]:
    """
    Check that the project names in the "Project progress", "Project location" and "Project finance changes" tables
    match those allowed for the organisation.

    :param extracted_table_dfs: Dictionary of DataFrames representing tables extracted from the original Excel file
    :param control_mappings: Dictionary of control mappings extracted from the original Excel file. These mappings are
    used to validate the data in the DataFrames
    :return: List of error messages
    """
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
        programme_id = control_mappings["programme_name_to_id"][organisation_name]
        allowed_project_ids = control_mappings["programme_id_to_project_ids"][programme_id]
        extracted_table_df = extracted_table_dfs[check_config.table_name]
        extracted_table_df["Project ID"] = extracted_table_df[check_config.project_name_column].map(
            control_mappings["project_name_to_id"]
        )
        breaching_row_indices = _check_values_against_allowed(
            df=extracted_table_df,
            value_column="Project ID",
            allowed_values=allowed_project_ids,
        )
        breaching_project_names = extracted_table_df.loc[
            breaching_row_indices, check_config.project_name_column
        ].tolist()
        error_messages.extend(
            [
                _error_message(
                    sheet=check_config.worksheet,
                    section=check_config.table_name,
                    description=PFErrors.PROJECT_NOT_ALLOWED.format(project_name=project_name),
                )
                for project_name in breaching_project_names
            ]
        )
    return error_messages


def _check_standard_outputs(
    extracted_table_dfs: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> list[Message]:
    """
    Check that the standard outputs in the "Outputs" table belong to the list of standard outputs for the respective
    intervention theme.
    """
    breaching_row_indices = _check_values_against_mapped_allowed(
        df=extracted_table_dfs["Outputs"],
        value_column="Output",
        allowed_values_key_column="Intervention theme",
        allowed_values_map=control_mappings["intervention_theme_to_standard_outputs"],
    )
    breaching_outputs = extracted_table_dfs["Outputs"].loc[breaching_row_indices, "Output"].tolist()
    return [
        _error_message(
            sheet="Outputs",
            section="Outputs",
            description=PFErrors.STANDARD_OUTPUT_NOT_ALLOWED.format(output=output),
        )
        for output in breaching_outputs
    ]


def _check_standard_outcomes(
    extracted_table_dfs: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> list[Message]:
    """
    Check that the standard outcomes in the "Outcomes" table belong to the list of standard outcomes for the respective
    intervention theme.
    """
    breaching_row_indices = _check_values_against_mapped_allowed(
        df=extracted_table_dfs["Outcomes"],
        value_column="Outcome",
        allowed_values_key_column="Intervention theme",
        allowed_values_map=control_mappings["intervention_theme_to_standard_outcomes"],
    )
    breaching_outcomes = extracted_table_dfs["Outcomes"].loc[breaching_row_indices, "Outcome"].tolist()
    return [
        _error_message(
            sheet="Outcomes",
            section="Outcomes",
            description=PFErrors.STANDARD_OUTCOME_NOT_ALLOWED.format(outcome=outcome),
        )
        for outcome in breaching_outcomes
    ]


def _check_bespoke_outputs(
    extracted_table_dfs: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> list[Message]:
    """
    Check that the bespoke outputs in the "Bespoke outputs" table belong to the list of allowed bespoke outputs for the
    organisation.
    """
    organisation_name = extracted_table_dfs["Organisation name"].iloc[0, 0]
    programme_id = control_mappings["programme_name_to_id"][organisation_name]
    allowed_outputs = control_mappings["programme_id_to_allowed_bespoke_outputs"][programme_id]
    breaching_row_indices = _check_values_against_allowed(
        df=extracted_table_dfs["Bespoke outputs"],
        value_column="Output",
        allowed_values=allowed_outputs,
    )
    breaching_outputs = extracted_table_dfs["Bespoke outputs"].loc[breaching_row_indices, "Output"].tolist()
    return [
        _error_message(
            sheet="Outputs",
            section="Bespoke outputs",
            description=PFErrors.BESPOKE_OUTPUT_NOT_ALLOWED.format(output=output),
        )
        for output in breaching_outputs
    ]


def _check_bespoke_outcomes(
    extracted_table_dfs: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> list[Message]:
    """
    Check that the bespoke outcomes in the "Bespoke outcomes" table belong to the list of allowed bespoke outcomes for
    the organisation.
    """
    organisation_name = extracted_table_dfs["Organisation name"].iloc[0, 0]
    programme_id = control_mappings["programme_name_to_id"][organisation_name]
    allowed_outcomes = control_mappings["programme_id_to_allowed_bespoke_outcomes"][programme_id]
    breaching_row_indices = _check_values_against_allowed(
        df=extracted_table_dfs["Bespoke outcomes"],
        value_column="Outcome",
        allowed_values=allowed_outcomes,
    )
    breaching_outcomes = extracted_table_dfs["Bespoke outcomes"].loc[breaching_row_indices, "Outcome"].tolist()
    return [
        _error_message(
            sheet="Outcomes",
            section="Bespoke outcomes",
            description=PFErrors.BESPOKE_OUTCOME_NOT_ALLOWED.format(outcome=outcome),
        )
        for outcome in breaching_outcomes
    ]


def _check_credible_plan_fields(extracted_table_dfs: dict[str, pd.DataFrame]) -> list[Message]:
    """
    Check that the fields in the "Total underspend", "Proposed underspend use" and "Credible plan summary" tables are
    completed correctly based on the value of the "Credible plan" field. If the "Credible plan" field is "Yes", then the
    fields in these tables must be completed; if "No", then they must be left blank.

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
                        _error_message(
                            sheet=worksheet,
                            section=table_name,
                            description=PFErrors.CREDIBLE_PLAN_YES,
                        )
                    )
    elif credible_plan == "No":
        for table_name in table_names:
            extracted_table_df = extracted_table_dfs[table_name]
            for _, row in extracted_table_df.iterrows():
                if not pd.isna(row[table_name]):
                    error_messages.append(
                        _error_message(
                            sheet=worksheet,
                            section=table_name,
                            description=PFErrors.CREDIBLE_PLAN_NO,
                        )
                    )
    return error_messages


def _check_intervention_themes_in_pfcs(
    extracted_table_dfs: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> list[Message]:
    """
    Check that the “Intervention theme moved from” and “Intervention theme moved to” in the table "Project finance
    changes" belong to the list of available intervention themes.

    :param extracted_table_dfs: Dictionary of DataFrames representing tables extracted from the original Excel file
    :param control_mappings: Dictionary of control mappings extracted from the original Excel file. These mappings are
    used to validate the data in the DataFrames
    :return: List of error messages
    """
    allowed_intervention_themes = control_mappings["intervention_themes"]
    breaching_intervention_themes = []
    for intervention_theme_column in ("Intervention theme moved from", "Intervention theme moved to"):
        breaching_row_indices = _check_values_against_allowed(
            df=extracted_table_dfs["Project finance changes"],
            value_column=intervention_theme_column,
            allowed_values=allowed_intervention_themes,
        )
        breaching_intervention_themes.extend(
            extracted_table_dfs["Project finance changes"]
            .loc[breaching_row_indices, intervention_theme_column]
            .tolist()
        )
    return [
        _error_message(
            sheet="Finances",
            section="Project finance changes",
            description=PFErrors.INTERVENTION_THEME_NOT_ALLOWED.format(intervention_theme=intervention_theme),
        )
        for intervention_theme in breaching_intervention_themes
    ]


def _check_actual_forecast_reporting_period(extracted_table_dfs: dict[str, pd.DataFrame]) -> list[Message]:
    """
    Check that the reporting period for actuals and forecasts in the "Project finance changes" table is consistent with
    the reporting period of the submission.
    """
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
                    _error_message(
                        sheet="Finances",
                        section="Project finance changes",
                        description=PFErrors.ACTUAL_REPORTING_PERIOD,
                    )
                )
        elif actual_forecast_cancelled == "Forecast":
            if change_reporting_period_start_date <= submission_reporting_period_start_date:
                error_messages.append(
                    _error_message(
                        sheet="Finances",
                        section="Project finance changes",
                        description=PFErrors.FORECAST_REPORTING_PERIOD,
                    )
                )
    return error_messages
