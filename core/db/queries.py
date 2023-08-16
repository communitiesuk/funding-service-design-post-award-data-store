from datetime import datetime

from sqlalchemy import UUID, and_, or_
from sqlalchemy.orm import joinedload

import core.db.entities as ents
from core.const import ITLRegion
from core.util import get_itl_regions_from_postcodes


def filter_on_regions(itl_regions: set[str]) -> list[UUID]:
    """
    Query DB and return all project UUIDs filtered on region filter params.

    Note: hack due to SQLite legacy issues on local. To be deprecated in light of PostgreSQL array lookups.

    :param itl_regions: List of ITL regions to filter on.
    :return: List of Project id's filtered on region params.
    """
    results = ents.Project.query.with_entities(ents.Project.id, ents.Project.postcodes).distinct().all()

    updated_results = [
        row[0] for row in results if row[1] and get_itl_regions_from_postcodes(row[1]).intersection(itl_regions)
    ]  # if row[1] is None, Python short-circuiting behaviour will not evaluate the second condition.
    return updated_results


def get_download_data_query(
    min_rp_start: datetime | None = None,
    max_rp_end: datetime | None = None,
    organisation_uuids: list[UUID] | None = None,
    fund_type_ids: list[str] | None = None,
    itl_regions: set[str] | None = None,
    outcome_categories: list[str] | None = None,
) -> tuple[tuple[UUID], tuple[UUID], tuple[UUID]]:
    """
    Build a query to join and filter database tables according to parameters passed.

    If param filters are set to all (i.e. empty) then corresponding condition is ignored (passed as True).

    :param min_rp_start: Minimum Reporting Period Start to filter by
    :param max_rp_end: Maximum Reporting Period End to filter by
    :param organisation_uuids: Organisations to filter by
    :param fund_type_ids: Fund Types to filter by
    :param itl_regions: ITL Regions to filter by
    :param outcome_categories: Outcome Categories to filter by
    :return: SQLAlchemy query (to extend as required).
    """
    all_regions_passed = itl_regions == {region for region in ITLRegion}
    itl_rows = filter_on_regions(itl_regions) if itl_regions and not all_regions_passed else []

    project_region_condition = ents.Project.id.in_(itl_rows) if itl_rows else True
    submission_period_condition = set_submission_period_condition(min_rp_start, max_rp_end)
    programme_fund_condition = ents.Programme.fund_type_id.in_(fund_type_ids) if fund_type_ids else True
    organisation_name_condition = ents.Organisation.id.in_(organisation_uuids) if organisation_uuids else True
    outcome_category_condition = (
        ents.OutcomeDim.outcome_category.in_(outcome_categories) if outcome_categories else True
    )

    base_query = (
        ents.Project.query.join(ents.Submission)
        .join(ents.Programme)
        .join(ents.Organisation)
        .outerjoin(  # left outer join: Outcomes is child of Project and hence optional
            ents.OutcomeData,
            or_(
                ents.Project.id == ents.OutcomeData.project_id,
                ents.Project.programme_id == ents.OutcomeData.programme_id,
            ),
        )
        .join(ents.OutcomeDim)
        .filter(project_region_condition)
        .filter(submission_period_condition)
        .filter(programme_fund_condition)
        .filter(organisation_name_condition)
        .filter(outcome_category_condition)
    )

    return base_query


def set_submission_period_condition(min_rp_start: datetime | None, max_rp_end: datetime | None):
    """Set SQLAlchemy query condition for filtering on Submission date field entities.

    :param min_rp_start: Min reporting period start
    :param max_rp_end: Max reporting period end
    :return: sqlalchemy Query[QueryCondition]
    """
    # TODO: check this logic actually returns correct periods. This only returns data that is FULLY inside the date
    #  range specified by filters. Should the filter also include partials, or are we assuming it is impossible to
    #  mis-match dates due to input?
    conditions = []

    if min_rp_start:
        conditions.append(ents.Submission.reporting_period_start >= min_rp_start)
    if max_rp_end:
        conditions.append(ents.Submission.reporting_period_end <= max_rp_end)

    submission_period_condition = True if not conditions else and_(*conditions)
    return submission_period_condition


def get_programme_child_with_natural_keys_query(child_model, programme_ids):
    """Filters a Programme child table by programme id and loads parent natural keys.

    This function pre-loads the parent submission.submission_id and programme.programme_id of the filtered results
    as an optimisation because they're required to take the place of the FK UUIDs in the serialized data output.

    :param child_model: A child model of Programme
    :param programme_ids: A list of programme ids
    :return: A list of child models with preloaded natural FKs.
    """
    return child_model.query.filter(child_model.programme_id.in_(programme_ids)).options(
        joinedload(child_model.submission).load_only(ents.Submission.submission_id),
        joinedload(child_model.programme).load_only(ents.Programme.programme_id),
    )


def get_project_child_with_natural_keys_query(child_model, project_ids):
    """Filters a Project child table by project id and loads parent natural keys.

    This function pre-loads the parent submission.submission_id and project.project_id of the filtered results
    as an optimisation because they're required to take the place of the FK UUIDs in the serialized data output.

    :param child_model: A child model of Project
    :param project_ids: A list of project ids
    :return: A list of child models with preloaded natural FKs.
    """
    return child_model.query.filter(child_model.project_id.in_(project_ids)).options(
        joinedload(child_model.submission).load_only(ents.Submission.submission_id),
        joinedload(child_model.project).load_only(ents.Project.project_id),
    )
