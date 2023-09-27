from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest
from sqlalchemy import case, text

from core.const import GeographyIndicatorEnum, ITLRegion
from core.db import db
from core.db.entities import (
    Organisation,
    OutcomeData,
    OutcomeDim,
    Programme,
    Project,
    Submission,
)
from core.db.queries import download_data_base_query, outcome_data_query, project_query


def expected_outcome_join(query):
    """Helper function: Extend a SQLAlchemy ORM query to filter / return columns for OutcomeData."""

    # conditional expression to not show project_names where Outcomes.project_id == None
    conditional_expression_project = case((OutcomeData.project_id.is_(None), None), else_=Project.project_name)
    # conditional expression to not show programme_names where Outcomes.programme_id == None
    conditional_expression_programme = case((OutcomeData.programme_id.is_(None), None), else_=Programme.programme_name)

    test_query_out = query.with_entities(
        OutcomeData.id.label("outcome_id"),
        OutcomeDim.outcome_name,
        OutcomeData.programme_id,
        conditional_expression_programme.label("programme_name"),
        OutcomeData.start_date,
        OutcomeData.project_id,
        conditional_expression_project.label("project_name"),
        OutcomeDim.outcome_category,
    ).distinct()

    return test_query_out


def outcome_data_structure_common_test(outcome_data_df):
    """Common test methods for testing structure of OutcomeData tables."""
    # check each outcome only occurs once (ie not duplicated)
    duplicates = outcome_data_df[outcome_data_df.duplicated()]
    assert len(duplicates) == 0

    # check 1 and only 1 of these 2 columns is always null
    assert (
        (outcome_data_df["programme_id"].isnull() & outcome_data_df["project_id"].notnull())
        | (outcome_data_df["programme_id"].notnull() & outcome_data_df["project_id"].isnull())
    ).all()
    assert (
        (outcome_data_df["programme_name"].isnull() & outcome_data_df["project_name"].notnull())
        | (outcome_data_df["programme_name"].notnull() & outcome_data_df["project_name"].isnull())
    ).all()


def test_get_download_data_no_filters(seeded_test_client, additional_test_data):
    assert len(OutcomeData.query.all()) == 31
    programme_with_no_projects = additional_test_data["programme_with_no_projects"]
    programme_outcome_child_of_no_projects = additional_test_data["outcome_no_projects"]
    assert programme_outcome_child_of_no_projects.id in [row.id for row in OutcomeData.query.all()]

    # programmes with no project children should not show up even if no filters are passed
    test_query = download_data_base_query()
    test_query = test_query.with_entities(Programme.id).distinct()

    test_programme_ids = [row[0] for row in test_query.all()]
    assert programme_with_no_projects.id not in test_programme_ids

    # assert all expected projects included
    test_query_projects = test_query.with_entities(
        Project.project_name,
    ).distinct()
    test_df = pd.read_sql(test_query_projects.statement, con=db.engine.connect())

    assert set(test_df.project_name) == {
        "ProjectName1",
        "ProjectName2",
        "ProjectName3",
        "ProjectName4",
        "ProjectName5",
        "ProjectName6",
        "ProjectName7",
        "ProjectName8",
        "TEST-PROJECT-NAME",
        "TEST-PROJECT-NAME2",
        "TEST-PROJECT-NAME3",
        "TEST-PROJECT-NAME4",
    }

    # join to OutcomeData
    test_query_out = outcome_data_query(test_query)
    test_df_out = pd.read_sql(test_query_out.statement, con=db.engine.connect())

    explain_sql = text(f"EXPLAIN QUERY PLAN {test_query_out}")
    explain_result = db.session.execute(explain_sql)

    # programme level outcome, where the parent programme has no project children, should not show in in query.
    assert programme_with_no_projects.programme_id not in test_df_out["programme_id"]

    outcome_data_structure_common_test(test_df_out)


def test_get_download_data_no_filters_date_range(seeded_test_client, additional_test_data):
    test_query = download_data_base_query()

    # check all date ranges are included
    test_df = pd.read_sql(
        test_query.with_entities(
            Submission.id,
            Submission.reporting_period_start,
            Submission.reporting_period_end,
            Project.project_id,
        )
        .distinct()
        .statement,
        con=db.engine.connect(),
    )

    assert set(test_df.reporting_period_start) == {
        pd.Timestamp(datetime(2019, 10, 10)),
        pd.Timestamp(datetime(2023, 2, 1)),
    }
    assert set(test_df.reporting_period_end) == {
        pd.Timestamp(datetime(2021, 10, 10)),
        pd.Timestamp(datetime(2023, 2, 12)),
    }

    test_df_map = pd.read_sql(
        test_query.with_entities(Submission.id, Programme.id).distinct().statement, con=db.engine.connect()
    )
    assert len(test_df_map) == 2  # should just be 2 rows if joined 1:1, no cartesian join.


def test_get_download_data_date_filters(seeded_test_client, additional_test_data):
    """Test date filter on base query."""

    submission = additional_test_data["submission"]

    # for assertion comparisons. Increase date range on filters to include all records
    max_rp_end = submission.reporting_period_end + timedelta(weeks=(52 * 2))
    test_query_all = download_data_base_query(min_rp_start=submission.reporting_period_start, max_rp_end=max_rp_end)
    test_query_all_subs = test_query_all.with_entities(
        Submission.id,
        Submission.reporting_period_start,
        Submission.reporting_period_end,
    ).distinct()

    test_all_df = pd.read_sql(test_query_all_subs.statement, con=db.engine.connect())

    # all submission data should be within the specified reporting period range
    min_rp_start = submission.reporting_period_start - timedelta(days=1)
    max_rp_end = submission.reporting_period_end + timedelta(days=1)

    test_query_dates = download_data_base_query(min_rp_start=min_rp_start, max_rp_end=max_rp_end)
    test_query_dates_subs = test_query_dates.with_entities(
        Submission.id,
        Submission.submission_id,
        Submission.reporting_period_start,
        Submission.reporting_period_end,
    ).distinct()

    test_subs_df = pd.read_sql(test_query_dates_subs.statement, con=db.engine.connect())

    assert len(test_subs_df) == 1
    assert test_subs_df.id[0] == submission.id

    # test query with larger date-range filters gets more rows
    assert len(test_all_df) > len(test_subs_df)


def test_get_download_data_end_date_filter(seeded_test_client, additional_test_data):
    """Test date filter with only end date parameter."""
    submission = additional_test_data["submission"]

    #  date range to include all records
    max_rp_end = submission.reporting_period_end + timedelta(weeks=(52 * 2))
    test_query_all = download_data_base_query(max_rp_end=max_rp_end)
    test_query_all_proj = project_query(test_query_all)

    test_all_results = test_query_all_proj.all()
    assert len(test_all_results) == 12

    #  using an earlier end date as the only param reduced the rows returned.
    test_query_reduced = download_data_base_query(max_rp_end=submission.reporting_period_end)
    test_query_reduced_proj = project_query(test_query_reduced)
    test_reduced_results = test_query_reduced_proj.all()
    assert len(test_reduced_results) == 4


def test_get_download_data_start_date_filter(seeded_test_client, additional_test_data):
    """Test date filter with only start date parameter."""

    submission = additional_test_data["submission"]

    #  date range to include all records
    test_query_all = download_data_base_query(min_rp_start=submission.reporting_period_start)
    test_query_all_proj = project_query(test_query_all)

    test_all_results = test_query_all_proj.all()
    assert len(test_all_results) == 12

    #  using a later start date as the only param reduced the rows returned.
    max_rp_end = submission.reporting_period_start + timedelta(weeks=(52 * 2))
    test_query_reduced = download_data_base_query(min_rp_start=max_rp_end)
    test_query_reduced_proj = project_query(test_query_reduced)
    test_reduced_results = test_query_reduced_proj.all()
    assert len(test_reduced_results) == 8


def test_get_download_data_organisation_filter(seeded_test_client, additional_test_data):
    """Pass organisation filter params and check rows"""
    organisation = additional_test_data["organisation"]
    organisation_uuids = [organisation.id]

    test_query_org = download_data_base_query(organisation_uuids=organisation_uuids)

    test_query_org_ents = test_query_org.with_entities(
        Submission.submission_id,
        Organisation.id,
        Organisation.organisation_name,
        Project.project_id,
        Programme.programme_id,
    ).distinct()

    db.session.flush()

    test_query_org_all = (
        download_data_base_query()
        .with_entities(
            Submission.submission_id,
            Organisation.id,
            Organisation.organisation_name,
            Project.project_id,
            Programme.programme_id,
        )
        .distinct()
    )

    # basic check that query filter returns expected amount of rows compared to unfiltered query
    test_org_filtered = test_query_org_ents.all()
    test_all_orgs = test_query_org_all.all()
    assert len(test_org_filtered) < len(test_all_orgs)
    assert len(test_org_filtered) == 4


def test_get_download_data_fund_filter(seeded_test_client, additional_test_data):
    """Pass fund filter params and check rows"""

    programme = additional_test_data["programme"]
    fund_type_ids = [programme.fund_type_id]

    test_query_fund_type = download_data_base_query(fund_type_ids=fund_type_ids)

    test_query_fund_ents = test_query_fund_type.with_entities(
        Submission.submission_id,
        Programme.programme_id,
        Programme.fund_type_id,
        Project.project_id,
    ).distinct()

    # basic check that query filter returns expected amount of rows
    test_fund_filtered = test_query_fund_ents.all()
    assert len(test_fund_filtered) == 4


def test_get_download_data_region_filter(seeded_test_client, additional_test_data):
    # when ITL region is passed, projects should be filtered by ITL region and any parent programmes with entirely
    # filtered out child projects should not be returned
    itl_regions = {ITLRegion.SouthWest}
    test_query_region = download_data_base_query(itl_regions=itl_regions)

    test_query_region_ents = test_query_region.with_entities(
        Project.id,
        Project.project_id,
    ).distinct()

    test_fund_filtered_df = pd.read_sql(test_query_region_ents.statement, con=db.engine.connect())

    project4 = additional_test_data["project4"]

    assert project4.id not in test_fund_filtered_df.id  # not in SW region
    assert all(
        ITLRegion.SouthWest in project.itl_regions
        for project in Project.query.filter(Project.id.in_(test_fund_filtered_df.id))
    )


def test_get_download_data_region_and_fund(seeded_test_client, additional_test_data):
    # when both ITL region and fund_type filter params are passed, return relevant results

    programme = additional_test_data["programme"]
    project4 = additional_test_data["project4"]
    itl_regions = {ITLRegion.SouthWest}
    fund_type_ids = [programme.fund_type_id]

    test_query_region_fund = download_data_base_query(fund_type_ids=fund_type_ids, itl_regions=itl_regions)

    test_query_region_funds_ents = test_query_region_fund.with_entities(
        Project.id,
        Project.project_id,
        Project.programme_id,
    ).distinct()

    test_region_fund_filtered_df = pd.read_sql(test_query_region_funds_ents.statement, con=db.engine.connect())

    assert project4.id not in test_region_fund_filtered_df.id  # not in SW region
    assert all(
        programme.fund_type_id == programme.fund_type_id
        for programme in Programme.query.filter(Programme.id.in_(test_region_fund_filtered_df.programme_id))
    )
    assert all(
        ITLRegion.SouthWest in project.itl_regions
        for project in Project.query.filter(Project.id.in_(test_region_fund_filtered_df.id))
    )


def test_outcomes_with_non_outcome_filters(seeded_test_client, additional_test_data):
    """Specifically testing the OutcomeData joins when filters applied to OTHER tables."""

    organisation = additional_test_data["organisation"]
    programme = additional_test_data["programme"]
    organisation_uuids = [organisation.id]
    itl_regions = {ITLRegion.SouthWest}
    fund_type_ids = [programme.fund_type_id]

    test_query = download_data_base_query(
        fund_type_ids=fund_type_ids, itl_regions=itl_regions, organisation_uuids=organisation_uuids
    )

    # Project table with filters applied, for assertion comparison
    test_df = pd.read_sql(test_query.with_entities(Project).distinct().statement, con=db.engine.connect())

    # OutcomeData table
    test_query_outcome = expected_outcome_join(test_query)
    test_df_out = pd.read_sql(test_query_outcome.statement, con=db.engine.connect())

    outcome_data_structure_common_test(test_df_out)

    # check projects column in outcomeData is subset of all projects
    assert np.isin(test_df_out["project_id"].dropna().unique(), test_df["id"].values).all()
    # only rows Explicitly set to project level should be included in OutcomeData,
    # whereas all child projects of Outcome Programmes should be included in project level tables
    assert len(set(test_df_out["project_id"].dropna())) < len(set(test_df["id"].dropna()))


@pytest.fixture
def non_transport_outcome_data(seeded_test_client):
    """Inserts a tree of data with no links to a transport outcome to assert against."""
    submission = Submission(
        submission_id="TEST-SUBMISSION-ID-OUTCOME-TEST",
        reporting_round=1,
        reporting_period_start=datetime(2019, 10, 10),
        reporting_period_end=datetime(2021, 10, 10),
    )
    organisation = Organisation(organisation_name="TEST-ORGANISATION-OUTCOME-TEST")
    test_outcome_dim = OutcomeDim(outcome_name="TEST-OUTCOME-3", outcome_category="TEST-OUTCOME-CATEGORY-OUTCOME-TEST")
    db.session.add_all((submission, organisation, test_outcome_dim))
    db.session.flush()
    programme_no_transport_outcome_or_transport_child_projects = Programme(
        programme_id="TEST-PROGRAMME-ID3",
        programme_name="TEST-PROGRAMME-NAME3",
        fund_type_id="TEST3",
        organisation_id=organisation.id,
    )
    db.session.add(programme_no_transport_outcome_or_transport_child_projects)
    db.session.flush()
    # Custom outcome, SW region, no transport outcome in programmes or & projects
    project = Project(
        submission_id=submission.id,
        programme_id=programme_no_transport_outcome_or_transport_child_projects.id,
        project_id="TEST-PROJECT-ID5",
        project_name="TEST-PROJECT-NAME5",
        primary_intervention_theme="TEST-PIT",
        locations="TEST-LOCATIONS",
    )
    db.session.add(project)
    db.session.flush()
    non_transport_outcome = OutcomeData(
        submission_id=submission.id,
        project_id=project.id,  # linked to project1
        outcome_id=test_outcome_dim.id,  # linked to TEST-OUTCOME-CATEGORY OutcomeDim
        start_date=datetime(2022, 1, 1),
        end_date=datetime(2022, 12, 31),
        unit_of_measurement="Units",
        geography_indicator=GeographyIndicatorEnum.LOWER_LAYER_SUPER_OUTPUT_AREA,
        amount=100.0,
        state="Actual",
        higher_frequency=None,
    )
    db.session.add(non_transport_outcome)
    db.session.flush()

    return programme_no_transport_outcome_or_transport_child_projects


def test_outcome_category_filter(seeded_test_client, additional_test_data, non_transport_outcome_data):
    """
    Test expected Outcome filter behaviour.

    specific case:
    - 1 Programme matches outcome filter, 2 projects match outcome filter.
    - 1 of the projects is a child of matching programme, one isn't
    check in outcomes table, that only these 3 project/programmes show up, 2 proj, 1 prog)
    also, all instances of outcomes show up (can be multiple outcomes per each proj/prog)
    check in project table, all children of prog turn up + 1 proj in filter with different prog
    check in programme table, both turn up
    """
    programme_no_transport_outcome_or_transport_child_projects = non_transport_outcome_data

    assert len(OutcomeData.query.all()) == 32

    # reference data, all Outcome data, unfiltered / un-joined.
    test_query = download_data_base_query()
    test_query = test_query.with_entities(OutcomeData, OutcomeDim).distinct()
    test_df_categories_unfiltered = pd.read_sql(test_query.statement, con=db.engine.connect())
    test_query = test_query.with_entities(Project, Programme).distinct()
    test_df_projects_unfiltered = pd.read_sql(test_query.statement, con=db.engine.connect())

    #  apply filter to outcomes.
    test_query = download_data_base_query(outcome_categories=["Transport"])

    test_query_out = expected_outcome_join(test_query)  # filter conditions for OutcomeData columns

    test_df_out = pd.read_sql(test_query_out.statement, con=db.engine.connect())

    test_query_proj = test_query.with_entities(Project, Programme).distinct()
    test_df_proj = pd.read_sql(test_query_proj.statement, con=db.engine.connect())

    programme_with_outcome = "Leaky Cauldron regeneration"
    child_project_with_outcome = "ProjectName2"  # project is also child of programme_with_outcome
    non_child_project_with_outcome = "TEST-PROJECT-NAME3"  # project has no parent programme referenced in OutcomeData

    #  check in outcomes table, that only these 3 project/programmes show up, 2 proj, 1 prog)
    assert set(test_df_out["programme_name"].dropna().unique()) == {programme_with_outcome}
    assert set(test_df_out["project_name"].dropna().unique()) == {
        child_project_with_outcome,
        non_child_project_with_outcome,
    }

    # also, all instances of outcomes show up (can be multiple outcomes per each proj/prog)
    assert (test_df_categories_unfiltered["outcome_category"] == "Transport").sum() == len(test_df_out)
    assert set(test_df_categories_unfiltered.query("outcome_category=='Transport'")["id"]) == set(
        test_df_out["outcome_id"]
    )

    #  check in project table, all children of prog turn up + 1 proj in filter with different prog
    child_projects_of_programme = list(
        test_df_projects_unfiltered.query("programme_name=='Leaky Cauldron regeneration'")["project_name"]
    )  # all project children of programme with Outcome row
    child_projects_of_programme.append(non_child_project_with_outcome)
    expected_projects = set(
        child_projects_of_programme
    )  # plus extra project with an Outcome but without corresponding programme with outcome

    # check this constructed set matches project filtered by outcome
    assert expected_projects == set(test_df_proj["project_name"])

    # check that child projects of programme with no matching programme level outcome are not in filtered project table
    assert set(test_df_projects_unfiltered["project_name"]) - set(test_df_proj["project_name"])

    #  check in programme table, both turn up
    assert len(set(test_df_proj["programme_id"])) == 2

    # check a programme with no links to transport outcomes is not included in the results
    assert programme_no_transport_outcome_or_transport_child_projects.id not in test_df_proj["programme_id"]


def test_project_if_no_outcomes(seeded_test_client, additional_test_data):
    """
    Test that other tables still show up if no outcome data/outcome refs.

    This is testing the outer joins in the base_query (this tests a bugfix whereby no projects were returned if
    no Outcome data)
    """
    db.session.query(OutcomeData).delete()
    db.session.query(OutcomeDim).delete()
    db.session.flush()
    test_query = download_data_base_query()
    test_query_proj = test_query.with_entities(Project.project_name).distinct()

    test_df = pd.read_sql(test_query_proj.statement, con=db.engine.connect())
    assert list(test_df["project_name"])
