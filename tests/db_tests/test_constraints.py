"""Tests for sqla CheckConstraints table_args on model."""

from datetime import datetime, timedelta

import pytest
from sqlalchemy.exc import IntegrityError

from core.db import db
from core.db.entities import (
    Fund,
    Funding,
    GeospatialDim,
    Organisation,
    OutcomeData,
    OutcomeDim,
    OutputData,
    OutputDim,
    Programme,
    ProgrammeFundingManagement,
    ProgrammeJunction,
    Project,
    ProjectProgress,
    RiskRegister,
    Submission,
)


def test_funding_constraint_dates_both_null(seeded_test_client_rollback):
    invalid_funding_row = Funding(
        project_id=Project.query.first().id,
        start_date=None,
        end_date=None,  # both date fields cannot be null at the same time
    )
    db.session.add(invalid_funding_row)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_outcome_constraint_project_xor_programme(seeded_test_client_rollback):
    invalid_outcome_row_both = OutcomeData(
        programme_junction_id=ProgrammeJunction.query.first().id,
        project_id=Project.query.first().id,  # cannot have both programme_junction_id and project_id
        outcome_id=OutcomeDim.query.first().id,
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    db.session.add(invalid_outcome_row_both)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()

    invalid_outcome_row_neither = OutcomeData(
        programme_junction_id=None,
        project_id=None,  # must have one of programme_junction_id or project_id
        outcome_id=OutcomeDim.query.first().id,
        start_date=datetime.now(),
        end_date=datetime.now(),
    )
    db.session.add(invalid_outcome_row_neither)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_risk_constraint_project_xor_programme(seeded_test_client_rollback):
    invalid_risk_row_both = RiskRegister(
        programme_junction_id=ProgrammeJunction.query.first().id,
        project_id=Project.query.first().id,  # cannot have both programme_junction_id and project_id
    )
    db.session.add(invalid_risk_row_both)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()

    invalid_risk_row_neither = RiskRegister(
        programme_junction_id=None,
        project_id=None,  # must have one of programme_junction_id and project_id
    )

    db.session.add(invalid_risk_row_neither)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_funding_constraint_project_xor_programme(seeded_test_client_rollback):
    invalid_funding_row_both = Funding(
        programme_junction_id=ProgrammeJunction.query.first().id,
        project_id=Project.query.first().id,  # cannot have both programme_junction_id and project_id
    )
    db.session.add(invalid_funding_row_both)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()

    invalid_funding_row_neither = Funding(
        programme_junction_id=None,
        project_id=None,  # must have one of programme_junction_id and project_id
    )

    db.session.add(invalid_funding_row_neither)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_output_constraint_project_xor_programme(seeded_test_client_rollback):
    invalid_output_row_both = OutputData(
        programme_junction_id=ProgrammeJunction.query.first().id,
        project_id=Project.query.first().id,  # cannot have both programme_junction_id and project_id
        output_id=OutputDim.query.first().id,
    )
    db.session.add(invalid_output_row_both)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()

    invalid_output_row_neither = OutputData(
        programme_junction_id=None,
        project_id=None,  # must have one of programme_junction_id and project_id
        output_id=OutputDim.query.first().id,
    )

    db.session.add(invalid_output_row_neither)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_geospatial_dim_unique_constraint(test_client_rollback):
    """Tests the unique constraint on geospatial_dim postcode_prefix."""

    geospatial = GeospatialDim(postcode_prefix="HP", itl1_region_code="TEST")
    same_geospatial = GeospatialDim(postcode_prefix="HP", itl1_region_code="TEST")
    db.session.add_all([geospatial, same_geospatial])

    with pytest.raises(IntegrityError):
        db.session.flush()


def test_project_geospatial_association_pk_constraint(seeded_test_client_rollback):
    """Tests the unique constraint on project_geospatial_association."""

    geospatial = GeospatialDim.query.filter_by(postcode_prefix="SW").one()
    geospatial_2 = GeospatialDim.query.filter_by(postcode_prefix="SW").one()
    submission = Submission(
        submission_id="TEST-SUBMISSION-ID",
        reporting_period_start=datetime(2019, 10, 10),
        reporting_period_end=datetime(2021, 10, 10),
    )

    organisation = Organisation(organisation_name="TEST-ORGANISATION")
    db.session.add_all((submission, organisation))
    db.session.flush()

    fund = Fund(
        fund_code="TEST",
    )

    db.session.add(fund)
    db.session.flush()

    programme = Programme(
        programme_id="TEST-PROGRAMME-ID",
        programme_name="TEST-PROGRAMME-NAME",
        fund_type_id=fund.id,
        organisation_id=organisation.id,
    )

    db.session.add(programme)
    db.session.flush()

    programme_junction = ProgrammeJunction(
        submission_id=submission.id,
        programme_id=programme.id,
        reporting_round=1,
    )
    db.session.add(programme_junction)
    db.session.flush()
    project1 = Project(
        programme_junction_id=programme_junction.id,
        project_id="TEST-PROJECT-ID",
        project_name="TEST-PROJECT-NAME",
        data_blob={"primary_intervention_theme": "TEST-PIT", "locations": "TEST-LOCATIONS"},
        postcodes=["SW1 2PQ"],
    )
    project1.geospatial_dims.append(geospatial)
    project1.geospatial_dims.append(geospatial_2)
    db.session.add(project1)

    with pytest.raises(IntegrityError) as error:
        db.session.flush()
    assert 'duplicate key value violates unique constraint "pk_project_geospatial_association"' in error.value.args[0]


class TestConstraintOnStartAndEndDates:
    def test_funding_model_nullable_dates(self, seeded_test_client_rollback):
        f = Funding(
            programme_junction_id=ProgrammeJunction.query.first().id,
            data_blob={},
            start_date=datetime.now(),
            end_date=datetime.now() - timedelta(seconds=1),
        )
        db.session.add(f)

        with pytest.raises(IntegrityError) as e:
            db.session.commit()

        assert "ck_funding_start_before_end" in str(e.value)

    def test_programme_funding_management_model_nullable_dates(self, seeded_test_client_rollback):
        pfm = ProgrammeFundingManagement(
            programme_junction_id=ProgrammeJunction.query.first().id,
            data_blob={},
            start_date=datetime.now(),
            end_date=datetime.now() - timedelta(seconds=1),
        )
        db.session.add(pfm)

        with pytest.raises(IntegrityError) as e:
            db.session.commit()

        assert "ck_programme_funding_management_start_before_end" in str(e.value)

    def test_project_progress_model_nullable_dates(self, seeded_test_client_rollback):
        pp = ProjectProgress(
            project_id=Project.query.first().id,
            data_blob={},
            start_date=datetime.now(),
            end_date=datetime.now() - timedelta(seconds=1),
        )
        db.session.add(pp)

        with pytest.raises(IntegrityError) as e:
            db.session.commit()

        assert "ck_project_progress_start_before_end" in str(e.value)

    def test_outcome_data_model_non_nullable_dates(self, seeded_test_client_rollback):
        od = OutcomeData(
            programme_junction_id=ProgrammeJunction.query.first().id,
            outcome_id=OutcomeDim.query.first().id,
            start_date=datetime.now(),
            end_date=datetime.now() - timedelta(seconds=1),
            data_blob={},
        )
        db.session.add(od)

        with pytest.raises(IntegrityError) as e:
            db.session.commit()

        assert "ck_outcome_data_start_before_end" in str(e.value)

    def test_output_data_model_non_nullable_dates(self, seeded_test_client_rollback):
        od = OutputData(
            programme_junction_id=ProgrammeJunction.query.first().id,
            output_id=OutputDim.query.first().id,
            start_date=datetime.now(),
            end_date=datetime.now() - timedelta(seconds=1),
            data_blob={},
        )
        db.session.add(od)

        with pytest.raises(IntegrityError) as e:
            db.session.commit()

        assert "ck_output_data_start_before_end" in str(e.value)

    def test_reporting_period_start_and_end_dates(self, seeded_test_client_rollback):
        s = Submission(
            submission_id="TEST",
            reporting_period_start=datetime.now(),
            reporting_period_end=datetime.now() - timedelta(seconds=1),
        )
        db.session.add(s)

        with pytest.raises(IntegrityError) as e:
            db.session.commit()

        assert "ck_submission_dim_start_before_end" in str(e.value)


def test_fund_dim_unique_constraint(test_client_rollback):
    """Tests the unique constraint on fund_dim."""

    fund = Fund(fund_code="JP")
    same_fund = Fund(fund_code="JP")
    db.session.add_all([fund, same_fund])

    with pytest.raises(IntegrityError):
        db.session.flush()
