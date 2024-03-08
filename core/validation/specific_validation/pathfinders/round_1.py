from core.exceptions import TamperedFileError, ValidationError
from core.messaging import Message
from core.table_configs.pathfinders.round_1 import PFErrors
from tables.table import Table


def cross_table_validation(tables: dict[str, Table], mappings: dict[str, dict]) -> None:
    """Run additional validation checks on the Pathfinders Round 1 tables.

    :param tables: set of tables to validate
    :param mappings: set of mappings from the reporting template
    :raises ValidationError: if any validation checks fail
    :return: None
    """
    # "programme_name_to_id": programme_name_to_id,
    # "project_name_to_id": project_name_to_id,
    # "programme_id_to_project_ids": programme_id_to_project_ids,
    # "programme_id_to_allowed_bespoke_outputs": programme_id_to_allowed_bespoke_outputs,
    # "programme_id_to_allowed_bespoke_outcomes": programme_id_to_allowed_bespoke_outcomes,
    # "allowed_standard_outputs": allowed_standard_outputs,
    # "allowed_standard_outcomes": allowed_standard_outcomes,

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


def _check_projects(tables: dict[str, Table], mappings: dict[str, dict]) -> None:
    """Check that the projects in the tables match those for the organisation.

    :param tables: tables from the reporting template
    :param mappings: mappings from the reporting template
    :raises TamperedFileError: if the projects in the tables do not match those for the organisation
    :return: None
    """
    programme = tables["Organisation Name"].df.iat[0, 0]
    programme_id = mappings["programme_name_to_id"][programme]
    allowed_project_ids = mappings["programme_id_to_project_ids"][programme_id]
    project_tables = (tables["Project Progress"],)  # TODO: add the project location table
    error_messages = []
    for table in project_tables:
        for index, row in table.df.iterrows():
            project_id = mappings["project_name_to_id"].get(row["Project name"])
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


def _check_bespoke_outputs_outcomes(tables: dict[str, Table], mappings: dict[str, dict]) -> list[Message]:
    """Check that the bespoke outputs and outcomes in the tables match those for the organisation.

    :param tables: tables from the reporting template
    :param mappings: mappings from the reporting template
    :return: list of validation messages
    """
    programme = tables["Organisation Name"].df.iat[0, 0]
    programme_id = mappings["programme_name_to_id"][programme]
    tables = (tables["Outputs"], tables["Outcomes"])
    columns = ("Output", "Outcome")
    allowed_values = (
        mappings["programme_id_to_allowed_bespoke_outputs"][programme_id],
        mappings["programme_id_to_allowed_bespoke_outcomes"][programme_id],
    )
    error_messages = []
    for table, column, allowed_values in zip(tables, columns, allowed_values):
        for index, row in table.df.iterrows():
            if row[column] not in allowed_values:
                error_messages.append(
                    Message(
                        sheet=table.worksheet,
                        section=None,
                        cell_index=table.get_cell(index, column),
                        description=PFErrors.ISIN,
                        error_type=None,
                    )
                )
    return error_messages


def _check_cross_finance_tables(tables: dict[str, Table], mappings: dict[str, dict]) -> list[Message]:
    """Check that the correct questions have been answered on the finance tables.

    :param tables: tables from the reporting template
    :param mappings: mappings from the reporting template
    :return: list of validation messages
    """
    pass
