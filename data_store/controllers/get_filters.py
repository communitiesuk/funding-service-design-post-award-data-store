from sqlalchemy import func

from data_store.const import FUND_ID_TO_NAME
from data_store.db import db

# isort: off
from data_store.db.entities import GeospatialDim, Organisation, OutcomeDim, Programme, Submission, Fund


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

    if not organisations:
        raise RuntimeError("No organisation names found.")

    return [{"name": row.organisation_name, "id": str(row.id)} for row in organisations]


def get_funds():
    """
    Fetches all funds sorted alphabetically by fund_code.

    :return: A tuple - list of funds and status code 200. If no funds found, aborts with 404 error.
    """
    funds = Fund.query.order_by(Fund.fund_code).with_entities(Fund.fund_code).all()

    if not funds:
        raise RuntimeError("No funds found.")

    return [{"name": FUND_ID_TO_NAME[row.fund_code], "id": row.fund_code} for row in funds]


def get_outcome_categories():
    """
    Returns a list of all outcome categories in alphabetical order of 'outcome_category'.

    :return: List of outcome categories
    """

    outcome_category = OutcomeDim.outcome_category
    outcome_dims = OutcomeDim.query.order_by(outcome_category).with_entities(outcome_category).distinct().all()

    if not outcome_dims:
        raise RuntimeError("No outcome categories found.")

    return [outcome_dim.outcome_category for outcome_dim in outcome_dims if outcome_dim.outcome_category]


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

    if not geospatial_itl1_regions:
        raise RuntimeError("No regions found.")

    return [{"name": row.itl1_region_name, "id": row.itl1_region_code} for row in geospatial_itl1_regions]


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
        raise RuntimeError("No reporting period range found.")

    return {"start_date": start, "end_date": end}
