from datetime import datetime
from typing import Iterable

from sqlalchemy import UUID, and_, or_, select
from sqlalchemy.orm import joinedload

import core.db.entities as ents
from core.const import ITLRegion
from core.db import db
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
    ]
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


def get_download_data_ids(
    min_rp_start: datetime | None = None,
    max_rp_end: datetime | None = None,
    organisation_uuids: list[UUID] | None = None,
    fund_type_ids: list[str] | None = None,
    itl_regions: set[str] | None = None,
    outcome_categories: list[str] | None = None,
) -> tuple[tuple[UUID], tuple[UUID], tuple[UUID]]:
    """Queries the database on these parameters and returns all relevant IDs needed to build the download.

    :param min_rp_start: Minimum Reporting Period Start to filter by
    :param max_rp_end: Maximum Reporting Period End to filter by
    :param organisation_uuids: Organisations to filter by
    :param fund_type_ids: Fund Types to filter by
    :param itl_regions: ITL Regions to filter by
    :param outcome_categories: Outcome Categories to filter by
    :return: A tuple of Submission, Programme and Project UUIDs returned within this search space.
    """
    submission_uuids, submission_ids = get_submission_ids(min_rp_start, max_rp_end)

    programme_uuids, programme_ids = get_programme_ids(
        organisation_uuids,
        fund_type_ids,
    )

    project_uuids, _ = get_child_projects(programme_uuids)

    project_uuids, project_ids = filter_project_ids(project_uuids, submission_uuids, itl_regions)

    # recalculate programmes from child projects - omits programmes with no projects left after filtering
    programme_uuids, programme_ids = get_parent_programmes(project_uuids)

    return submission_uuids, programme_uuids, project_uuids


def get_results_as_tuples_of_columns(query, cols) -> tuple[None, ...]:
    """Executes an SQLAlchemy query and returns as a set of tuples, each representing a column.

    :param query: the query to execute
    :param cols: number of columns to be returned (i.e. values in the select statement)
    :return:
    """
    results = [tuple(row) for row in db.session.execute(query)]
    if results:
        tuples_of_columns = zip(*results)
        return tuples_of_columns
    else:
        # if no results, return None for each missing column of data
        return tuple(None for _ in range(cols))


def get_submission_ids(
    min_rp_start: datetime | None, max_rp_end: datetime | None
) -> tuple[tuple[UUID] | None, tuple[str] | None]:
    """Get submissions by reporting period.

    :param min_rp_start: Min reporting period start
    :param max_rp_end: Max reporting period end
    :return: Submission UUIDs, Submission IDs
    """
    if min_rp_start and max_rp_end:
        submission_condition = and_(
            ents.Submission.reporting_period_start >= min_rp_start,
            ents.Submission.reporting_period_end <= max_rp_end,
        )
    elif min_rp_start:
        submission_condition = ents.Submission.reporting_period_start >= min_rp_start
    elif max_rp_end:
        submission_condition = ents.Submission.reporting_period_end <= max_rp_end
    else:
        submission_condition = True

    submission_id_query = select(ents.Submission.id, ents.Submission.submission_id).filter(submission_condition)

    submission_uuid, submission_id = get_results_as_tuples_of_columns(submission_id_query, cols=2)

    print(f"Submission IDs: {submission_id}")
    return submission_uuid, submission_id


def get_programme_ids(
    organisation_ids: list[UUID] | None = None,
    fund_types: list[str] | None = None,
) -> tuple[tuple[UUID] | None, tuple[str] | None]:
    """Get programme ids from a set of query parameters - org ids, outcome cats, project ids.

    These are grouped in an "and" clause:
     - If organisation_ids is passed, filter programmes by organisation_id.
     - If fund_ids is passed, filter programmes by fund type id.

    :param organisation_ids: list of organisation ids to filter by
    :param fund_types: list of fund types to filter by
    :return: a tuple of tuples of programme UUIDs and programme ids
    """

    programme_conditions = []
    if organisation_ids:
        programme_conditions.append(ents.Programme.organisation_id.in_(organisation_ids))
    if fund_types:
        programme_conditions.append(ents.Programme.fund_type_id.in_(fund_types))

    # return true if there are no programme conditions - i.e. this will return all programmes
    programme_condition_operator = and_(True, *programme_conditions) if programme_conditions else True

    programme_id_query = (
        select(ents.Programme.id, ents.Programme.programme_id).filter(programme_condition_operator).distinct()
    )

    programme_uuids, programme_ids = get_results_as_tuples_of_columns(programme_id_query, cols=2)
    print(f"Programme IDs: {programme_ids}")
    return programme_uuids, programme_ids


def get_parent_programmes(project_uuids) -> tuple[tuple[UUID] | None, tuple[str] | None]:
    """Returns parent programmes from a collection of Project UUIDs.

    :param project_uuids: collection of Project UUIDs
    :return: Programme UUIDs, Programme IDs
    """
    query = (
        select(ents.Programme.id, ents.Programme.programme_id)
        .join(ents.Project, ents.Project.programme_id == ents.Programme.id)
        .where(ents.Project.id.in_(project_uuids))
        .distinct()
    )
    programme_uuids, programme_ids = get_results_as_tuples_of_columns(query, cols=2)
    return programme_uuids, programme_ids


def get_child_projects(programme_uuids: Iterable[UUID]) -> tuple[tuple[UUID] | None, tuple[str] | None]:
    """Returns child projects from a collection of Programme UUIDs.

    :param programme_uuids: collection of Programme UUIDs
    :return: Project UUIDs, Project IDs
    """
    query = select(
        ents.Project.id,
        ents.Project.project_id,
    ).where(ents.Project.programme_id.in_(programme_uuids))
    project_uuids, project_ids = get_results_as_tuples_of_columns(query, cols=2)
    return project_uuids, project_ids


def filter_project_ids(
    project_uuids: Iterable[UUID],
    submission_uuids: Iterable[UUID],
    itl_regions: set[str] | None = None,
) -> tuple[tuple[UUID] | None, tuple[str] | None]:
    """Filters a given set of projects by submission and region, if either are provided.

    :param project_uuids: Project UUIDs
    :param submission_uuids: Submission UUIDs
    :param itl_regions: a set of ITL Regions
    :return: a tuple of Project UUIDs and Project IDs
    """
    # always filter by Submission
    project_id_query = select(ents.Project.id, ents.Project.project_id, ents.Project.postcodes).where(
        and_(ents.Project.submission_id.in_(submission_uuids), ents.Project.id.in_(project_uuids))
    )

    results = [tuple(row) for row in db.session.execute(project_id_query)]

    all_regions_passed = itl_regions == {region for region in ITLRegion}
    if itl_regions and not all_regions_passed:
        project_results = [
            # omit postcode column
            tuple(row[:2])
            for row in results
            # filter by itl region
            if get_itl_regions_from_postcodes(row[2]).intersection(itl_regions)
        ]
    else:
        # omit postcode column
        project_results = [tuple(row[:2]) for row in results]

    if not project_results:
        # handle the query returning nothing
        return None, None

    project_uuids, project_ids = zip(*project_results)
    print(f"Project IDs: {project_ids}")
    return project_uuids, project_ids
