from datetime import datetime

import pytest

from core.const import GeographyIndicatorEnum, MultiplicityEnum
from core.db import db

# isort: off
from core.db.entities import Organisation, OutcomeData, OutcomeDim, Programme, Project, Submission

# isort: on


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


def test_get_submissions_by_reporting_period_all(submissions):
    result = Submission.get_submissions_by_reporting_period(None, None)

    assert len(result) == len(submissions)
    assert all(sub in result for sub in submissions)


def test_get_submissions_by_reporting_period_with_start_and_end(submissions):
    start = datetime(2023, 3, 1)
    end = datetime(2023, 5, 31)

    result = Submission.get_submissions_by_reporting_period(start, end)

    assert len(result) == 2
    assert all(
        start <= sub.reporting_period_start <= end and start <= sub.reporting_period_end <= end for sub in result
    )


def test_get_submissions_by_reporting_period_with_start(submissions):
    start = datetime(2023, 6, 1)

    result = Submission.get_submissions_by_reporting_period(start, None)

    assert len(result) == 2
    assert all(start <= sub.reporting_period_start for sub in result)


def test_get_submissions_by_reporting_period_with_end(submissions):
    end = datetime(2023, 6, 30)

    result = Submission.get_submissions_by_reporting_period(None, end)

    assert len(result) == len(submissions)
    assert all(sub.reporting_period_end <= end for sub in result)


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
        location_multiplicity=MultiplicityEnum.MULTIPLE,
        locations="Location 1",
        gis_provided="Yes",
        lat_long="12345",
    )
    proj2 = Project(
        project_id="2",
        submission_id=sub_ids[1],
        programme_id=prog_ids[1],  # prog 2
        project_name="Project 2",
        primary_intervention_theme="Theme 2",
        location_multiplicity=MultiplicityEnum.MULTIPLE,
        locations="Location 2",
        gis_provided="No",
        lat_long=None,
    )
    proj3 = Project(
        project_id="3",
        submission_id=sub_ids[0],
        programme_id=prog_ids[0],  # prog 1
        project_name="Project 3",
        primary_intervention_theme="Theme 1",
        location_multiplicity=MultiplicityEnum.MULTIPLE,
        locations="Location 3",
        gis_provided="Yes",
        lat_long="67890",
    )
    proj4 = Project(
        project_id="4",
        submission_id=sub_ids[1],
        programme_id=prog_ids[1],  # prog 2
        project_name="Project 4",
        primary_intervention_theme="Theme 2",
        location_multiplicity=MultiplicityEnum.MULTIPLE,
        locations="Location 4",
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


def test_filter_projects_by_outcome_categories_with_only_projects(projects, outcomes):
    (
        filtered_projects,
        filtered_outcomes,
    ) = Project.filter_projects_by_outcome_categories(projects, [])

    expected_projects = set(projects)  # all projects
    expected_outcomes = {outcomes[0], outcomes[1], outcomes[2]}  # all outcomes linked to projects (not programme)

    assert set(filtered_projects) == expected_projects
    assert set(filtered_outcomes) == expected_outcomes


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
