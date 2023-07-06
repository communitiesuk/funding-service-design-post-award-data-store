from flask import abort
from sqlalchemy import func

from core.const import FUND_ID_TO_NAME
from core.db import db

# isort: off
from core.db.entities import Organisation, OutcomeDim, Programme, Project, Submission


# isort: on


def get_organisation_names():
    """Returns a list of all distinct organisation names that are referenced by at least one programme.

    :return: List of organisation names
    """
    organisations = db.session.query(Organisation).join(Programme).distinct().all()

    if not organisations:
        return abort(404, "No organisation names found.")

    organisation_list = [{"name": row.organisation_name, "id": str(row.id)} for row in organisations]

    return organisation_list, 200


def get_funds():
    """Returns a list of all distinct funds.

    :return: List of funds
    """
    programmes = Programme.query.with_entities(Programme.fund_type_id).distinct().all()

    if not programmes:
        return abort(404, "No funds found.")

    funds = [
        {"name": FUND_ID_TO_NAME[programme.fund_type_id], "id": programme.fund_type_id} for programme in programmes
    ]

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


def get_reporting_period_range():
    """Returns the start and end of the financial period.

    :return: Minimum reporting start and maximum reporting end period
    """
    result = db.session.query(
        func.min(Submission.reporting_period_start), func.max(Submission.reporting_period_end)
    ).first()

    start = result[0]  # earliest reporting period start date
    end = result[1]  # latest reporting period end date

    if not start or not end:
        return abort(404, "No reporting period range found.")

    return_period_range = {"start_date": start, "end_date": end}

    return return_period_range, 200
