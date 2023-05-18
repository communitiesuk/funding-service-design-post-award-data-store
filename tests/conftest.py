import pytest

import tests.db_tests.resources.db_seed_data as db_seed
from app import create_app
from core.db import db
from core.db import entities as ents
from tests.util_test import seed_test_database


@pytest.fixture()
def flask_test_client():
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.
    :return: A flask test client.
    """
    with create_app().test_client() as test_client:
        yield test_client


@pytest.fixture
def app_ctx(flask_test_client):
    """
    Pushes an application context to a test.

    :return: a test application context.
    """
    with flask_test_client.application.app_context():
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture
def seeded_app_ctx(app_ctx):
    """
    Load seed data into test database.

    This is a fixture. Extends app_ctx.

    :return: a test application context.
    """

    seed_test_database(ents.Organisation, db_seed.ORGANISATION_DATA)
    seed_test_database(ents.Contact, db_seed.CONTACT_DATA)
    seed_test_database(ents.Package, db_seed.PACKAGE_DATA)
    seed_test_database(ents.Project, db_seed.PROJECT_DATA)
    seed_test_database(ents.ProjectDeliveryPlan, db_seed.PROJECT_DELIVERY_PLAN_DATA)
    seed_test_database(ents.Procurement, db_seed.PROCUREMENT_DATA)
    seed_test_database(ents.ProjectProgress, db_seed.PROJECT_PROGRESS_DATA)
    seed_test_database(ents.DirectFund, db_seed.DIRECT_FUND_DATA)
    seed_test_database(ents.Capital, db_seed.CAPITAL_DATA)
    seed_test_database(ents.IndirectFundSecured, db_seed.INDIRECT_FUND_SECURED_DATA)
    seed_test_database(ents.IndirectFundUnsecured, db_seed.INDIRECT_FUND_UNSECURED_DATA)
    seed_test_database(ents.OutputData, db_seed.OUTPUT_DATA)
    seed_test_database(ents.OutputDim, db_seed.OUTPUT_DIM)
    seed_test_database(ents.OutcomeData, db_seed.OUTCOME_DATA)
    seed_test_database(ents.OutcomeDim, db_seed.OUTCOME_DIM)
    seed_test_database(ents.RiskRegister, db_seed.RISK_REGISTER_DATA)

    db.session.commit()

    yield
