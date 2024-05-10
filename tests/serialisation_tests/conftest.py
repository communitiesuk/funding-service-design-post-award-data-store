from datetime import datetime

import pytest

from core.const import GeographyIndicatorEnum
from core.db import db
from core.db.entities import (
    Fund,
    Organisation,
    OutcomeData,
    OutcomeDim,
    Programme,
    ProgrammeJunction,
    Project,
    Submission,
)


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
        fund_type_id=Fund.query.first().id,
        organisation_id=organisation.id,
    )
    db.session.add(programme_no_transport_outcome_or_transport_child_projects)
    db.session.flush()

    programme_junction = ProgrammeJunction(
        submission_id=submission.id,
        programme_id=programme_no_transport_outcome_or_transport_child_projects.id,
        reporting_round=submission.reporting_round,
    )
    db.session.add(programme_junction)
    db.session.flush()

    # Custom outcome, SW region, no transport outcome in programmes or & projects
    project = Project(
        programme_junction_id=programme_junction.id,
        project_id="TEST-PROJECT-ID5",
        project_name="TEST-PROJECT-NAME5",
        data_blob={
            "primary_intervention_theme": "TEST-PIT",
            "locations": "TEST-LOCATIONS",
        },
    )
    db.session.add(project)
    db.session.flush()
    non_transport_outcome = OutcomeData(
        project_id=project.id,  # linked to project1
        outcome_id=test_outcome_dim.id,  # linked to TEST-OUTCOME-CATEGORY OutcomeDim
        start_date=datetime(2022, 1, 1),
        end_date=datetime(2022, 12, 31),
        data_blob={
            "unit_of_measurement": "Units",
            "geography_indicator": GeographyIndicatorEnum.LOWER_LAYER_SUPER_OUTPUT_AREA,
            "amount": 100.0,
            "state": "Actual",
            "higher_frequency": None,
        },
    )
    db.session.add(non_transport_outcome)
    db.session.commit()

    return programme_no_transport_outcome_or_transport_child_projects
