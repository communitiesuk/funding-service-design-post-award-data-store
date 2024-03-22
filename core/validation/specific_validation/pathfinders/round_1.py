import pandas as pd

from core.exceptions import ValidationError
from core.messaging import Message
from core.transformation.pathfinders.round_1.control_mappings import (
    create_control_mappings,
)


def cross_table_validation(df_dict: dict[str, pd.DataFrame]) -> None:
    """
    Perform cross-table validation checks on the input DataFrames extracted from the original Excel file. These are
    checks that require data from multiple tables to be compared against each other.

    :param df_dict: Dictionary of DataFrames representing tables extracted from the original Excel file
    :raises ValidationError: If any of the cross-table validation checks fail
    :return: None
    """
    mappings = create_control_mappings(df_dict)
    check_functions = [
        _check_projects,
        _check_standard_outputs_outcomes,
        _check_bespoke_outputs_outcomes,
        _check_credible_plan_fields,
    ]
    error_messages = []
    for check_function in check_functions:
        error_messages.extend(check_function(df_dict, mappings))
    if error_messages:
        raise ValidationError(error_messages)


def _check_projects(df_dict: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]) -> list[Message]:
    """
    Check that the project names in the Project progress and Project location tables match those allowed for the
    organisation.

    :param df_dict: Dictionary of DataFrames representing tables extracted from the original Excel file
    :param control_mappings: Dictionary of control mappings extracted from the original Excel file. These mappings are
    used to validate the data in the DataFrames
    :return: List of error messages
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
            project_name = row["Project name"]
            project_id = control_mappings["project_name_to_id"].get(project_name)
            if project_id is None or project_id not in allowed_project_ids:
                error_messages.append(
                    Message(
                        sheet=worksheet,
                        section=table_name,
                        cell_index=None,
                        description=f"Project name {project_name} is not allowed for this organisation.",
                        error_type=None,
                    )
                )
    return error_messages


def _check_standard_outputs_outcomes(
    df_dict: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> list[Message]:
    """
    Check that the standard outputs and outcomes in the Outputs and Outcomes tables are in the allowed values.

    :param df_dict: Dictionary of DataFrames representing tables extracted from the original Excel file
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
        df = df_dict[table_name]
        for _, row in df.iterrows():
            value = row[column]
            if value not in allowed_values:
                error_messages.append(
                    Message(
                        sheet=worksheet,
                        section=table_name,
                        cell_index=None,
                        description=f"Standard output or outcome value {value} not in allowed values.",
                        error_type=None,
                    )
                )
    return error_messages


def _check_bespoke_outputs_outcomes(
    df_dict: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> list[Message]:
    """
    Check that the bespoke outputs and outcomes in the Bespoke outputs and Bespoke outcomes tables are in the allowed
    values.

    :param df_dict: Dictionary of DataFrames representing tables extracted from the original Excel file
    :param control_mappings: Dictionary of control mappings extracted from the original Excel file. These mappings are
    used to validate the data in the DataFrames
    :return: List of error messages
    """
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
            value = row[column]
            if value not in allowed_values:
                error_messages.append(
                    Message(
                        sheet=worksheet,
                        section=table_name,
                        cell_index=None,
                        description=f"Bespoke output or outcome value {value} is not allowed for this organisation.",
                        error_type=None,
                    )
                )
    return error_messages


def _check_credible_plan_fields(
    df_dict: dict[str, pd.DataFrame], control_mappings: dict[str, dict | list[str]]
) -> list[Message]:
    """
    Check that the fields in the Total underspend, Proposed underspend use and Credible plan summary tables are
    completed correctly based on the value of the Credible plan field. If the Credible plan field is Yes, then the
    fields in these tables must be completed; if No, then they must be left blank.

    :param df_dict: Dictionary of DataFrames representing tables extracted from the original Excel file
    :param control_mappings: Dictionary of control mappings extracted from the original Excel file. These mappings are
    used to validate the data in the DataFrames
    :return: List of error messages
    """
    credible_plan = df_dict["Credible plan"].iloc[0, 0]
    error_messages = []
    worksheet = "Finances"
    table_names = ["Total underspend", "Proposed underspend use", "Credible plan summary"]
    if credible_plan == "Yes":
        for table_name in table_names:
            df = df_dict[table_name]
            for _, row in df.iterrows():
                # Column names are identical to table names and so can be used interchangeably
                if pd.isna(row[table_name]):
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
