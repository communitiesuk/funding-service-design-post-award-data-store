"""
Module for performing cross-table validation checks on the input DataFrames extracted from the original Excel file.
These are checks that require data from multiple tables to be compared against each other. The checks are specific to
the Pathfinders round 1 reporting template.
"""

from collections import namedtuple
from copy import deepcopy

import pandas as pd

from core.messaging import Message
from core.table_configs.pathfinders.round_1 import PFErrors
from core.transformation.pathfinders.consts import PF_REPORTING_PERIOD_TO_DATES_PFCS
from core.transformation.pathfinders.round_1.control_mappings import (
    create_control_mappings,
)


def cross_table_validation(extracted_table_dfs: dict[str, pd.DataFrame]) -> list[Message]:
    """
    Perform cross-table validation checks on the input DataFrames extracted from the original Excel file. These are
    checks that require data from multiple tables to be compared against each other.

    :param extracted_table_dfs: Dictionary of DataFrames representing tables extracted from the original Excel file
    :return: List of error messages
    """
    mappings = create_control_mappings(extracted_table_dfs)
    # TODO: https://dluhcdigital.atlassian.net/browse/SMD-745
    # mismatch in names between spreadsheet dropdown & control mapping requires standardisation of name
    mappings["intervention_theme_to_standard_outcomes"]["Enhancing subregional and regional connectivity"] = mappings[
        "intervention_theme_to_standard_outcomes"
    ].pop("Enhancing sub-regional and regional connectivity")
    mappings["intervention_theme_to_standard_outputs"]["Enhancing subregional and regional connectivity"] = mappings[
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
    return error_messages


def _error_message(sheet: str, section: str, description: str, cell_index: str = None) -> Message:
    """
    Create an error message object.

    :param sheet: Name of the sheet
    :param section: Name of the section
    :param description: Description of the error
    :param cell_index: Index of the cell where the error occurred
    :return: Message object
    """
    return Message(sheet=sheet, section=section, cell_indexes=(cell_index,), description=description, error_type=None)


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

    The cell_index in the error message is calculated by adding 1 to the row index of the breaching cell. This is
    because DataFrames are 0-indexed and Excel is not.

    :param extracted_table_dfs: Dictionary of DataFrames representing tables extracted from the original Excel file
    :param control_mappings: Dictionary of control mappings extracted from the original Excel file. These mappings are
    used to validate the data in the DataFrames
    :return: List of error messages
    """
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
                    cell_index=f"{column_name_to_cell_indexes_letter[check_config.project_name_column]}"
                    f"{breaching_row_indices.pop(0) + 1}",
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

    Any standard outputs which do not raise an error are also checked to ensure that the corresponding unit of
    measurement is allowed for that standard ouput.

    The cell_index in the error message is calculated by adding 1 to the row index of the breaching cell. This is
    because DataFrames are 0-indexed and Excel is not.
    """
    breaching_row_indices_outputs = _check_values_against_mapped_allowed(
        df=extracted_table_dfs["Outputs"],
        value_column="Output",
        allowed_values_key_column="Intervention theme",
        allowed_values_map=control_mappings["intervention_theme_to_standard_outputs"],
    )
    breaching_outputs = (
        extracted_table_dfs["Outputs"]
        .loc[breaching_row_indices_outputs, ["Output", "Intervention theme"]]
        .values.tolist()
    )
    breaching_indices_copy = deepcopy(breaching_row_indices_outputs)
    output_errors = [
        _error_message(
            sheet="Outputs",
            section="Outputs",
            description=PFErrors.STANDARD_OUTPUT_NOT_ALLOWED.format(
                output=output, intervention_theme=intervention_theme
            ),
            cell_index=f"C{breaching_row_indices_outputs.pop(0) + 1}",
        )
        for output, intervention_theme in breaching_outputs
    ]

    non_breaching_row_indices = extracted_table_dfs["Outputs"].index.difference(breaching_indices_copy)

    breaching_row_indices_uom = _check_values_against_mapped_allowed(
        df=extracted_table_dfs["Outputs"].loc[non_breaching_row_indices],
        value_column="Unit of measurement",
        allowed_values_key_column="Output",
        allowed_values_map=control_mappings["standard_output_uoms"],
    )
    breaching_uoms = extracted_table_dfs["Outputs"].loc[breaching_row_indices_uom, "Unit of measurement"].tolist()
    uom_errors = [
        _error_message(
            sheet="Outputs",
            section="Standard outputs",
            description=PFErrors.UOM_NOT_ALLOWED.format(unit_of_measurement=unit_of_measurement),
            cell_index=f"D{breaching_row_indices_uom.pop(0) + 1}",
        )
        for unit_of_measurement in breaching_uoms
    ]

    return output_errors + uom_errors


def _check_standard_outcomes(
    extracted_table_dfs: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> list[Message]:
    """
    Check that the standard outcomes in the "Outcomes" table belong to the list of standard outcomes for the respective
    intervention theme.

    Any standard outcomes which do not raise an error are also checked to ensure that the corresponding unit of
    measurement is allowed for that standard outcome.

    The cell_index in the error message is calculated by adding 1 to the row index of the breaching cell. This is
    because DataFrames are 0-indexed and Excel is not.
    """
    breaching_row_indices_outcomes = _check_values_against_mapped_allowed(
        df=extracted_table_dfs["Outcomes"],
        value_column="Outcome",
        allowed_values_key_column="Intervention theme",
        allowed_values_map=control_mappings["intervention_theme_to_standard_outcomes"],
    )
    breaching_outcomes = (
        extracted_table_dfs["Outcomes"]
        .loc[breaching_row_indices_outcomes, ["Outcome", "Intervention theme"]]
        .values.tolist()
    )
    breaching_indices_copy = deepcopy(breaching_row_indices_outcomes)
    outcome_errors = [
        _error_message(
            sheet="Outcomes",
            section="Outcomes",
            description=PFErrors.STANDARD_OUTCOME_NOT_ALLOWED.format(
                outcome=outcome, intervention_theme=intervention_theme
            ),
            cell_index=f"C{breaching_row_indices_outcomes.pop(0) + 1}",
        )
        for outcome, intervention_theme in breaching_outcomes
    ]

    non_breaching_row_indices = extracted_table_dfs["Outcomes"].index.difference(breaching_indices_copy)

    breaching_row_indices_uom = _check_values_against_mapped_allowed(
        df=extracted_table_dfs["Outcomes"].loc[non_breaching_row_indices],
        value_column="Unit of measurement",
        allowed_values_key_column="Outcome",
        allowed_values_map=control_mappings["standard_outcome_uoms"],
    )
    breaching_uoms = extracted_table_dfs["Outcomes"].loc[breaching_row_indices_uom, "Unit of measurement"].tolist()
    uom_errors = [
        _error_message(
            sheet="Outcomes",
            section="Standard outcomes",
            description=PFErrors.UOM_NOT_ALLOWED.format(unit_of_measurement=unit_of_measurement),
            cell_index=f"D{breaching_row_indices_uom.pop(0) + 1}",
        )
        for unit_of_measurement in breaching_uoms
    ]

    return outcome_errors + uom_errors


def _check_bespoke_outputs(
    extracted_table_dfs: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> list[Message]:
    """
    Check that the bespoke outputs in the "Bespoke outputs" table belong to the list of allowed bespoke outputs for the
    organisation.

    Any bespoke outputs which do not raise an error are also checked to ensure that the corresponding unit of
    measurement is allowed for that bespoke ouput.

    The cell_index in the error message is calculated by adding 1 to the row index of the breaching cell. This is
    because DataFrames are 0-indexed and Excel is not.
    """
    organisation_name = extracted_table_dfs["Organisation name"].iloc[0, 0]
    programme_id = control_mappings["programme_name_to_id"][organisation_name]
    allowed_outputs = control_mappings["programme_id_to_allowed_bespoke_outputs"][programme_id]
    breaching_row_indices_bespoke_outputs = _check_values_against_allowed(
        df=extracted_table_dfs["Bespoke outputs"],
        value_column="Output",
        allowed_values=allowed_outputs,
    )
    breaching_outputs = (
        extracted_table_dfs["Bespoke outputs"]
        .loc[breaching_row_indices_bespoke_outputs, ["Output", "Intervention theme"]]
        .values.tolist()
    )
    breaching_indices_copy = deepcopy(breaching_row_indices_bespoke_outputs)
    bespoke_output_errors = [
        _error_message(
            sheet="Outputs",
            section="Bespoke outputs",
            description=PFErrors.BESPOKE_OUTPUT_NOT_ALLOWED.format(
                output=output, intervention_theme=intervention_theme
            ),
            cell_index=f"C{breaching_row_indices_bespoke_outputs.pop(0) + 1}",
        )
        for output, intervention_theme in breaching_outputs
    ]

    non_breaching_row_indices = extracted_table_dfs["Bespoke outputs"].index.difference(breaching_indices_copy)

    breaching_row_indices_uom = _check_values_against_mapped_allowed(
        df=extracted_table_dfs["Bespoke outputs"].loc[non_breaching_row_indices],
        value_column="Unit of measurement",
        allowed_values_key_column="Output",
        allowed_values_map=control_mappings["bespoke_output_uoms"],
    )
    breaching_uoms = (
        extracted_table_dfs["Bespoke outputs"].loc[breaching_row_indices_uom, "Unit of measurement"].tolist()
    )
    uom_errors = [
        _error_message(
            sheet="Outputs",
            section="Bespoke outputs",
            description=PFErrors.UOM_NOT_ALLOWED.format(unit_of_measurement=unit_of_measurement),
            cell_index=f"D{breaching_row_indices_uom.pop(0) + 1}",
        )
        for unit_of_measurement in breaching_uoms
    ]

    return bespoke_output_errors + uom_errors


def _check_bespoke_outcomes(
    extracted_table_dfs: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> list[Message]:
    """
    Check that the bespoke outcomes in the "Bespoke outcomes" table belong to the list of allowed bespoke outcomes for
    the organisation.

    Any bespoke outcomes which do not raise an error are also checked to ensure that the corresponding unit of
    measurement is allowed for that bespoke outcome.

    The cell_index in the error message is calculated by adding 1 to the row index of the breaching cell. This is
    because DataFrames are 0-indexed and Excel is not.
    """
    organisation_name = extracted_table_dfs["Organisation name"].iloc[0, 0]
    programme_id = control_mappings["programme_name_to_id"][organisation_name]
    allowed_outcomes = control_mappings["programme_id_to_allowed_bespoke_outcomes"][programme_id]
    breaching_row_indices_bespoke_outcomes = _check_values_against_allowed(
        df=extracted_table_dfs["Bespoke outcomes"],
        value_column="Outcome",
        allowed_values=allowed_outcomes,
    )
    breaching_outcomes = (
        extracted_table_dfs["Bespoke outcomes"]
        .loc[breaching_row_indices_bespoke_outcomes, ["Outcome", "Intervention theme"]]
        .values.tolist()
    )
    breaching_indices_copy = deepcopy(breaching_row_indices_bespoke_outcomes)
    bespoke_outcome_errors = [
        _error_message(
            sheet="Outcomes",
            section="Bespoke outcomes",
            description=PFErrors.BESPOKE_OUTCOME_NOT_ALLOWED.format(
                outcome=outcome, intervention_theme=intervention_theme
            ),
            cell_index=f"C{breaching_row_indices_bespoke_outcomes.pop(0) + 1}",
        )
        for outcome, intervention_theme in breaching_outcomes
    ]

    non_breaching_row_indices = extracted_table_dfs["Bespoke outcomes"].index.difference(breaching_indices_copy)

    breaching_row_indices_uom = _check_values_against_mapped_allowed(
        df=extracted_table_dfs["Bespoke outcomes"].loc[non_breaching_row_indices],
        value_column="Unit of measurement",
        allowed_values_key_column="Outcome",
        allowed_values_map=control_mappings["bespoke_outcome_uoms"],
    )
    breaching_uoms = (
        extracted_table_dfs["Bespoke outcomes"].loc[breaching_row_indices_uom, "Unit of measurement"].tolist()
    )
    uom_errors = [
        _error_message(
            sheet="Outcomes",
            section="Bespoke outcomes",
            description=PFErrors.UOM_NOT_ALLOWED.format(unit_of_measurement=unit_of_measurement),
            cell_index=f"D{str(breaching_row_indices_uom.pop(0) + 1)}",
        )
        for unit_of_measurement in breaching_uoms
    ]

    return bespoke_outcome_errors + uom_errors


def _check_credible_plan_fields(extracted_table_dfs: dict[str, pd.DataFrame]) -> list[Message]:
    """
    Check that the fields in the "Total underspend", "Proposed underspend use" and "Credible plan summary" tables are
    completed correctly based on the value of the "Credible plan" field. If the "Credible plan" field is "Yes", then the
    fields in these tables must be completed; if "No", then they must be left blank.

    The cell_index in the error message is calculated by adding 1 to the row index of the breaching cell. This is
    because DataFrames are 0-indexed and Excel is not.

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
            for idx, row in extracted_table_df.iterrows():
                # Column names are identical to table names and so can be used interchangeably
                if pd.isna(row[table_name]):
                    error_messages.append(
                        _error_message(
                            sheet=worksheet,
                            section=table_name,
                            description=PFErrors.CREDIBLE_PLAN_YES,
                            cell_index=f"B{idx + 1}",
                        )
                    )
    elif credible_plan == "No":
        for table_name in table_names:
            extracted_table_df = extracted_table_dfs[table_name]
            for idx, row in extracted_table_df.iterrows():
                if not pd.isna(row[table_name]):
                    error_messages.append(
                        _error_message(
                            sheet=worksheet,
                            section=table_name,
                            description=PFErrors.CREDIBLE_PLAN_NO,
                            cell_index=f"B{idx + 1}",
                        )
                    )
    return error_messages


def _check_intervention_themes_in_pfcs(
    extracted_table_dfs: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> list[Message]:
    """
    Check that the “Intervention theme moved from” and “Intervention theme moved to” in the table "Project finance
    changes" belong to the list of available intervention themes.

    The cell_index in the error message is calculated by adding 1 to the row index of the breaching cell. This is
    because DataFrames are 0-indexed and Excel is not.

    :param extracted_table_dfs: Dictionary of DataFrames representing tables extracted from the original Excel file
    :param control_mappings: Dictionary of control mappings extracted from the original Excel file. These mappings are
    used to validate the data in the DataFrames
    :return: List of error messages
    """
    allowed_themes = control_mappings["intervention_themes"]
    columns = [
        ("E", "Intervention theme moved from"),
        ("I", "Intervention theme moved to"),
    ]
    error_messages = []
    for col_letter, col_name in columns:
        breaching_indices = _check_values_against_allowed(
            df=extracted_table_dfs["Project finance changes"], value_column=col_name, allowed_values=allowed_themes
        )
        breaching_themes = extracted_table_dfs["Project finance changes"].loc[breaching_indices, col_name].tolist()
        error_messages.extend(
            _error_message(
                sheet="Finances",
                section="Project finance changes",
                cell_index=f"{col_letter}{row + 1}",  # +1 because DataFrames are 0-indexed and Excel is not
                description=PFErrors.INTERVENTION_THEME_NOT_ALLOWED.format(intervention_theme=theme),
            )
            for row, theme in zip(breaching_indices, breaching_themes)
        )
    return error_messages


def _check_actual_forecast_reporting_period(extracted_table_dfs: dict[str, pd.DataFrame]) -> list[Message]:
    """
    Check that the reporting period for actuals and forecasts in the "Project finance changes" table is consistent with
    the reporting period of the submission.
    """
    reporting_period = extracted_table_dfs["Reporting period"].iloc[0, 0]
    submission_reporting_period_start_date = PF_REPORTING_PERIOD_TO_DATES_PFCS[reporting_period]["start"]
    pfcs_df = extracted_table_dfs["Project finance changes"]
    error_messages = []
    for idx, row in pfcs_df.iterrows():
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
                        cell_index=f"P{idx + 1}",
                    )
                )
        elif actual_forecast_cancelled == "Forecast":
            if change_reporting_period_start_date <= submission_reporting_period_start_date:
                error_messages.append(
                    _error_message(
                        sheet="Finances",
                        section="Project finance changes",
                        description=PFErrors.FORECAST_REPORTING_PERIOD,
                        cell_index=f"P{idx + 1}",
                    )
                )
    return error_messages
