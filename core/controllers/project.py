from copy import deepcopy

from flask import abort, current_app

from core.const import LookupArgs


def get_package(package_id):
    """Takes a value for package_id and returns the associated package data

    :param package_id: the package_id provided as a string
    :return: JSON object with the package dimensions
    """
    package_data = get_by_package_id(table="package", package_id=package_id)

    if not package_data:
        return abort(
            404,
            f"The provided package_id: {package_id} did not return any results.",
        )

    return package_data[0], 200


def get_project(project_id: str):
    """Takes a value for project_id and returns the associated project data.

    :param project_id: the project_id provided as a string
    :return: all data associated with a project
    """
    project_data = get_by_project_id(table="project", project_id=project_id)

    if not project_data:
        return abort(
            404,
            f"The provided project_id: {project_id} did not return any results.",
        )

    project = project_data[0]
    package_id = project["package_id"]

    project_tables = [
        "project_delivery_plan",
        "procurement",
        "direct_fund",
        "capital",
        "indirect_fund_secured",
        "indirect_fund_unsecured",
        "risk_register",
    ]

    project_nested_fk_tables = {
        "output_data": LookupArgs(
            fk_primary="output",
            related_table="outputs_dim",
            pk_related="output_name",
        ),
        "outcome_data": LookupArgs(fk_primary="outcome", related_table="outcome_dim", pk_related="outcome_name"),
    }

    package_tables = [
        "project_progress",
    ]

    # Add the tables called with project_id
    project.update({table_name: get_by_project_id(table_name, project_id) for table_name in project_tables})

    # Add tables with related data returned by get_by_project_with_fk
    project.update(
        {
            table_name: get_by_project_with_fk(table_name, project_id, lookup_args)
            for table_name, lookup_args in project_nested_fk_tables.items()
        }
    )

    # Add the tables called with package_id
    project.update({table_name: get_by_package_id(table_name, package_id) for table_name in package_tables})

    return project, 200


def get_by_project_id(table: str, project_id: str) -> list[dict]:
    """Get data from a fake table by project_id.

    :param table: table to search
    :param project_id: project id to match
    :return: results from the table that match the project id
    """
    return [
        table_model.as_dict() for table_model in getattr(current_app.db, table) if table_model.project_id == project_id
    ]


def get_by_package_id(table: str, package_id: str) -> list[dict]:
    """Get data from a fake table by package_id.

    :param table: table to search
    :param package_id: package id to match
    :return: results from the table that match the package id
    """
    return [
        table_model.as_dict() for table_model in getattr(current_app.db, table) if table_model.package_id == package_id
    ]


def get_by_project_with_fk(table_name: str, project_id: str, fk_lookup_args: LookupArgs) -> list[dict]:
    """
    Get data from a fake table by package_id including fk lookups to related table.

    Look up specified table, filtered to rows with PK (specifically project_id)
    matching input param. Within this table, lookup related data from specified
    table using key/field names specified in params.

    :param table_name: table to search
    :param project_id: project ID to filter table on.
    :param fk_lookup_args: namedtuple of fk lookup args.
    :return: Results from table that match lookup params as a list of
     table rows (each row defined as dict).
    """
    fk_primary, related_table, pk_related = fk_lookup_args
    table = getattr(current_app.db, related_table)
    rows_returned = []

    for parent_row_model in (table for table in getattr(current_app.db, table_name) if table.project_id == project_id):
        parent_row = parent_row_model.as_dict()

        for lookup_row_model in table:
            if getattr(lookup_row_model, pk_related) == parent_row[fk_primary]:
                lookup_table_row = deepcopy(lookup_row_model.as_dict())
                del lookup_table_row[pk_related]  # remove this key as it is effectively duplicate data
                parent_row.update(lookup_table_row)
                break

        rows_returned.append(parent_row)

    return rows_returned
