from sqlalchemy import func

from core.const import FUND_ID_TO_NAME
from core.db import db

# isort: off
from core.db.entities import GeospatialDim, Organisation, OutcomeDim, Programme, Submission, Fund


# isort: on


def get_organisation_names():
    """
    Returns a list of all distinct organisation names that are referenced by at least one programme ordered
    alphabetically by fund_id.

    :return: List of organisation names
    """
    organisations = (
        db.session.query(Organisation).order_by(Organisation.organisation_name).join(Programme).distinct().all()
    )

    organisation_list = [{"name": row.organisation_name, "id": str(row.id)} for row in organisations]

    return organisation_list


def get_funds():
    """
    Fetches all funds sorted alphabetically by fund_code.

    :return: A tuple - list of funds and status code 200. If no funds found, aborts with 404 error.
    """
    funds = Fund.query.order_by(Fund.fund_code).with_entities(Fund.fund_code).all()

    fund_list = [{"name": FUND_ID_TO_NAME[row.fund_code], "id": row.fund_code} for row in funds]

    return fund_list


def get_outcome_categories():
    """
    Returns a list of all outcome categories in alphabetical order of 'outcome_category'.

    :return: List of outcome categories
    """

    outcome_category = OutcomeDim.outcome_category
    outcome_dims = OutcomeDim.query.order_by(outcome_category).with_entities(outcome_category).distinct().all()

    outcome_categories = [outcome_dim.outcome_category for outcome_dim in outcome_dims if outcome_dim.outcome_category]

    return outcome_categories


def get_geospatial_regions():
    """Returns all unique ITL1 region codes associated with projects.

    :return: A tuple - list of ITL1 regions and status code 200. If no ITL1 regions found, aborts with 404 error.
    """
    geospatial_itl1_regions = (
        GeospatialDim.query.order_by(GeospatialDim.itl1_region_name)
        .distinct(
            GeospatialDim.itl1_region_name,
            GeospatialDim.itl1_region_code,
        )
        .with_entities(GeospatialDim.itl1_region_name, GeospatialDim.itl1_region_code)
        .filter(GeospatialDim.projects.any())
        .all()
    )

    itl_regions = [{"name": row.itl1_region_name, "id": row.itl1_region_code} for row in geospatial_itl1_regions]

    return itl_regions


def get_reporting_period_range():
    """Returns the start and end of the financial period.

    :return: Minimum reporting start and maximum reporting end period
    """
    result = db.session.query(
        func.min(Submission.reporting_period_start), func.max(Submission.reporting_period_end)
    ).first()

    start = result[0]  # earliest reporting period start date
    end = result[1]  # latest reporting period end date

    return_period_range = {"start_date": start, "end_date": end}

    return return_period_range
