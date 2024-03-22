import pandas as pd

from core.exceptions import ValidationError
from core.messaging import Message
from core.transformation.pathfinders.round_1.control_mappings import (
    create_control_mappings,
)


def cross_table_validation(tables: dict[str, pd.DataFrame]) -> None:
    """
    :param tables: set of tables to validate
    """
    # TODO add correct error messages from design and error types
    mappings = create_control_mappings(tables)
    check_functions = [
        _check_projects,
        _check_standard_outputs_outcomes,
        _check_bespoke_outputs_outcomes,
        _check_credible_plan_fields,
    ]
    error_messages = []
    for check_function in check_functions:
        error_messages.extend(check_function(tables, mappings))
    if error_messages:
        raise ValidationError(error_messages)


def _check_projects(df_dict: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]) -> None:
    """
    :param tables: set of tables to validate
    :param mappings: the control mapping which we validate input dataframes against
    """

    worksheets = ["Progress", "Project Location"]
    table_names = ["Project progress", "Project location"]
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
    project_code = control_mappings["programme_name_to_id"][organisation_name]
    allowed_project_ids = control_mappings["programme_id_to_project_ids"][project_code]
    error_messages = []
    for worksheet, table_name in zip(worksheets, table_names):
        df = df_dict[table_name]
        for _, row in df.iterrows():
            project_id = control_mappings["project_name_to_id"].get(row["Project name"])
            if project_id is None or project_id not in allowed_project_ids:
                error_messages.append(
                    Message(
                        sheet=worksheet,
                        section=table_name,
                        cell_index=None,
                        description="Project name does not match those allowed for the organisation.",
                        error_type=None,
                    )
                )
    return error_messages


def _check_standard_outputs_outcomes(
    df_dict: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> None:
    """
    Check standard outputs and outcomes against allowed values. Standard outputs/outcomes are standard across all LAs
    :input tables: standard outcome dataframes
    :control_mappings:
    """
    allowed_values = (control_mappings["standard_outputs"], control_mappings["standard_outcomes"])
    worksheets = ["Outputs", "Outcomes"]
    table_names = ["Outputs", "Outcomes"]
    columns = ("Output", "Outcome")
    error_messages = []
    for table_name, worksheet, column, allowed_values in zip(table_names, worksheets, columns, allowed_values):
        # TODO move this for loop into a helper function
        df = df_dict[table_name]
        for _, row in df.iterrows():
            if row[column] not in allowed_values:
                error_messages.append(
                    Message(
                        sheet=worksheet,
                        section=table_name,
                        cell_index=None,
                        description="Standard output or outcome value not in allowed values.",
                        error_type=None,
                    )
                )
    return error_messages


def _check_bespoke_outputs_outcomes(
    df_dict: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> None:
    organisation_name = df_dict["Organisation name"].iloc[0, 0]
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
        df = df_dict[table_name]
        for _, row in df.iterrows():
            if row[column] not in allowed_values:
                error_messages.append(
                    Message(
                        sheet=worksheet,
                        section=table_name,
                        cell_index=None,
                        description="Bespoke output or outcome value not in allowed values.",
                        error_type=None,
                    )
                )
    return error_messages


def _check_credible_plan_fields(
    df_dict: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> None:
    credible_plan = df_dict["Credible plan"].iloc[0, 0]
    error_messages = []
    worksheet = "Finances"
    table_names = ["Total underspend", "Proposed underspend use", "Credible plan summary"]
    # If the answer to Q1 is Yes, then Q2, Q3, Q4 are required to be completed; if No, then they must be left blank
    if credible_plan == "Yes":
        for table_name in table_names:
            df = df_dict[table_name]
            for _, row in df.iterrows():
                if pd.isna(
                    row[table_name]
                ):  # Column names are identical to table names and so can be used interchangeably
                    error_messages.append(
                        Message(
                            sheet=worksheet,
                            section=table_name,
                            cell_index=None,
                            description="If credible plan is selected, you must answer Q2, Q3 and Q4.",
                            error_type=None,
                        )
                    )
    elif credible_plan == "No":
        for table_name in table_names:
            df = df_dict[table_name]
            for _, row in df.iterrows():
                if not pd.isna(row[table_name]):
                    error_messages.append(
                        Message(
                            sheet=worksheet,
                            section=table_name,
                            cell_index=None,
                            description="If credible plan is not selected, Q2, Q3 and Q4 must be left blank.",
                            error_type=None,
                        )
                    )
    return error_messages
