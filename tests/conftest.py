from datetime import datetime

import pytest

from app import create_app
from core.const import GeographyIndicatorEnum
from core.db import db
from core.db.entities import (
    Organisation,
    OutcomeData,
    OutcomeDim,
    Programme,
    Project,
    Submission,
)


@pytest.fixture
def test_client():
    """
    Returns a test client with pushed application context.

    Wipes db after use.

    :return: a flask test client with application context.
    """
    with create_app().test_client() as test_client:
        with test_client.application.app_context():
            db.create_all()
            yield test_client
            db.session.remove()
            db.drop_all()


@pytest.fixture
def seeded_test_client(test_client):
    """
    Load seed data into test database.

    NOTE: This is currently seeded via the ingest endpoint due to time constraints.

    This is a fixture. Extends test_client.

    :return: a flask test client with application context and seeded db.
    """
    # TODO: Replace seeding via ingest with independent test seed data.
    with open(test_client.application.config["EXAMPLE_DATA_MODEL_PATH"], "rb") as example_data_model_file:
        endpoint = "/ingest"
        response = test_client.post(
            endpoint,
            data={
                "excel_file": example_data_model_file,
            },
        )
        # check endpoint gave a success response to ingest
        assert response.status_code == 200
        yield test_client


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
