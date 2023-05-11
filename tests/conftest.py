import pytest

import tests.db_tests.resources.db_seed_data as db_seed
from app import create_app
from core.db.entities import *  # flake8: noqa
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

    # flake8: noqa
    seed_test_database(Organisation, db_seed.ORGANISATION_DATA)
    seed_test_database(Contact, db_seed.CONTACT_DATA)
    seed_test_database(Package, db_seed.PACKAGE_DATA)
    seed_test_database(Project, db_seed.PROJECT_DATA)
    seed_test_database(ProjectDeliveryPlan, db_seed.PROJECT_DELIVERY_PLAN_DATA)
    seed_test_database(Procurement, db_seed.PROCUREMENT_DATA)
    seed_test_database(ProjectProgress, db_seed.PROJECT_PROGRESS_DATA)
    seed_test_database(DirectFund, db_seed.DIRECT_FUND_DATA)
    seed_test_database(Capital, db_seed.CAPITAL_DATA)
    seed_test_database(IndirectFundSecured, db_seed.INDIRECT_FUND_SECURED_DATA)
    seed_test_database(IndirectFundUnsecured, db_seed.INDIRECT_FUND_UNSECURED_DATA)
    seed_test_database(OutputData, db_seed.OUTPUT_DATA)
    seed_test_database(OutputDim, db_seed.OUTPUT_DIM)
    seed_test_database(OutcomeData, db_seed.OUTCOME_DATA)
    seed_test_database(OutcomeDim, db_seed.OUTCOME_DIM)
    seed_test_database(RiskRegister, db_seed.RISK_REGISTER_DATA)

    db.session.commit()

    yield
