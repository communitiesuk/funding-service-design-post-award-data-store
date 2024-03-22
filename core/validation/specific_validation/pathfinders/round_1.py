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

    tamper_checks = (_check_projects, _check_standard_outputs_outcomes, _check_bespoke_outputs_outcomes)
    validation_checks = _check_financial_underspend_values

    for check in tamper_checks:
        check(tables, mappings)

    messages = []
    for check in validation_checks:
        messages.extend(check(tables, mappings))

    if messages:
        raise ValidationError(messages)


def _check_projects(input_tables: dict[str, pd.DataFrame], control_mappings) -> None:
    """
    :param tables: set of tables to validate
    :param mappings: the control mapping which we validate input dataframes against
    """

    # The organisation used by the user
    table_names = ["Project progress", "Project location"]

    organisation_name = input_tables["Organisation name"].df.iat[0, 0]
    project_code = control_mappings["programme_name_to_id"][organisation_name]

    allowed_project_ids = control_mappings["programme_id_to_project_ids"][project_code]

    error_messages = []

    for table_name in table_names:
        table = input_tables[table_name]
        for index, row in table.iterrows():
            project_id = control_mappings["project_name_to_id"].get(row["Project name"])
            if project_id is None or project_id not in allowed_project_ids:
                error_messages.append(
                    Message(
                        sheet=table.worksheet,
                        section=table_name,
                        cell_index=table.get_cell(index, "Project name"),
                        description="Project Name does not match those for the organisation",
                        error_type=None,
                    )
                )

    return error_messages


def _check_standard_outputs_outcomes(input_tables: dict[str, pd.DataFrame], control_mappings: dict[str, str]) -> None:
    """
    Check standard outputs and outcomes against allowed values. Standard outputs/outcomes are standard across all LAs
    :input tables: standard outcome dataframes
    :control_mappings:
    """

    allowed_values = (control_mappings["standard_outcomes"], control_mappings["standard_outputs"])

    table_names = ["Outcomes", "Outputs"]

    columns = ("Output", "Outcome")

    error_messages = []
    for table_name, column, allowed_values in zip(table_names, columns, allowed_values):
        # double check index tables referred to correctly
        # TODO move this for loop into a helper function
        table = input_tables[table_name]
        for index, row in table.df.iterrows():
            if row[column] not in allowed_values:
                error_messages.append(
                    Message(
                        sheet=table.worksheet,
                        section=table_name,
                        cell_index=table.get_cell(index, column),
                        description="Standard output or outcome value not in allowed values",
                        error_type=None,
                    )
                )
    return error_messages


def _check_bespoke_outputs_outcomes(input_tables: dict[str, pd.DataFrame], control_mappings):
    organisation_name = input_tables["organisation name"].df.iat[0, 0]

    programme_id = control_mappings["programme_name_to_id"][organisation_name]

    allowed_values = (
        control_mappings["programme_id_to_allowed_bespoke_outputs"][programme_id],
        control_mappings["programme_id_to_allowed_bespoke_outcomes"][programme_id],
    )
    table_names = ["Bespoke outputs", "Bespoke outcomes"]
    columns = ("Output", "Outcome")
    error_messages = []

    for table_name, column, allowed_values in zip(table_names, columns, allowed_values):
        table = input_tables[table_name]
        for index, row in table.df.iterrows():
            if row[column] not in allowed_values:
                error_messages.append(
                    Message(
                        sheet=table.worksheet,
                        section=table_name,
                        cell_index=table.get_cell(index, column),
                        description="Bespoke output or outcome value not in allowed values",
                        error_type=None,
                    )
                )

    return error_messages


def _check_financial_underspend_values(input_tables: dict[str, pd.DataFrame]):
    credible_plan = input_tables["Credible plan"]

    error_messages = []

    table_names = ("Total underspend", "Proposed underspend use", "Credible plan summary")
    # If the answer to Q1 is Yes, then Q2, Q3, Q4 are required to be completed
    if credible_plan == "Yes":

        for table_name in table_names:
            table = input_tables[table_name]
            for index, row in table.df.iterrows():
                # column names are identical to table names and so can be used interchangeably
                if not row[table_name]:
                    error_messages.append(
                        Message(
                            sheet=table.worksheet,
                            section=table_name,
                            cell_index=table.get_cell(index, table_name),
                            description="If credible plan is selected, you must answer Q2, Q3 and Q4",
                            error_type=None,
                        )
                    )

    elif credible_plan == "No":
        for table_name in table_names:
            table = input_tables[table_name]
            for index, row in table.df.iterrows():
                if row[table_name]:
                    error_messages.append(
                        Message(
                            sheet=table.worksheet,
                            section=table_name,
                            cell_index=table.get_cell(index, table_name),
                            description="If credible plan is not selected, Q2, Q3 and Q4 must be left blank.",
                            error_type=None,
                        )
                    )

    return error_messages
