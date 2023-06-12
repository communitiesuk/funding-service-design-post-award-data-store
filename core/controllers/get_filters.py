from flask import abort

from core.const import FUND_ID_TO_NAME
from core.db.entities import Organisation, OutcomeDim, Programme, Project


def get_organisation_names():
    """Returns a list of all distinct organisation names.

    :return: List of organisation names
    """
    organisations = Organisation.query.with_entities(Organisation.id, Organisation.organisation_name).distinct().all()

    if not organisations:
        return abort(404, "No organisation names found.")

    organisation_list = [{"name": row.organisation_name, "id": str(row.id)} for row in organisations]

    return organisation_list, 200


def get_funds():
    """Returns a list of all distinct funds.

    :return: List of funds
    """
    fund_ids = [prog.fund_type_id for prog in Programme.query.with_entities(Programme.fund_type_id).distinct().all()]

    if not fund_ids:
        return abort(404, "No funds found.")

    funds = [{"name": FUND_ID_TO_NAME[fund_id], "id": fund_id} for fund_id in fund_ids]

    return funds, 200


def get_outcome_categories():
    """Returns a list of all outcome categories.

    :return: List of outcome categories
    """
    outcome_dims = OutcomeDim.query.with_entities(OutcomeDim.outcome_category).distinct().all()

    if not outcome_dims:
        return abort(404, "No outcome categories found.")

    outcome_categories = [outcome_dim.outcome_category for outcome_dim in outcome_dims if outcome_dim.outcome_category]

    return outcome_categories, 200


def get_regions():
    """Returns all unique itl region codes associated with projects.

    :return: a list of itl region codes
    """
    projects = Project.query.all()

    itl_regions = set(region for project in projects for region in project.itl_regions)

    if not itl_regions:
        return abort(404, "No regions found.")

    return list(itl_regions), 200
