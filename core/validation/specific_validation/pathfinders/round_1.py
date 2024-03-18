import pandas as pd

from core.exceptions import TamperedFileError, ValidationError
from core.messaging import Message
from core.transformation.pathfinders.round_1.control_mappings import (
    create_control_mappings,
)


def cross_table_validation(tables: dict[str, pd.DataFrame]) -> None:
    """
    :param tables: set of tables to validate
    """

    # TODO add correct error messages from design
    mappings = create_control_mappings(tables)

    tamper_checks = (_check_projects,)
    validation_checks = (
        _check_bespoke_outputs_outcomes,
        # TODO: perform conditional checks related to underspend on tables in the Finance section
    )

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
    organisation_name = input_tables["Organisation Name"].df.iat[0, 0]
    project_code = control_mappings["programme_name_to_id"][organisation_name]

    # This is the user input data on their projects
    input_project_tables = (input_tables["Progress"], input_tables["Project Location"])

    # This is the control project data to validate against
    # {"PF-BOL": ["PF-BOL-001", "PF-BOL-002"]},
    allowed_project_ids = control_mappings["programme_id_to_project_ids"][project_code]
    # {"PF-BOL": ["PF-BOL-001", "PF-BOL-002"]}

    error_messages = []

    for table in input_project_tables:
        for index, row in table.iterrows():
            project_id = control_mappings["project_name_to_id"].get(row["Project name"])
            if project_id is None or project_id not in allowed_project_ids:
                error_messages.append(
                    Message(
                        sheet=table.worksheet,
                        section=None,
                        cell_index=table.get_cell(index, "Project name"),
                        description="Project Name does not match those for the organisation",
                        error_type=None,
                    )
                )

    if error_messages:
        raise TamperedFileError(error_messages)


# As far as I understand, there are no programme-specific restrictions on standard outputs or outcomes
def _check_standard_outputs_outcomes(input_tables: dict[str, pd.DataFrame], control_mappings: dict[str, str]) -> None:
    """
    Check standard outputs and outcomes against allowed values. Standard outputs/outcomes are standard across all LAs
    :input tables: standard outcome dataframes
    :control_mappings:
    """

    allowed_values = (control_mappings["standard_outcomes"], control_mappings["standard_outputs"])

    standard_outcome_output_tables = (input_tables["Outcomes"], input_tables["Outputs"])

    columns = ("Output", "Outcome")

    error_messages = []
    for table, column, allowed_values in zip(standard_outcome_output_tables, columns, allowed_values):
        for index, row in table.df.iterrows():
            if row[column] not in allowed_values:
                error_messages.append(
                    Message(
                        sheet=table.worksheet,
                        section=None,
                        cell_index=table.get_cell(index, column),
                        description="Standard output or outcome value not in allowed values",
                        error_type=None,
                    )
                )
    return error_messages


def _check_bespoke_outputs_outcomes(input_tables: dict[str, pd.DataFrame], control_mappings):
    # Rotherham Borough Council
    organisation_name = input_tables["Organisation Name"].df.iat[0, 0]

    programme_id = control_mappings["programme_name_to_id"][organisation_name]

    allowed_values = (
        control_mappings["programme_id_to_allowed_bespoke_outputs"][programme_id],
        control_mappings["programme_id_to_allowed_bespoke_outcomes"][programme_id],
    )
    tables = (input_tables["Bespoke outputs"], input_tables["Bespoke outcomes"])
    columns = ("Output", "Outcome")
    error_messages = []

    for table, column, allowed_values in zip(tables, columns, allowed_values):
        for index, row in table.df.iterrows():
            if row[column] not in allowed_values:
                error_messages.append(
                    Message(
                        sheet=table.worksheet,
                        section=None,
                        cell_index=table.get_cell(index, "replace"),
                        description="Bespoke output or outcome value not in allowed values",
                        error_type=None,
                    )
                )


def _check_financial_underspend_values(input_tables: dict[str, pd.DataFrame], mapping):
    #  Project Finances Change table on the Finances tab,
    #  to prevent users from selecting Forecast from the drop down,
    #  after selecting Forecast in previous reporting period

    # finance_tables = input_tables["Project finance changes"]
    # column = "Actual or forecast"
    pass
