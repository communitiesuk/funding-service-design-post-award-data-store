"""Tests for sqla CheckConstraints table_args on model."""

from datetime import datetime

import pytest
from sqlalchemy.exc import IntegrityError

from core.db import db
from core.db.entities import (
    Funding,
    OutcomeData,
    OutcomeDim,
    OutputData,
    OutputDim,
    ProgrammeJunction,
    Project,
    RiskRegister,
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
