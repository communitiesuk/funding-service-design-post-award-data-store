from flask import abort

from core.const import FUND_ID_TO_NAME
from core.db.entities import Organisation, OutcomeDim, Programme, Submission


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

    outcome_categories = [outcome_dim.outcome_category for outcome_dim in outcome_dims]

    return outcome_categories, 200


def get_returns():
    """Returns the start and end of the financial period.

    :return: Minimum reporting start and maximum reporting end period
    """
    returns = (
        Submission.query.with_entities(Submission.reporting_period_start, Submission.reporting_period_end)
        .distinct()
        .all()
    )

    if not returns:
        return abort(404, "No return periods found.")

    returns_list = [{"start_date": row.reporting_period_start, "end_date": row.reporting_period_end} for row in returns]

    return returns_list, 200
