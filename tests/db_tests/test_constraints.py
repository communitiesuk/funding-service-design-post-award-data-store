"""Tests for sqla CheckConstraints table_args on model."""
from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from core.db import db

# isort: off
from core.db.entities import Funding, OutcomeData, OutcomeDim, Programme, Project, RiskRegister, Submission


def test_funding_constraint_dates_both_null(seeded_test_client):
    invalid_funding_row = Funding(
        submission_id=Submission.query.first().id,
        project_id=Project.query.first().id,
        funding_source_name="test name",
        funding_source_type="test_type",
        start_date=None,
        end_date=None,  # both date fields cannot be null at the same time
    )
    db.session.add(invalid_funding_row)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_outcome_constraint_project_xor_programme(seeded_test_client):
    invalid_outcome_row_both = OutcomeData(
        submission_id=Submission.query.first().id,
        programme_id=Programme.query.first().id,
        project_id=Project.query.first().id,  # cannot have both programme_id and project_id
        outcome_id=OutcomeDim.query.first().id,
        start_date=datetime.now(),
        end_date=datetime.now(),
        unit_of_measurement="blah",
        state="Actual",
    )
    db.session.add(invalid_outcome_row_both)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()

    invalid_outcome_row_neither = OutcomeData(
        submission_id=Submission.query.first().id,
        programme_id=None,
        project_id=None,  # must have one of programme_id and project_id
        outcome_id=OutcomeDim.query.first().id,
        start_date=datetime.now(),
        end_date=datetime.now(),
        unit_of_measurement="blah",
        state="Actual",
    )
    db.session.add(invalid_outcome_row_neither)
    with pytest.raises(IntegrityError):
        db.session.commit()


def test_risk_constraint_project_xor_programme(seeded_test_client):
    invalid_risk_row_both = RiskRegister(
        submission_id=Submission.query.first().id,
        programme_id=Programme.query.first().id,
        project_id=Project.query.first().id,  # cannot have both programme_id and project_id
        risk_name="blah",
    )
    db.session.add(invalid_risk_row_both)
    with pytest.raises(IntegrityError):
        db.session.commit()
    db.session.rollback()

    invalid_risk_row_neither = RiskRegister(
        submission_id=Submission.query.first().id,
        programme_id=None,
        project_id=None,  # must have one of programme_id and project_id
        risk_name="blah",
    )

    db.session.add(invalid_risk_row_neither)
    with pytest.raises(IntegrityError):
        db.session.commit()
