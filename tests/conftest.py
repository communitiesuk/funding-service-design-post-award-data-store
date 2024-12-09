"""
Package-wide fixtures including Flask app client and DB setup / teardown.

General guide to use:
Try to use the highest level scope possible for your use case, for the best performance. Be aware that session level
fixtures can interfere with the scope of other test modules, so if using this level, always check all the tests still
run concurrently.
The same applies to module scoped fixtures, these can interfere with other tests in the same module, if used
inappropriately.
For particularly disruptive or scope changing tests, the function scoped fixtures are designed to reset the DB, but
since these reset the DB at a function scope, they have the biggest impact on performance.
"""

import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, BinaryIO, Generator
from unittest import mock

import pandas as pd
import pytest
from flask.testing import FlaskClient
from mypy_boto3_s3.type_defs import ObjectIdentifierTypeDef
from sqlalchemy import text
from werkzeug.test import TestResponse

import config
from app import create_app
from config import Config
from config.envs.unit_test import UnitTestConfig
from data_store.aws import _S3_CLIENT
from data_store.const import GeographyIndicatorEnum, OrganisationTypeEnum
from data_store.db import db
from data_store.db.entities import (
    Fund,
    FundingQuestion,
    GeospatialDim,
    Organisation,
    OutcomeData,
    OutcomeDim,
    PlaceDetail,
    Programme,
    ProgrammeJunction,
    ProgrammeProgress,
    Project,
    ProjectFinanceChange,
    ReportingRound,
    RiskRegister,
    Submission,
)
from data_store.reference_data import seed_fund_table, seed_geospatial_dim_table, seed_reporting_round_table
from data_store.util import load_example_data
from submit.main.fund import TOWNS_FUND_APP_CONFIG
from tests.resources.pathfinders.pf_r1_extracted_data import get_pf_r1_extracted_data
from tests.resources.pathfinders.pf_r2_extracted_data import get_pf_r2_extracted_data


def pytest_addoption(parser):
    parser.addoption("--e2e", action="store_true", default=False, help="run e2e (browser) tests")

    # WARNING: Do not add an option for `prod` here. We *must* rework the e2e test authentication process before
    #          that would be something we could consider.
    parser.addoption(
        "--e2e-env",
        action="store",
        default="local",
        help="choose the environment that e2e tests will target",
        choices=("local", "dev", "test"),
    )

    parser.addoption(
        "--e2e-aws-vault-profile",
        action="store",
        help="the aws-vault profile matching the env set in --e2e-env (for `dev` or `test` only)",
    )

    parser.addoption(
        "--viewport",
        default="1920x1080",
        type=str,
        help="Change the viewport size of the browser window used for playwright tests (default: 1920x1080)",
    )


def pytest_collection_modifyitems(config, items):
    skip_e2e = pytest.mark.skip(reason="only running non-e2e tests")
    skip_non_e2e = pytest.mark.skip(reason="only running e2e tests")

    e2e_run = config.getoption("--e2e")
    if e2e_run:
        for item in items:
            if "e2e" not in item.keywords:
                item.add_marker(skip_non_e2e)
    else:
        for item in items:
            if "e2e" in item.keywords:
                item.add_marker(skip_e2e)


@pytest.fixture(scope="session")
def test_session() -> Generator[FlaskClient, None, None]:
    """
    Yield a test client with pushed application context and an empty DB.

    Tears down DB after use. Mainly intended as a package-wide test setup. Session scoped to remove overhead of
    building/tearing down DB tables repeatedly.

    Use as a base for fixtures that need application context / clean DB.

    Use for tests that
    - need application context
    - need empty DB
    - do not make uncommitted changes to DB
    - do not commit DB changes
    - do not cause errors in the flask client (Endpoint errors etc).
    - do not cause DB errors

    If DB is altered or tests deliberately cause errors or failures from endpoints, then one of the module or function
    scoped fixtures below, that specifically handle DB resets or rollbacks will be more appropriate.

    :yield: a flask test client with application context.
    """
    with create_app().test_client() as test_client:
        with test_client.application.app_context():
            db.create_all()
            yield test_client
            db.session.remove()
            db.drop_all()


@pytest.fixture(scope="module")
def test_client(test_session: FlaskClient) -> Generator[FlaskClient, None, None]:
    """
    Yield a test client with pushed application context and an empty DB.

    Resets DB to empty state after use, to prevent "test leakage" into other test modules.
    For use at module level scope. Inherits session scoped setup/tear-down.

    Use for tests that:
    - need application context
    - need empty DB
    - do not make uncommitted changes to DB
    - do not commit DB changes

    :param test_session: Flask test client with empty DB.
    :yield: a flask test client with application context.
    """

    yield test_session
    db.session.rollback()
    # disable foreign key checks
    db.session.execute(text("SET session_replication_role = replica"))
    # delete all data from data_store.table_extraction
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    # reset foreign key checks
    db.session.execute(text("SET session_replication_role = DEFAULT"))
    db.session.commit()
    db.session.remove()


@pytest.fixture(scope="function")
def test_client_rollback(test_client: FlaskClient) -> Generator[FlaskClient, None, None]:
    """
    Roll back any uncommitted database changes made in a test.

    This is a fixture. Extends test_client. Function scope to reset session
    (transaction) per test. Inherits module scoped setup/tear-down.

    Use for tests that:
    - need application context
    - need empty DB
    - make uncommitted changes to DB - THIS FIXTURE RESETS OPEN TRANSACTION AFTER EACH TEST.
    - do not commit DB changes

    :param test_client: Flask test client with empty DB.
    :yield: a flask test client with application context.
    """
    yield test_client
    db.session.rollback()


@pytest.fixture(scope="module")
def seeded_test_client(test_client: FlaskClient) -> Generator[FlaskClient, None, None]:
    """
    Yield a test client with pushed application context preloaded example data in test database.

    This test first seeds the 'fund_dim' and 'geospatial_dim' reference tables, and then calls
    load_example_data to load data into the other tables via csvs.
    This is a fixture. Extends test_client.

    Use for tests that:
    - need application context
    - need DB with preloaded test data
    - do not make uncommitted changes to DB
    - do not commit DB changes


    :param test_client: a Flask test client
    :yield: a flask test client with application context and seeded db.
    """
    seed_fund_table()
    seed_geospatial_dim_table()
    seed_reporting_round_table()
    load_example_data()
    yield test_client


@pytest.fixture(scope="function")
def seeded_test_client_rollback(seeded_test_client: FlaskClient) -> Generator[FlaskClient, None, None]:
    """Roll back any uncommitted database changes made in a test.

    This is a fixture. Extends seeded_test_client. Function scope to reset session
    (transaction) per test back to seeded db initial state (ie still with seeded data
    but disregarding uncommitted DB changes). Inherits module scoped setup/tear-down.

    Use for tests that:
    - need application context
    - need DB with preloaded test data
    - make uncommitted changes to DB
    - do not commit DB changes

    :param seeded_test_client: Flask test client with pre-populated DB.
    :yield: a flask test client with application context and seeded db.
    """
    yield seeded_test_client
    db.session.rollback()


@pytest.fixture(scope="function")
def test_client_reset(test_client: FlaskClient) -> Generator[FlaskClient, None, None]:
    """
    Returns a test client with pushed application context. Removes DB data at a function scope.

    Intended for use where a test involves a commit to DB.
    Seeds the fund_dim and geospatial_dim tables with pre-existing values, or else ingestion will not work.
    Empties existing DB tables after use, to prevent "test leakage" into other tests.
    For use at function level scope. Inherits module scoped setup/tear-down.
    Avoid using for tests that do not commit to DB, to avoid the extra overhead of setup/teardown once per function.
    The 'fund_dim' and 'geospatial_dim' tables are seeded at the beginning of each test as the application requires
    prior data for funds and geospatial reference data.

    Use for tests that:
    - need application context
    - need empty DB with preloaded Geospatial and Fund reference data
    - commit DB changes as part of their execution.

    :param test_client: Flask test client with empty DB.
    :yield: a flask test client with application context.
    """
    seed_fund_table()
    seed_geospatial_dim_table()
    seed_reporting_round_table()
    yield test_client
    db.session.rollback()
    # disable foreign key checks
    db.session.execute(text("SET session_replication_role = replica"))
    # delete all data from data_store.table_extraction
    for table in reversed(db.metadata.sorted_tables):
        db.session.execute(table.delete())
    # reset foreign key checks
    db.session.execute(text("SET session_replication_role = DEFAULT"))
    db.session.commit()
    db.session.remove()


@pytest.fixture(scope="module")
def additional_test_data() -> dict[str, Any]:
    """
    Add additional test data to DB (for specific use cases).

    Intended for use in conjunction with fixtures that handle DB setup/teardown.

    :return: dict of reference data objects added to DB (for comparison/assertion purposes)
    """
    fund = Fund(
        id=uuid.uuid4(),
        fund_code="TEST",
    )
    reporting_round = ReportingRound(
        fund_id=fund.id,
        round_number=1,
        observation_period_start=datetime(2019, 10, 10),
        observation_period_end=datetime(2021, 10, 10),
    )
    db.session.add(fund)
    db.session.add(reporting_round)
    db.session.flush()

    submission = Submission(
        submission_id="TEST-SUBMISSION-ID",
        reporting_round=reporting_round,
        submission_date=datetime(2024, 10, 1),
    )

    organisation = Organisation(organisation_name="TEST-ORGANISATION")
    organisation2 = Organisation(organisation_name="TEST-ORGANISATION2")
    db.session.add_all((submission, organisation, organisation2))
    db.session.flush()

    programme = Programme(
        programme_id="TEST-PROGRAMME-ID",
        programme_name="TEST-PROGRAMME-NAME",
        fund_type_id=fund.id,
        organisation_id=organisation.id,
    )

    db.session.add_all((programme,))
    db.session.flush()

    programme_junction = ProgrammeJunction(
        submission_id=submission.id,
        programme_id=programme.id,
        reporting_round_entity=reporting_round,
    )
    db.session.add(programme_junction)
    db.session.flush()

    geospatial_postcode_row = GeospatialDim.query.filter_by(postcode_prefix="BS").one()

    # Custom outcome, SW region
    project1 = Project(
        programme_junction_id=programme_junction.id,
        project_id="TEST-PROJECT-ID",
        project_name="TEST-PROJECT-NAME",
        data_blob={"primary_intervention_theme": "TEST-PIT", "locations": "TEST-LOCATIONS"},
        postcodes=["BS3 1AB"],  # real postcode area so we can test region filter works
    )
    project1.geospatial_dims.append(geospatial_postcode_row)

    # No outcomes, SW region
    project2 = Project(
        programme_junction_id=programme_junction.id,
        project_id="TEST-PROJECT-ID2",
        project_name="TEST-PROJECT-NAME2",
        data_blob={"primary_intervention_theme": "TEST-PIT2", "locations": "TEST-LOCATIONS2"},
        postcodes=["BS3 1AB"],  # real postcode area so we can test region filter works
    )
    project2.geospatial_dims.append(geospatial_postcode_row)

    # Transport outcome, SW region
    project3 = Project(
        programme_junction_id=programme_junction.id,
        project_id="TEST-PROJECT-ID3",
        project_name="TEST-PROJECT-NAME3",
        data_blob={"primary_intervention_theme": "TEST-PIT3", "locations": "TEST-LOCATIONS3"},
        postcodes=["BS3 1AB"],  # real postcode area so we can test region filter works
    )
    project3.geospatial_dims.append(geospatial_postcode_row)

    # Transport outcome, no region
    project4 = Project(
        programme_junction_id=programme_junction.id,
        project_id="TEST-PROJECT-ID4",
        project_name="TEST-PROJECT-NAME4",
        data_blob={"primary_intervention_theme": "TEST-PIT4", "locations": "TEST-LOCATIONS4"},
        postcodes=[],  # no postcode == no region
    )

    db.session.add_all((project1, project2, project3, project4))
    db.session.flush()

    test_outcome_dim = OutcomeDim(outcome_name="TEST-OUTCOME-1", outcome_category="TEST-OUTCOME-CATEGORY")
    transport_outcome_dim = OutcomeDim(outcome_name="TEST-OUTCOME-2", outcome_category="Transport")
    db.session.add_all((test_outcome_dim, transport_outcome_dim))
    db.session.flush()

    project_outcome1 = OutcomeData(
        project_id=project1.id,  # linked to project1
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

    project_outcome2 = OutcomeData(
        project_id=project3.id,  # linked to project3
        outcome_id=transport_outcome_dim.id,  # linked to Transport OutcomeDim
        start_date=datetime(2021, 1, 1),
        end_date=datetime(2022, 12, 31),
        data_blob={
            "unit_of_measurement": "Units",
            "geography_indicator": GeographyIndicatorEnum.TRAVEL_CORRIDOR,
            "amount": 100.0,
            "state": "Actual",
            "higher_frequency": None,
        },
    )

    programme_outcome = OutcomeData(
        programme_junction_id=programme_junction.id,
        outcome_id=test_outcome_dim.id,  # linked to Transport OutcomeDim
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31),
        data_blob={
            "unit_of_measurement": "Units",
            "geography_indicator": GeographyIndicatorEnum.TOWN,
            "amount": 26.0,
            "state": "Actual",
            "higher_frequency": None,
        },
    )

    # the following entities are all for a previous funding round (testing joins)
    funding_question = FundingQuestion(
        programme_junction_id=programme_junction.id,
        data_blob={
            "question": "Some Question",
            "indicator": "You shouldn't see this",
            "response": "test response",
            "guidance_notes": "test notes",
        },
    )
    prog_risk = RiskRegister(
        programme_junction_id=programme_junction.id,
        project_id=None,
        data_blob={"risk_name": "Test RISK", "risk_category": "Test CAT"},
    )
    programme_progress = ProgrammeProgress(
        programme_junction_id=programme_junction.id,
        data_blob={"question": "test QUESTION", "answer": "test ANSWER"},
    )
    place_detail = PlaceDetail(
        programme_junction_id=programme_junction.id,
        data_blob={"question": "test QUESTION", "answer": "test ANSWER", "indicator": "test INDICATOR"},
    )
    outcome_programme = OutcomeData(
        programme_junction_id=programme_junction.id,
        project_id=None,
        outcome_id=test_outcome_dim.id,  # linked to TEST-OUTCOME-CATEGORY OutcomeDim
        start_date=datetime(2024, 1, 1),
        end_date=datetime(2024, 12, 31),
        data_blob={
            "unit_of_measurement": "TEST Units",
        },
    )
    project_finance_change = ProjectFinanceChange(
        programme_junction_id=programme_junction.id,
        data_blob={
            "change_number": 1,
            "project_funding_moved_from": "blah",
            "intervention_theme_moved_from": "blah",
            "project_funding_moved_to": "blah",
            "intervention_theme_moved_to": "blah",
            "amount_moved": 10,
            "changes_made": "blah",
            "reasons_for_change": "blah",
            "forecast_or_actual_change": "blah",
            "reporting_period_change_takes_place": "blah",
        },
    )

    db.session.add_all(
        (
            project_outcome1,
            project_outcome2,
            programme_outcome,
            funding_question,
            prog_risk,
            programme_progress,
            place_detail,
            outcome_programme,
            project_finance_change,
        )
    )
    db.session.commit()

    return {
        "organisation": organisation,
        "submission": submission,
        "fund": fund,
        "reporting_round": reporting_round,
        "programme": programme,
        "project1": project1,
        "project2": project2,
        "project3": project3,
        "project4": project4,
        "test_outcome_dim": test_outcome_dim,
        "transport_outcome_dim": transport_outcome_dim,
        "funding_question": funding_question,
        "prog_risk": prog_risk,
        "programme_progress": programme_progress,
        "place_detail": place_detail,
        "outcome_programme": outcome_programme,
        "project_finance_change": project_finance_change,
    }


@pytest.fixture(scope="function")
def towns_fund_bolton_round_1_test_data(test_client_reset):
    """
    Add additional test data to DB (for specific use cases).

    Intended for use in conjunction with 'pathfinders_round_1_file_success' to ensure that
    there is no conflict between programmes with the same name in the same round for different
    funds.
    """
    fund = Fund.query.filter_by(fund_code="TD").one()
    rr1 = ReportingRound.query.filter_by(fund_id=fund.id, round_number=1).one()
    submission = Submission(
        submission_id="S-R01-1",
        reporting_round=rr1,
        submission_date=datetime(2024, 10, 1),
    )

    organisation = Organisation(organisation_name="Bolton Council")
    db.session.add_all((submission, organisation))
    db.session.flush()

    programme = Programme(
        programme_id="TD-BOL",
        programme_name="Bolton Council",
        fund_type_id=Fund.query.filter_by(fund_code="TD").first().id,
        organisation_id=organisation.id,
    )

    db.session.add(programme)
    db.session.flush()

    programme_junction = ProgrammeJunction(
        submission_id=submission.id,
        programme_id=programme.id,
        reporting_round_entity=rr1,
    )
    db.session.add(programme_junction)
    db.session.commit()


@pytest.fixture(scope="function")
def pathfinders_round_1_submission_data(test_client_reset):
    """Pre-populates Submission table with an already existing PF submission."""
    fund = Fund.query.filter_by(fund_code="PF").one()
    rr1 = ReportingRound.query.filter_by(fund_id=fund.id, round_number=1).one()
    submission = Submission(
        submission_id="S-PF-R01-1",
        reporting_round=rr1,
        submission_date=datetime(2024, 10, 1),
    )

    organisation = Organisation(organisation_name="Romulus")
    db.session.add_all((submission, organisation))
    db.session.flush()

    programme = Programme(
        programme_id="PF-ROM",
        programme_name="Romulan Star Empire",
        fund_type_id=Fund.query.filter_by(fund_code="PF").first().id,
        organisation_id=organisation.id,
    )

    db.session.add(programme)
    db.session.flush()

    programme_junction = ProgrammeJunction(
        submission_id=submission.id,
        programme_id=programme.id,
        reporting_round_entity=rr1,
    )
    db.session.add(programme_junction)
    db.session.commit()


@pytest.fixture(scope="function")
def towns_fund_td_round_3_submission_data(test_client_reset):
    """Pre-populates Submission table with an already existing TD submission."""
    fund = Fund.query.filter_by(fund_code="TD").one()
    rr3 = ReportingRound.query.filter_by(fund_id=fund.id, round_number=3).one()
    submission = Submission(
        submission_id="S-R03-1",
        reporting_round=rr3,
        submission_date=datetime(2024, 10, 1),
    )

    organisation = Organisation(organisation_name="Romulus")
    db.session.add_all((submission, organisation))
    db.session.flush()

    programme = Programme(
        programme_id="TD-ROM",
        programme_name="Romulan Star Empire",
        fund_type_id=Fund.query.filter_by(fund_code="TD").first().id,
        organisation_id=organisation.id,
    )

    db.session.add(programme)
    db.session.flush()

    programme_junction = ProgrammeJunction(
        submission_id=submission.id,
        programme_id=programme.id,
        reporting_round_entity=rr3,
    )
    db.session.add(programme_junction)
    db.session.commit()


@pytest.fixture(scope="function")
def mock_pf_r1_df_dict() -> dict[str, pd.DataFrame]:
    return get_pf_r1_extracted_data()


@pytest.fixture(scope="function")
def mock_pf_r2_df_dict() -> dict[str, pd.DataFrame]:
    return get_pf_r2_extracted_data()


@pytest.fixture(scope="function")
def mock_sentry_metrics():
    with mock.patch("data_store.metrics.sentry_sdk.metrics") as mock_sentry_metrics:
        yield mock_sentry_metrics


@pytest.fixture(scope="function")
def mocked_auth(mocker):
    # mock authorised user
    mocker.patch(
        "fsd_utils.authentication.decorators._check_access_token",
        return_value={
            "accountId": "test-user",
            "roles": [TOWNS_FUND_APP_CONFIG.user_role],
            "email": "user@wigan.gov.uk",
        },
    )


@pytest.fixture(scope="function")
def mocked_pf_auth(mocker):
    # mock authorised user with Pathfinders role
    mocker.patch(
        "fsd_utils.authentication.decorators._check_access_token",
        return_value={
            "accountId": "pf-test-user",
            "roles": ["PF_MONITORING_RETURN_SUBMITTER"],
            "email": "pf-user@wigan.gov.uk",
        },
    )


@pytest.fixture(scope="function")
def mocked_pf_and_tf_auth(mocker):
    # mock authorised user with Pathfinders role
    mocker.patch(
        "fsd_utils.authentication.decorators._check_access_token",
        return_value={
            "accountId": "pf-tf-test-user",
            "roles": ["PF_MONITORING_RETURN_SUBMITTER", "TF_MONITORING_RETURN_SUBMITTER"],
            "email": "test-user@wigan.gov.uk",
        },
    )


@pytest.fixture(scope="function")
def mocked_find_auth(mocker):
    # mock authorised user for Find
    mocker.patch(
        "fsd_utils.authentication.decorators._check_access_token",
        return_value={
            "accountId": "test-user",
            "roles": [],
            "email": "test-user@communities.gov.uk",
        },
    )


@pytest.fixture(scope="function")
def mocked_admin_user(mocker):
    mocker.patch(
        "fsd_utils.authentication.decorators._check_access_token",
        return_value={
            "accountId": "test-user",
            "roles": ["FSD_ADMIN"],
            "email": "admin@communities.gov.uk",
        },
    )


class _SubmitFlaskClient(FlaskClient):
    def open(
        self,
        *args: Any,
        buffered: bool = False,
        follow_redirects: bool = False,
        **kwargs: Any,
    ) -> TestResponse:
        if "headers" in kwargs:
            kwargs["headers"].setdefault("Host", UnitTestConfig.SUBMIT_HOST)
        else:
            kwargs.setdefault("headers", {"Host": UnitTestConfig.SUBMIT_HOST})
        return super().open(*args, buffered=buffered, follow_redirects=follow_redirects, **kwargs)


@pytest.fixture(scope="function")
def submit_test_client(mocked_auth) -> Generator[FlaskClient, None, None]:
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.

    NOTE: Auth is mocked here because it's required for all routes.

    :return: A flask test client.
    """
    app = create_app(config.Config)
    app.test_client_class = _SubmitFlaskClient
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(scope="function")
def unauthenticated_submit_test_client() -> Generator[FlaskClient, None, None]:
    """
    :return: An unauthenticated flask test client.
    """
    app = create_app(config.Config)
    app.test_client_class = _SubmitFlaskClient
    with app.test_client() as test_client:
        yield test_client


class _FindFlaskClient(FlaskClient):
    def open(
        self,
        *args: Any,
        buffered: bool = False,
        follow_redirects: bool = False,
        **kwargs: Any,
    ) -> TestResponse:
        if "headers" in kwargs:
            kwargs["headers"].setdefault("Host", UnitTestConfig.FIND_HOST)
        else:
            kwargs.setdefault("headers", {"Host": UnitTestConfig.FIND_HOST})
        return super().open(*args, buffered=buffered, follow_redirects=follow_redirects, **kwargs)


@pytest.fixture(scope="function")
def find_test_client(mocked_find_auth) -> Generator[FlaskClient, None, None]:
    """
    Creates the test client we will be using to test the responses
    from our app, this is a test fixture.

    NOTE: Auth is mocked here because it's required for all routes.

    :return: A flask test client.
    """
    app = create_app(config.Config)
    app.test_client_class = _FindFlaskClient
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(scope="function")
def admin_test_client(mocked_admin_user) -> Generator[FlaskClient, None, None]:
    app = create_app(config.Config)
    app.test_client_class = _FindFlaskClient
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(scope="function")
def unauthenticated_find_test_client() -> Generator[FlaskClient, None, None]:
    """
    :return: An unauthenticated flask test client.
    """
    app = create_app(config.Config)
    app.test_client_class = _FindFlaskClient
    with app.test_client() as test_client:
        yield test_client


@pytest.fixture(scope="function")
def non_internal_user_find_test_client(mocked_pf_auth) -> Generator[FlaskClient, None, None]:
    """
    :return: A flask test client authenticated for an external user
    ie. without @communities.gov.uk or @test-communities.gov.uk email.
    """
    app = create_app(config.Config)
    app.test_client_class = _FindFlaskClient
    with app.test_client() as test_client:
        yield test_client


def create_bucket(bucket: str):
    """Helper function that creates a specified bucket if it doesn't already exist."""
    if bucket not in {bucket_obj["Name"] for bucket_obj in _S3_CLIENT.list_buckets()["Buckets"]}:
        _S3_CLIENT.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "eu-central-1"})


def delete_bucket(bucket: str):
    """Helper function that deletes all objects in a specified bucket and then deletes the bucket."""
    s3_objects_response = _S3_CLIENT.list_objects_v2(Bucket=bucket)
    if "Contents" in s3_objects_response:
        s3_objects: list[ObjectIdentifierTypeDef] = [{"Key": obj["Key"]} for obj in s3_objects_response["Contents"]]
        _S3_CLIENT.delete_objects(Bucket=bucket, Delete={"Objects": s3_objects})
    _S3_CLIENT.delete_bucket(Bucket=bucket)


@pytest.fixture(scope="module")
def test_buckets():
    """Sets up and tears down buckets used by this module.
    On set up:
    - creates data-store-failed-files-unit-tests
    - creates data-store-successful-files-unit-tests
    - creates data-store-find-download-files-unit-tests

    On tear down, deletes all objects stored in the buckets and then the buckets themselves.
    """
    create_bucket(Config.AWS_S3_BUCKET_FAILED_FILES)
    create_bucket(Config.AWS_S3_BUCKET_SUCCESSFUL_FILES)
    create_bucket(Config.AWS_S3_BUCKET_FIND_DOWNLOAD_FILES)
    yield
    delete_bucket(Config.AWS_S3_BUCKET_FAILED_FILES)
    delete_bucket(Config.AWS_S3_BUCKET_SUCCESSFUL_FILES)
    delete_bucket(Config.AWS_S3_BUCKET_FIND_DOWNLOAD_FILES)


@pytest.fixture()
def pathfinders_round_1_file_success() -> Generator[BinaryIO, None, None]:
    """An example spreadsheet for reporting round 1 of Pathfinders that should ingest without validation errors."""
    with open(
        Path(__file__).parent / "integration_tests" / "mock_pf_returns" / "PF_Round_1_Success.xlsx", "rb"
    ) as file:
        yield file


@pytest.fixture()
def pathfinders_round_2_file_success() -> Generator[BinaryIO, None, None]:
    """An example spreadsheet for reporting round 2 of Pathfinders that should ingest without validation errors."""
    with open(
        Path(__file__).parent / "integration_tests" / "mock_pf_returns" / "PF_Round_2_Success.xlsx", "rb"
    ) as file:
        yield file


@pytest.fixture(scope="session")
def towns_fund_round_3_success_file_path():
    """Filepath to an example spreadsheet for Towns Fund Round 3 that should ingest without validation errors."""
    filepath = Path(__file__).parent / "integration_tests" / "mock_tf_returns" / "TF_Round_3_Success.xlsx"
    yield filepath


@pytest.fixture(scope="function")
def towns_fund_round_3_file_success(towns_fund_round_3_success_file_path) -> Generator[BinaryIO, None, None]:
    """An example spreadsheet for reporting round 3 of Towns Fund that should ingest without validation errors."""
    with open(towns_fund_round_3_success_file_path, "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_file_success() -> Generator[BinaryIO, None, None]:
    """An example spreadsheet for reporting round 4 of Towns Fund that should ingest without validation errors."""
    with open(
        Path(__file__).parent / "integration_tests" / "mock_tf_returns" / "TF_Round_4_Success.xlsx", "rb"
    ) as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_6_file_success() -> Generator[BinaryIO, None, None]:
    """An example spreadsheet for reporting round 6 of Towns Fund that should ingest without validation errors."""
    with open(
        Path(__file__).parent / "integration_tests" / "mock_tf_returns" / "TF_Round_6_Success.xlsx", "rb"
    ) as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_6_file_failure() -> Generator[BinaryIO, None, None]:
    """An example spreadsheet for reporting round 6 of Towns Fund that should ingest with validation errors."""
    with open(
        Path(__file__).parent / "integration_tests" / "mock_tf_returns" / "TF_Round_6_General_Validation_Failures.xlsx",
        "rb",
    ) as file:
        yield file


@pytest.fixture
def test_organisation(test_session):
    org = Organisation(
        organisation_name="Original Name",
        external_reference_code="Original Code",
        organisation_type=OrganisationTypeEnum.LOCAL_AUTHORITY,
    )
    db.session.add(org)
    db.session.commit()

    return org
