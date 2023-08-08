import uuid
from datetime import datetime, timedelta

import numpy as np
import pandas as pd
import pytest
from sqlalchemy import case

from core.const import GeographyIndicatorEnum, ITLRegion, MultiplicityEnum
from core.db import db
from core.db.entities import (
    Organisation,
    OutcomeData,
    OutcomeDim,
    Programme,
    Project,
    Submission,
)
from core.db.queries import (  # get_programmes_and_child_projects,
    filter_project_ids,
    get_child_projects,
    get_download_data_ids,
    get_download_data_query,
    get_parent_programmes,
    get_programme_ids,
    get_submission_ids,
)


@pytest.fixture
def submissions(test_client):
    # Create some sample submissions for testing
    sub1 = Submission(
        submission_id="1",
        submission_date=datetime(2023, 5, 1),
        reporting_period_start=datetime(2023, 4, 1),
        reporting_period_end=datetime(2023, 4, 30),
        reporting_round=1,
    )
    sub2 = Submission(
        submission_id="2",
        submission_date=datetime(2023, 5, 5),
        reporting_period_start=datetime(2023, 5, 1),
        reporting_period_end=datetime(2023, 5, 31),
        reporting_round=2,
    )
    sub3 = Submission(
        submission_id="3",
        submission_date=datetime(2023, 6, 1),
        reporting_period_start=datetime(2023, 6, 1),
        reporting_period_end=datetime(2023, 6, 30),
        reporting_round=1,
    )
    sub4 = Submission(
        submission_id="4",
        submission_date=datetime(2023, 6, 5),
        reporting_period_start=datetime(2023, 6, 1),
        reporting_period_end=datetime(2023, 6, 30),
        reporting_round=2,
    )
    submissions = [sub1, sub2, sub3, sub4]
    db.session.add_all(submissions)
    return submissions


@pytest.fixture
def sub_ids(test_client, submissions):
    sub_ids = [
        Submission.query.filter_by(submission_id=submissions[idx].submission_id).first().id
        for idx in range(len(submissions))
    ]
    return sub_ids


def test_get_submissions_by_reporting_period_all_old(submissions):
    result = Submission.get_submissions_by_reporting_period(None, None)

    assert len(result) == len(submissions)
    assert all(sub in result for sub in submissions)


def test_get_submissions_by_reporting_period_with_start_and_end_old(submissions):
    start = datetime(2023, 3, 1)
    end = datetime(2023, 5, 31)

    result = Submission.get_submissions_by_reporting_period(start, end)

    assert len(result) == 2
    assert all(
        start <= sub.reporting_period_start <= end and start <= sub.reporting_period_end <= end for sub in result
    )


def test_get_submissions_by_reporting_period_with_start_old(submissions):
    start = datetime(2023, 6, 1)

    result = Submission.get_submissions_by_reporting_period(start, None)

    assert len(result) == 2
    assert all(start <= sub.reporting_period_start for sub in result)


def test_get_submissions_by_reporting_period_with_end_old(submissions):
    end = datetime(2023, 6, 15)

    result = Submission.get_submissions_by_reporting_period(None, end)

    assert len(result) == 2
    assert all(sub.reporting_period_end <= end for sub in result)


def test_get_submissions_by_reporting_period_all(sub_ids):
    actual_sub_ids, _ = get_submission_ids(None, None)

    # assert all submission ids are returned
    assert set(actual_sub_ids) == set(sub_ids)


def test_get_submissions_by_reporting_period_none(sub_ids):
    start = datetime(9999, 9, 9)
    end = datetime(9999, 9, 9)

    actual_sub_ids, _ = get_submission_ids(start, end)

    # assert no submission ids are returned if range isn't captured in the data
    assert not actual_sub_ids


def test_get_submissions_by_reporting_period_with_start_and_end(submissions):
    start = datetime(2023, 3, 1)
    end = datetime(2023, 5, 31)

    actual_sub_ids, _ = get_submission_ids(start, end)

    # assert returns a subset of all submissions
    assert len(actual_sub_ids) == 2
    # assert returned submissions are within the range
    assert all(
        start <= sub.reporting_period_start and end >= sub.reporting_period_end
        for sub in Submission.query.filter(Submission.id.in_(actual_sub_ids)).all()
    )


def test_get_submissions_by_reporting_period_with_start(submissions):
    start = datetime(2023, 6, 1)

    actual_sub_ids, _ = get_submission_ids(start, None)

    # assert returns a subset of all submissions
    assert len(actual_sub_ids) == 2
    # assert returned submissions are within the range
    assert all(
        start <= sub.reporting_period_start for sub in Submission.query.filter(Submission.id.in_(actual_sub_ids))
    )


def test_get_submissions_by_reporting_period_with_end(submissions):
    end = datetime(2023, 6, 15)

    actual_sub_ids, _ = get_submission_ids(None, end)

    # assert returns a subset of all submissions
    assert len(actual_sub_ids) == 2
    # assert returned submissions are within the range
    assert all(end >= sub.reporting_period_end for sub in Submission.query.filter(Submission.id.in_(actual_sub_ids)))


@pytest.fixture
def organisations(test_client):
    # Create some sample organisations for testing
    org1 = Organisation(organisation_name="Org 1", geography="Geography 1")
    org2 = Organisation(organisation_name="Org 2", geography="Geography 2")
    org3 = Organisation(organisation_name="Org 3", geography="Geography 3")
    org4 = Organisation(organisation_name="Org 4", geography="Geography 4")
    orgs = [org1, org2, org3, org4]
    db.session.add_all(orgs)
    return orgs


@pytest.fixture
def org_ids(test_client, organisations):
    org_ids = [
        Organisation.query.filter_by(organisation_name=organisations[idx].organisation_name).first().id
        for idx in range(len(organisations))
    ]
    return org_ids


def test_get_organisations_by_name_with_names(organisations):
    # Arrange
    names = ["Org 2", "Org 4"]

    # Act
    result = Organisation.get_organisations_by_name(names)

    # Assert
    assert len(result) == 2
    assert all(org.organisation_name in names for org in result)


def test_get_organisations_by_name_without_names(organisations):
    result = Organisation.get_organisations_by_name([])

    assert len(result) == len(organisations)
    assert all(org in result for org in organisations)


@pytest.fixture
def programmes(test_client, org_ids):
    # Create some sample programmes for testing
    prog1 = Programme(
        programme_id="1", programme_name="Programme 1", fund_type_id="fund_type_1", organisation_id=org_ids[0]
    )
    prog2 = Programme(
        programme_id="2", programme_name="Programme 2", fund_type_id="fund_type_1", organisation_id=org_ids[1]
    )
    prog3 = Programme(
        programme_id="3", programme_name="Programme 3", fund_type_id="fund_type_2", organisation_id=org_ids[0]
    )
    prog4 = Programme(
        programme_id="4", programme_name="Programme 4", fund_type_id="fund_type_2", organisation_id=org_ids[2]
    )
    programmes = [prog1, prog2, prog3, prog4]
    db.session.add_all(programmes)
    return programmes


@pytest.fixture
def prog_ids(test_client, programmes):
    prog_ids = [
        Programme.query.filter_by(programme_name=programmes[idx].programme_name).first().id
        for idx in range(len(programmes))
    ]
    return prog_ids


def test_get_programmes_by_org_and_fund_type_all(programmes):
    result = Programme.get_programmes_by_org_and_fund_type([], [])

    assert len(result) == len(programmes)
    assert all(prog in result for prog in programmes)


def test_get_programmes_by_org_and_fund_type_with_org_and_fund_type(programmes, org_ids):
    query_org_ids = [org_ids[0], org_ids[1]]
    fund_type_ids = ["fund_type_1"]

    result = Programme.get_programmes_by_org_and_fund_type(query_org_ids, fund_type_ids)

    assert len(result) == 2
    assert all(prog.organisation_id in query_org_ids and prog.fund_type_id in fund_type_ids for prog in result)


def test_get_programmes_by_org_and_fund_type_with_org_only(programmes, org_ids):
    query_org_ids = [org_ids[2]]

    result = Programme.get_programmes_by_org_and_fund_type(query_org_ids, [])

    assert len(result) == 1
    assert all(prog.organisation_id in query_org_ids for prog in result)


def test_get_programmes_by_org_and_fund_type_with_fund_type_only(programmes):
    fund_type_ids = ["fund_type_2"]

    result = Programme.get_programmes_by_org_and_fund_type([], fund_type_ids)

    assert len(result) == 2
    assert all(prog.fund_type_id in fund_type_ids for prog in result)


@pytest.fixture
def projects(test_client, prog_ids, sub_ids):
    # Create some sample projects for testing
    proj1 = Project(
        project_id="1",
        submission_id=sub_ids[0],
        programme_id=prog_ids[0],  # prog 1
        project_name="Project 1",
        primary_intervention_theme="Theme 1",
        location_multiplicity=MultiplicityEnum.SINGLE,
        locations="Somewhere",
        postcodes="M1 3DF",  # North West
        gis_provided="Yes",
        lat_long="12345",
    )
    proj2 = Project(
        project_id="2",
        submission_id=sub_ids[1],
        programme_id=prog_ids[1],  # prog 2
        project_name="Project 2",
        primary_intervention_theme="Theme 2",
        location_multiplicity=MultiplicityEnum.SINGLE,
        locations="Somewhere",
        postcodes="M1 3DF",  # North West
        gis_provided="No",
        lat_long=None,
    )
    proj3 = Project(
        project_id="3",
        submission_id=sub_ids[0],
        programme_id=prog_ids[0],  # prog 1
        project_name="Project 3",
        primary_intervention_theme="Theme 1",
        location_multiplicity=MultiplicityEnum.SINGLE,
        locations="Somewhere",
        postcodes="DT1 2TG",  # South West
        gis_provided="Yes",
        lat_long="67890",
    )
    proj4 = Project(
        project_id="4",
        submission_id=sub_ids[1],
        programme_id=prog_ids[1],  # prog 2
        project_name="Project 4",
        primary_intervention_theme="Theme 2",
        location_multiplicity=MultiplicityEnum.SINGLE,
        locations="Somewhere",
        postcodes="DT1 2TG",  # South West
        gis_provided="No",
        lat_long=None,
    )
    projects = [proj1, proj2, proj3, proj4]
    db.session.add_all(projects)
    return projects


@pytest.fixture
def outcomes(sub_ids, prog_ids, proj_ids):
    # Create some sample outcomes for testing
    outcome_dim1 = OutcomeDim(outcome_name="OutcomeDim 1", outcome_category="Category 1")
    outcome_dim2 = OutcomeDim(outcome_name="OutcomeDim 2", outcome_category="Category 2")
    outcome_dims = [outcome_dim1, outcome_dim2]
    db.session.add_all(outcome_dims)
    outcome_dim_ids = [
        OutcomeDim.query.filter_by(outcome_name=outcome_dim.outcome_name).first().id for outcome_dim in outcome_dims
    ]

    outcome1 = OutcomeData(
        submission_id=sub_ids[0],
        project_id=proj_ids[0],  # Project 1
        outcome_id=outcome_dim_ids[0],  # Category 1
        start_date=datetime(2022, 1, 1),
        end_date=datetime(2022, 12, 31),
        unit_of_measurement="Units",
        geography_indicator=GeographyIndicatorEnum.TRAVEL_CORRIDOR,
        amount=100.0,
        state="Actual",
        higher_frequency=None,
    )
    outcome2 = OutcomeData(
        submission_id=sub_ids[0],
        project_id=proj_ids[1],  # Project 2
        outcome_id=outcome_dim_ids[0],  # Category 1
        start_date=datetime(2022, 1, 1),
        end_date=datetime(2022, 12, 31),
        unit_of_measurement="Units",
        geography_indicator=GeographyIndicatorEnum.TRAVEL_CORRIDOR,
        amount=200.0,
        state="Actual",
        higher_frequency=None,
    )
    outcome3 = OutcomeData(
        submission_id=sub_ids[0],
        project_id=proj_ids[0],  # Project 1
        outcome_id=outcome_dim_ids[1],  # Category 2
        start_date=datetime(2022, 1, 1),
        end_date=datetime(2022, 12, 31),
        unit_of_measurement="Units",
        geography_indicator=GeographyIndicatorEnum.TRAVEL_CORRIDOR,
        amount=300.0,
        state="Actual",
        higher_frequency=None,
    )
    outcome4 = OutcomeData(
        submission_id=sub_ids[0],
        programme_id=prog_ids[0],  # Programme 1
        outcome_id=outcome_dim_ids[1],  # Category 2
        start_date=datetime(2022, 1, 1),
        end_date=datetime(2022, 12, 31),
        unit_of_measurement="Units",
        geography_indicator=GeographyIndicatorEnum.TRAVEL_CORRIDOR,
        amount=400.0,
        state="Actual",
        higher_frequency=None,
    )
    outcomes = [outcome1, outcome2, outcome3, outcome4]
    db.session.add_all(outcomes)
    return outcomes


@pytest.fixture
def proj_ids(test_client, projects):
    proj_ids = [
        Project.query.filter_by(project_name=projects[idx].project_name).first().id for idx in range(len(projects))
    ]
    return proj_ids


def test_filter_projects_by_itl_regions_match_multiple_itl_regions(projects):
    itl_regions = ["TLD", "TLK"]  # North West, South West
    filtered_projects = Project.filter_projects_by_itl_regions(projects, itl_regions=itl_regions)
    assert set(filtered_projects) == set(projects)


def test_filter_projects_by_itl_regions_match_a_single_itl_region(projects):
    itl_regions = ["TLD"]  # North West
    filtered_projects = Project.filter_projects_by_itl_regions(projects, itl_regions=itl_regions)
    assert set(filtered_projects) == {projects[0], projects[1]}


def test_filter_projects_by_itl_regions_match_none(projects):
    itl_regions = ["TLI"]  # London
    filtered_projects = Project.filter_projects_by_itl_regions(projects, itl_regions=itl_regions)
    assert not filtered_projects


def test_filter_projects_by_outcome_categories_none(test_client):
    (
        projects,
        outcomes,
    ) = Project.filter_projects_by_outcome_categories([], [])

    assert not projects
    assert not outcomes


def test_filter_projects_by_outcome_categories_with_projects_and_categories(projects, outcomes):
    outcome_categories = ["Category 1"]  # links to project 1 and 2

    (
        filtered_projects,
        filtered_outcomes,
    ) = Project.filter_projects_by_outcome_categories(projects, outcome_categories)

    expected_projects = {projects[0], projects[1]}  # project 1 and 2
    expected_outcomes = {outcomes[0], outcomes[1]}  # outcome 1 and 2

    assert set(filtered_projects) == expected_projects
    assert set(filtered_outcomes) == expected_outcomes


def test_filter_projects_by_outcome_categories_no_outcome_categories(projects, outcomes):
    """If no outcomes are provided, then no projects outcomes will match, therefore returns no results."""
    (
        filtered_projects,
        filtered_outcomes,
    ) = Project.filter_projects_by_outcome_categories(projects, [])

    assert not filtered_outcomes  # no outcomes match the outcome_categories due to empty list
    assert not filtered_projects  # no outcomes causes no projects


def test_filter_projects_by_outcome_categories_with_only_outcome_categories(projects, outcomes):
    outcome_categories = ["Category 1"]

    (
        filtered_projects,
        filtered_outcomes,
    ) = Project.filter_projects_by_outcome_categories([], outcome_categories)

    assert not filtered_projects
    assert not filtered_outcomes


def test_filter_programmes_by_outcome_category_none(test_client):
    (
        programmes,
        outcomes,
    ) = Programme.filter_programmes_by_outcome_category([], [])

    assert not programmes
    assert not outcomes


def test_filter_programmes_by_outcome_category(programmes, outcomes):
    outcome_categories = ["Category 2"]

    filtered_programmes, programme_outcomes = Programme.filter_programmes_by_outcome_category(
        programmes, outcome_categories
    )

    assert set(filtered_programmes) == {programmes[0]}
    assert set(programme_outcomes) == {outcomes[3]}


@pytest.fixture()
def additional_test_data():
    submission = Submission(
        submission_id="TEST-SUBMISSION-ID",
        reporting_round=1,
        reporting_period_start=datetime(2019, 10, 10),
        reporting_period_end=datetime(2021, 10, 10),
    )
    organisation = Organisation(organisation_name="TEST-ORGANISATION")
    organisation2 = Organisation(organisation_name="TEST-ORGANISATION2")
    db.session.add_all((submission, organisation, organisation2))
    db.session.flush()

    programme = Programme(
        programme_id="TEST-PROGRAMME-ID",
        programme_name="TEST-PROGRAMME-NAME",
        fund_type_id="TEST",
        organisation_id=organisation.id,
    )

    programme_with_no_projects = Programme(
        programme_id="TEST-PROGRAMME-ID2",
        programme_name="TEST-PROGRAMME-NAME2",
        fund_type_id="TEST2",
        organisation_id=organisation2.id,
    )
    db.session.add_all((programme, programme_with_no_projects))
    db.session.flush()

    # Custom outcome, SW region
    project1 = Project(
        submission_id=submission.id,
        programme_id=programme.id,
        project_id="TEST-PROJECT-ID",
        project_name="TEST-PROJECT-NAME",
        primary_intervention_theme="TEST-PIT",
        locations="TEST-LOCATIONS",
        postcodes="BS3 1AB",  # real postcode area so we can test region filter works
    )

    # No outcomes, SW region
    project2 = Project(
        submission_id=submission.id,
        programme_id=programme.id,
        project_id="TEST-PROJECT-ID2",
        project_name="TEST-PROJECT-NAME2",
        primary_intervention_theme="TEST-PIT2",
        locations="TEST-LOCATIONS2",
        postcodes="BS3 1AB",  # real postcode area so we can test region filter works
    )

    # Transport outcome, SW region
    project3 = Project(
        submission_id=submission.id,
        programme_id=programme.id,
        project_id="TEST-PROJECT-ID3",
        project_name="TEST-PROJECT-NAME3",
        primary_intervention_theme="TEST-PIT3",
        locations="TEST-LOCATIONS3",
        postcodes="BS3 1AB",  # real postcode area so we can test region filter works
    )

    # Transport outcome, no region
    project4 = Project(
        submission_id=submission.id,
        programme_id=programme.id,
        project_id="TEST-PROJECT-ID4",
        project_name="TEST-PROJECT-NAME4",
        primary_intervention_theme="TEST-PIT4",
        locations="TEST-LOCATIONS4",
        postcodes="",  # no postcode == no region
    )

    db.session.add_all((project1, project2, project3, project4))
    db.session.flush()

    test_outcome_dim = OutcomeDim(outcome_name="TEST-OUTCOME-1", outcome_category="TEST-OUTCOME-CATEGORY")
    transport_outcome_dim = OutcomeDim(outcome_name="TEST-OUTCOME-2", outcome_category="Transport")
    db.session.add_all((test_outcome_dim, transport_outcome_dim))
    db.session.flush()

    project_outcome1 = OutcomeData(
        submission_id=submission.id,
        project_id=project1.id,  # linked to project1
        outcome_id=test_outcome_dim.id,  # linked to TEST-OUTCOME-CATEGORY OutcomeDim
        start_date=datetime(2022, 1, 1),
        end_date=datetime(2022, 12, 31),
        unit_of_measurement="Units",
        geography_indicator=GeographyIndicatorEnum.LOWER_LAYER_SUPER_OUTPUT_AREA,
        amount=100.0,
        state="Actual",
        higher_frequency=None,
    )

    project_outcome2 = OutcomeData(
        submission_id=submission.id,
        project_id=project3.id,  # linked to project3
        outcome_id=transport_outcome_dim.id,  # linked to Transport OutcomeDim
        start_date=datetime(2021, 1, 1),
        end_date=datetime(2022, 12, 31),
        unit_of_measurement="Units",
        geography_indicator=GeographyIndicatorEnum.TRAVEL_CORRIDOR,
        amount=100.0,
        state="Actual",
        higher_frequency=None,
    )

    programme_outcome = OutcomeData(
        submission_id=submission.id,
        programme_id=programme.id,  # linked to programme
        outcome_id=test_outcome_dim.id,  # linked to Transport OutcomeDim
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2023, 12, 31),
        unit_of_measurement="Units",
        geography_indicator=GeographyIndicatorEnum.TOWN,
        amount=26.0,
        state="Actual",
        higher_frequency=None,
    )

    programme_outcome2 = OutcomeData(
        submission_id=submission.id,
        programme_id=programme_with_no_projects.id,  # linked to programme
        outcome_id=test_outcome_dim.id,  # linked to Transport OutcomeDim
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2023, 12, 31),
        unit_of_measurement="Units",
        geography_indicator=GeographyIndicatorEnum.TOWN,
        amount=26.0,
        state="Actual",
        higher_frequency=None,
    )

    db.session.add_all((project_outcome1, project_outcome2, programme_outcome, programme_outcome2))
    db.session.flush()

    return (
        organisation,
        submission,
        programme,
        programme_with_no_projects,
        project1,
        project2,
        project3,
        project4,
        test_outcome_dim,
        transport_outcome_dim,
    )


def test_get_programme_ids(seeded_test_client, additional_test_data):
    (
        organisation,
        submission,
        programme,
        programme_with_no_projects,
        project1,
        project2,
        project3,
        project4,
        test_outcome_dim,
        transport_outcome_dim,
    ) = additional_test_data

    all_programmes = Programme.query.all()

    # all programmes are returned when no filters are provided
    programme_uuids, programme_ids = get_programme_ids()
    assert set(programme_ids) == {programme.programme_id for programme in all_programmes}
    assert set(programme_uuids) == {programme.id for programme in all_programmes}

    # programmes of a given organisation are returned (filters: org)
    # only return the programme from additional_test_data
    org_ids = [organisation.id]
    programme_uuids, programme_ids = get_programme_ids(organisation_ids=org_ids)
    assert set(programme_ids) == {programme.programme_id}
    assert set(programme_uuids) == {programme.id}
    assert all(
        programme.organisation.id == organisation.id  # assert all programmes are of the filtered organisation
        for programme in Programme.query.filter(Programme.id.in_(programme_uuids)).all()
    )

    # programmes of a given fund type are returned (filters: fund type)
    # only return the programme from additional_test_data
    fund_types = [programme_with_no_projects.fund_type_id]
    programme_uuids, programme_ids = get_programme_ids(fund_types=fund_types)
    assert set(programme_ids) == {programme_with_no_projects.programme_id}
    assert set(programme_uuids) == {programme_with_no_projects.id}
    assert all(
        programme.fund_type_id == programme_with_no_projects.fund_type_id
        # assert all programmes are of the filtered fund type
        for programme in Programme.query.filter(Programme.id.in_(programme_uuids)).all()
    )


def test_get_programme_ids_returns_none(test_client):
    # if we pass a non-existent fund type on its own we should receive no programme data
    fund_types = ["NOT-EXISTING"]
    programme_uuids, programme_ids = get_programme_ids(fund_types=fund_types)
    assert programme_uuids is None
    assert programme_ids is None

    # if we pass a non-existent organisation type on its own we should receive no programme data
    organisation_ids = [uuid.uuid4()]
    programme_uuids, programme_ids = get_programme_ids(organisation_ids=organisation_ids)
    assert programme_uuids is None
    assert programme_ids is None


def test_get_project_ids(seeded_test_client, additional_test_data):
    (
        organisation,
        submission,
        programme,
        programme_with_no_projects,
        project1,
        project2,
        project3,
        project4,
        test_outcome_dim,
        transport_outcome_dim,
    ) = additional_test_data

    all_sub_ids = [sub.id for sub in Submission.query.all()]
    all_projects = Project.query.all()
    all_project_uuids = [project.id for project in all_projects]

    # all projects are returned when no filtering (filters: all submissions)
    project_uuids, project_ids = filter_project_ids(all_project_uuids, submission_uuids=all_sub_ids)
    assert set(project_ids) == set((project.project_id for project in all_projects))
    assert set(project_uuids) == set((project.id for project in all_projects))

    # projects from a given submission are returned (filters: one submission)
    project_uuids, project_ids = filter_project_ids(all_project_uuids, submission_uuids=[submission.id])
    assert set(project_ids) == {project1.project_id, project2.project_id, project3.project_id, project4.project_id}
    assert set(project_uuids) == {project1.id, project2.id, project3.id, project4.id}

    # projects are filtered by region (filters: all submissions, South West region)
    project_uuids, project_ids = filter_project_ids(
        all_project_uuids, submission_uuids=all_sub_ids, itl_regions={ITLRegion.SouthWest}
    )
    assert project4.project_id not in project_ids  # project4 not in SW
    assert set(project_ids) == {project1.project_id, project2.project_id, project3.project_id}
    assert set(project_uuids) == {project1.id, project2.id, project3.id}
    assert all(
        project.itl_regions.intersection({ITLRegion.SouthWest})  # assert regions align
        for project in Project.query.filter(Project.id.in_(project_uuids)).all()
    )

    # if all regions are passed, then do not filter by region
    itl_regions = {region for region in ITLRegion}
    project_uuids, project_ids = filter_project_ids(
        all_project_uuids, submission_uuids=all_sub_ids, itl_regions=itl_regions
    )
    assert (
        project4.project_id in project_ids
    )  # project4 does not have a region, but we shouldn't filter it out this time

    # returns no project data if region doesn't exist in the data
    project_uuids, project_ids = filter_project_ids(
        all_project_uuids, submission_uuids=all_sub_ids, itl_regions={"NON-EXISTENT-REGION"}
    )
    assert project_uuids is None
    assert project_ids is None


def test_get_child_projects(seeded_test_client, additional_test_data):
    (
        organisation,
        submission,
        programme,
        programme_with_no_projects,
        project1,
        project2,
        project3,
        project4,
        test_outcome_dim,
        transport_outcome_dim,
    ) = additional_test_data

    # returns children projects of a programme
    programme_uuids = [programme.id]
    project_uuids, project_ids = get_child_projects(programme_uuids)
    assert len(project_uuids) == 4
    assert set(project_uuids) == {project1.id, project2.id, project3.id, project4.id}
    assert set(project_ids) == {project1.project_id, project2.project_id, project3.project_id, project4.project_id}
    assert all(project.programme_id == programme.id for project in Project.query.filter(Project.id.in_(project_uuids)))

    # programme with no children projects returns None, None
    programme_uuids = [programme_with_no_projects.id]
    project_uuids, project_ids = get_child_projects(programme_uuids)
    assert project_uuids is None
    assert project_ids is None

    # still returns children projects of a programme even when a programme with no children is also passed
    programme_uuids = [programme.id, programme_with_no_projects.id]  # with projects  # with no projects
    project_uuids, project_ids = get_child_projects(programme_uuids)
    assert len(project_uuids) == 4
    assert set(project_uuids) == {project1.id, project2.id, project3.id, project4.id}
    assert set(project_ids) == {project1.project_id, project2.project_id, project3.project_id, project4.project_id}
    assert all(project.programme_id == programme.id for project in Project.query.filter(Project.id.in_(project_uuids)))

    # no programmes return None, None
    programme_uuids = []  # empty list
    project_uuids, project_ids = get_child_projects(programme_uuids)
    assert project_uuids is None
    assert project_ids is None


def test_get_parent_programmes(seeded_test_client, additional_test_data):
    (
        organisation,
        submission,
        programme,
        programme_with_no_projects,
        project1,
        project2,
        project3,
        project4,
        test_outcome_dim,
        transport_outcome_dim,
    ) = additional_test_data

    # returns parent programme of a project
    project_uuids = [project1.id]
    programme_uuids, programme_ids = get_parent_programmes(project_uuids)
    assert len(programme_uuids) == 1
    assert set(programme_uuids) == {programme.id}
    assert set(programme_ids) == {programme.programme_id}

    # returns a single instance of a parent programme when multiple child projects are passed
    project_uuids = [project1.id, project2.id]
    programme_uuids, programme_ids = get_parent_programmes(project_uuids)
    assert len(programme_uuids) == 1
    assert set(programme_uuids) == {programme.id}
    assert set(programme_ids) == {programme.programme_id}

    # if no projects are passed, returns None, None
    project_uuids = []  # empty list
    programme_uuids, programme_ids = get_parent_programmes(project_uuids)
    assert programme_uuids is None
    assert programme_ids is None


def test_get_download_data_ids(seeded_test_client, additional_test_data):
    def assert_all_child_projects_returned(programme_uuids, project_uuids):
        all_programme_child_projects = [
            project
            for programme in Programme.query.filter(Programme.id.in_(programme_uuids))
            for project in programme.projects
        ]
        same_length = len(all_programme_child_projects) == len(project_uuids)
        same_content = set(all_programme_child_projects) == {
            project for project in Project.query.filter(Project.id.in_(project_uuids))
        }
        return same_length and same_content

    (
        organisation,
        submission,
        programme,
        programme_with_no_projects,
        project1,
        project2,
        project3,
        project4,
        test_outcome_dim,
        transport_outcome_dim,
    ) = additional_test_data

    # programmes with no children should still not show up even if no filters are passed
    submission_uuids, programme_uuids, project_uuids = get_download_data_ids()
    assert programme_with_no_projects.id not in programme_uuids

    # all submission data should be within the specified reporting period range
    min_rp_start = submission.reporting_period_start - timedelta(days=1)
    max_rp_end = submission.reporting_period_end + timedelta(days=1)
    submission_uuids, programme_uuids, project_uuids = get_download_data_ids(
        min_rp_start=min_rp_start, max_rp_end=max_rp_end
    )
    # returns only the relevant submission
    assert len(submission_uuids) == 1
    assert submission_uuids[0] == submission.id
    # every project is linked to the relevant submission
    assert all(
        project.submission_id == submission.id for project in Project.query.filter(Project.id.in_(project_uuids))
    )
    assert programme_with_no_projects.id not in programme_uuids  # any programmes with no children should not show up

    # when organisation is passed but no other filters, programmes should be filtered by org and all of their child
    # projects returned
    organisation_uuids = [organisation.id]
    submission_uuids, programme_uuids, project_uuids = get_download_data_ids(organisation_uuids=organisation_uuids)
    assert all(
        programme.organisation_id == organisation.id
        for programme in Programme.query.filter(Programme.id.in_(programme_uuids))
    )
    assert assert_all_child_projects_returned(programme_uuids, project_uuids)

    # when fund type is passed but no other filters, programmes should be filtered by fund type and all of their
    # child projects returned
    fund_type_ids = [programme.fund_type_id]
    submission_uuids, programme_uuids, project_uuids = get_download_data_ids(fund_type_ids=fund_type_ids)
    assert all(
        programme.fund_type_id == programme.fund_type_id
        for programme in Programme.query.filter(Programme.id.in_(programme_uuids))
    )
    assert assert_all_child_projects_returned(programme_uuids, project_uuids)

    # when ITL region is passed, projects should be filtered by ITL region and any parent programmes with entirely
    # filtered out child projects should not be returned
    itl_regions = {ITLRegion.SouthWest}
    submission_uuids, programme_uuids, project_uuids = get_download_data_ids(itl_regions=itl_regions)
    assert project4.id not in project_uuids  # not in SW region
    assert all(
        ITLRegion.SouthWest in project.itl_regions for project in Project.query.filter(Project.id.in_(project_uuids))
    )

    # when both ITL region and fund_type is passed, return relevant results
    itl_regions = {ITLRegion.SouthWest}
    fund_type_ids = [programme.fund_type_id]
    submission_uuids, programme_uuids, project_uuids = get_download_data_ids(
        fund_type_ids=fund_type_ids, itl_regions=itl_regions
    )
    assert project4.id not in project_uuids  # not in SW region
    assert all(
        programme.fund_type_id == programme.fund_type_id
        for programme in Programme.query.filter(Programme.id.in_(programme_uuids))
    )
    assert all(
        ITLRegion.SouthWest in project.itl_regions for project in Project.query.filter(Project.id.in_(project_uuids))
    )


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
    assert outcome_data_df["outcome_id"].is_unique

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
    assert len(OutcomeData.query.all()) == 30
    programme_with_no_projects = additional_test_data[3]

    # programmes with no children should still not show up even if no filters are passed
    test_query = get_download_data_query()
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
    test_query_out = expected_outcome_join(test_query)
    test_df_out = pd.read_sql(test_query_out.statement, con=db.engine.connect())

    # check all Outputs show up via the above query. There is 1 extra that should not show up (programme w. no projects)
    all_outcomes = [row.id for row in OutcomeData.query.all()]
    left_over_uuid = set(all_outcomes) - set(test_df_out["outcome_id"])
    assert len(left_over_uuid) == 1
    left_over_outcome = OutcomeData.query.filter(OutcomeData.id == left_over_uuid.pop()).first()
    # The only Outcome NOT returned by the query is the ONE linked to programme without projects (Not valid).
    assert programme_with_no_projects.id == left_over_outcome.programme_id

    outcome_data_structure_common_test(test_df_out)

    # TODO: test this with outcome filter applied
    # TODO: also, check that (when filtered on outcome) ONLY expected projects and programmes
    #  turn up here, and in other project level tables :
    #  specific case:
    #  - 1 Programme matches outcome filter, 2 projects match outcome filter.
    #  - 1 of the projects is a child of programme, one isn't
    #  check in outcomes table, that only these 3 rows show up, 2 proj, 1 prog)
    #  check in project table, all children of prog turn up + 1 proj in filter with different prog
    #  check in programme table, both turn up
    #  - apply different filter, that matches 1 programme level outcome only
    #  check child projects turn up in project tabs, but not outcomes
    #  check only this programme turns up in programme table
    #  - repeat for filter that just hits one project outcome (no programmes)
    #  check only 1 project turns up in project tabs and outcomes tab

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

    submission = additional_test_data[1]

    # for assertion comparisons. Increase date range on filters to include all records
    max_rp_end = submission.reporting_period_end + timedelta(weeks=(52 * 2))
    test_query_all = get_download_data_query(min_rp_start=submission.reporting_period_start, max_rp_end=max_rp_end)
    test_query_all_subs = test_query_all.with_entities(
        Submission.id,
        Submission.reporting_period_start,
        Submission.reporting_period_end,
    ).distinct()

    test_all_df = pd.read_sql(test_query_all_subs.statement, con=db.engine.connect())

    # all submission data should be within the specified reporting period range
    min_rp_start = submission.reporting_period_start - timedelta(days=1)
    max_rp_end = submission.reporting_period_end + timedelta(days=1)

    test_query_dates = get_download_data_query(min_rp_start=min_rp_start, max_rp_end=max_rp_end)
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
    submission = additional_test_data[1]

    #  date range to include all records
    max_rp_end = submission.reporting_period_end + timedelta(weeks=(52 * 2))
    test_query_all = get_download_data_query(max_rp_end=max_rp_end)
    test_query_all_proj = test_query_all.with_entities(
        Project.project_id,
    ).distinct()

    test_all_results = test_query_all_proj.all()
    assert len(test_all_results) == 12

    #  using an earlier end date as the only param reduced the rows returned.
    test_query_reduced = get_download_data_query(max_rp_end=submission.reporting_period_end)
    test_query_reduced_proj = test_query_reduced.with_entities(
        Project.project_id,
    ).distinct()
    test_reduced_results = test_query_reduced_proj.all()
    assert len(test_reduced_results) == 4


def test_get_download_data_start_date_filter(seeded_test_client, additional_test_data):
    """Test date filter with only start date parameter."""

    submission = additional_test_data[1]

    #  date range to include all records
    test_query_all = get_download_data_query(min_rp_start=submission.reporting_period_start)
    test_query_all_proj = test_query_all.with_entities(
        Project.project_id,
    ).distinct()

    test_all_results = test_query_all_proj.all()
    assert len(test_all_results) == 12

    #  using a later start date as the only param reduced the rows returned.
    max_rp_end = submission.reporting_period_start + timedelta(weeks=(52 * 2))
    test_query_reduced = get_download_data_query(min_rp_start=max_rp_end)
    test_query_reduced_proj = test_query_reduced.with_entities(
        Project.project_id,
    ).distinct()
    test_reduced_results = test_query_reduced_proj.all()
    assert len(test_reduced_results) == 8


def test_get_download_data_organisation_filter(seeded_test_client, additional_test_data):
    """Pass organisation filter params and check rows"""
    organisation = additional_test_data[0]
    organisation_uuids = [organisation.id]

    test_query_org = get_download_data_query(organisation_uuids=organisation_uuids)

    test_query_org_ents = test_query_org.with_entities(
        Submission.submission_id,
        Organisation.id,
        Organisation.organisation_name,
        Project.project_id,
        Programme.programme_id,
    ).distinct()

    db.session.flush()

    test_query_org_all = (
        get_download_data_query()
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

    programme = additional_test_data[2]
    fund_type_ids = [programme.fund_type_id]

    test_query_fund_type = get_download_data_query(fund_type_ids=fund_type_ids)

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
    test_query_region = get_download_data_query(itl_regions=itl_regions)

    test_query_region_ents = test_query_region.with_entities(
        Project.id,
        Project.project_id,
        # Project.itl_regions,
    ).distinct()

    test_fund_filtered_df = pd.read_sql(test_query_region_ents.statement, con=db.engine.connect())

    project4 = additional_test_data[7]

    assert project4.id not in test_fund_filtered_df.id  # not in SW region
    assert all(
        ITLRegion.SouthWest in project.itl_regions
        for project in Project.query.filter(Project.id.in_(test_fund_filtered_df.id))
    )


def test_get_download_data_region_and_fund(seeded_test_client, additional_test_data):
    # when both ITL region and fund_type filter params are passed, return relevant results

    (
        _,
        _,
        programme,
        _,
        _,
        _,
        _,
        project4,
        _,
        _,
    ) = additional_test_data

    itl_regions = {ITLRegion.SouthWest}
    fund_type_ids = [programme.fund_type_id]

    test_query_region_fund = get_download_data_query(fund_type_ids=fund_type_ids, itl_regions=itl_regions)

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
    (
        organisation,
        _,
        programme,
        _,
        _,
        _,
        _,
        _,
        _,
        _,
    ) = additional_test_data

    organisation_uuids = [organisation.id]
    itl_regions = {ITLRegion.SouthWest}
    fund_type_ids = [programme.fund_type_id]

    test_query = get_download_data_query(
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


def test_outcome_category_filter(seeded_test_client, additional_test_data):
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

    assert len(OutcomeData.query.all()) == 30

    # reference data, all Outcome data, unfiltered / un-joined.
    test_query = get_download_data_query()
    test_query = test_query.with_entities(OutcomeData, OutcomeDim).distinct()
    test_df_categories_unfiltered = pd.read_sql(test_query.statement, con=db.engine.connect())
    test_query = test_query.with_entities(Project, Programme).distinct()
    test_df_projects_unfiltered = pd.read_sql(test_query.statement, con=db.engine.connect())

    #  apply filter to outcomes.
    test_query = get_download_data_query(outcome_categories=["Transport"])

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


def get_results_as_tuples_of_columns(query, cols) -> tuple[None, ...]:
    """Executes an SQLAlchemy query and returns as a set of tuples, each representing a column.

    :param query: the query to execute
    :param cols: number of columns to be returned (i.e. values in the select statement)
    :return:
    """
    results = [tuple(row) for row in query.all()]
    if results:
        tuples_of_columns = zip(*results)
        return tuples_of_columns
    else:
        # if no results, return None for each missing column of data
        return tuple(None for _ in range(cols))
