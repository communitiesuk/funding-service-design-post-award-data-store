import logging
from datetime import datetime, timedelta
from unittest.mock import patch
from uuid import UUID

import pandas as pd
import pytest
from sqlalchemy import exc

from core.db import db
from core.db.entities import (
    Fund,
    GeospatialDim,
    Organisation,
    OutcomeData,
    OutcomeDim,
    Programme,
    ProgrammeJunction,
    Project,
    Submission,
)
from core.db.queries import (
    download_data_base_query,
    get_latest_submission_by_round_and_fund,
    get_programme_by_id_and_previous_round,
    get_programme_by_id_and_round,
    get_project_id_fk,
    outcome_data_query,
    project_query,
)
from core.db.utils import transaction_retry_wrapper


def outcome_data_structure_common_test(outcome_data_df):
    """Common test methods for testing structure of OutcomeData tables."""
    # event_blob, which is a dict, is not hashable, and so each of the keys are converted to columns
    outcome_data_df["unit_of_measurement"] = outcome_data_df["data_blob"].apply(
        lambda x: x.get("unit_of_measurement") if isinstance(x, dict) else None
    )
    outcome_data_df["geography_indicator"] = outcome_data_df["data_blob"].apply(
        lambda x: x.get("geography_indicator") if isinstance(x, dict) else None
    )
    outcome_data_df["amount"] = outcome_data_df["data_blob"].apply(
        lambda x: x.get("amount") if isinstance(x, dict) else None
    )
    outcome_data_df["state"] = outcome_data_df["data_blob"].apply(
        lambda x: x.get("state") if isinstance(x, dict) else None
    )
    outcome_data_df["higher_frequency"] = outcome_data_df["data_blob"].apply(
        lambda x: x.get("higher_frequency") if isinstance(x, dict) else None
    )
    outcome_data_df.drop(columns=["data_blob"], inplace=True)
    # check each outcome only occurs once (ie not duplicated)
    duplicates = outcome_data_df[outcome_data_df.duplicated()]
    assert len(duplicates) == 0

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

    test_query = download_data_base_query()
    test_query = test_query.with_entities(Programme.id).distinct()

    # assert all expected projects included
    test_query_projects = test_query.with_entities(
        Project.project_name,
    ).distinct()
    test_df = pd.read_sql(test_query_projects.statement, con=db.session.connection())

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
    test_query_out = outcome_data_query(test_query)
    test_df_out = pd.read_sql(test_query_out.statement, con=db.session.connection())

    outcome_data_structure_common_test(test_df_out)


def test_get_download_data_no_filters_date_range(seeded_test_client, additional_test_data):
    test_query = download_data_base_query()

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
        con=db.session.connection(),
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
        test_query.with_entities(Submission.id, Programme.id).distinct().statement, con=db.session.connection()
    )
    assert len(test_df_map) == 2  # should just be 2 rows if joined 1:1, no cartesian join.


def test_get_download_data_date_filters(seeded_test_client, additional_test_data):
    """Test date filter on base query."""

    submission = additional_test_data["submission"]

    # for assertion comparisons. Increase date range on filters to include all records
    max_rp_end = submission.reporting_period_end + timedelta(weeks=(52 * 2))
    test_query_all = download_data_base_query(min_rp_start=submission.reporting_period_start, max_rp_end=max_rp_end)
    test_query_all_subs = test_query_all.with_entities(
        Submission.id,
        Submission.reporting_period_start,
        Submission.reporting_period_end,
    ).distinct()

    test_all_df = pd.read_sql(test_query_all_subs.statement, con=db.session.connection())

    # all submission data should be within the specified reporting period range
    min_rp_start = submission.reporting_period_start - timedelta(days=1)
    max_rp_end = submission.reporting_period_end + timedelta(days=1)

    test_query_dates = download_data_base_query(min_rp_start=min_rp_start, max_rp_end=max_rp_end)
    test_query_dates_subs = test_query_dates.with_entities(
        Submission.id,
        Submission.submission_id,
        Submission.reporting_period_start,
        Submission.reporting_period_end,
    ).distinct()

    test_subs_df = pd.read_sql(test_query_dates_subs.statement, con=db.session.connection())

    assert len(test_subs_df) == 1
    assert test_subs_df.id[0] == submission.id

    # test query with larger date-range filters gets more rows
    assert len(test_all_df) > len(test_subs_df)


def test_get_download_data_end_date_filter(seeded_test_client, additional_test_data):
    """Test date filter with only end date parameter."""
    submission = additional_test_data["submission"]

    #  date range to include all records
    max_rp_end = submission.reporting_period_end + timedelta(weeks=(52 * 2))
    test_query_all = download_data_base_query(max_rp_end=max_rp_end)
    test_query_all_proj = project_query(test_query_all)

    test_all_results = test_query_all_proj.all()
    assert len(test_all_results) == 12

    #  using an earlier end date as the only param reduced the rows returned.
    test_query_reduced = download_data_base_query(max_rp_end=submission.reporting_period_end)
    test_query_reduced_proj = project_query(test_query_reduced)
    test_reduced_results = test_query_reduced_proj.all()
    assert len(test_reduced_results) == 4


def test_get_download_data_start_date_filter(seeded_test_client, additional_test_data):
    """Test date filter with only start date parameter."""

    submission = additional_test_data["submission"]

    #  date range to include all records
    test_query_all = download_data_base_query(min_rp_start=submission.reporting_period_start)
    test_query_all_proj = project_query(test_query_all)

    test_all_results = test_query_all_proj.all()
    assert len(test_all_results) == 12

    #  using a later start date as the only param reduced the rows returned.
    max_rp_end = submission.reporting_period_start + timedelta(weeks=(52 * 2))
    test_query_reduced = download_data_base_query(min_rp_start=max_rp_end)
    test_query_reduced_proj = project_query(test_query_reduced)
    test_reduced_results = test_query_reduced_proj.all()
    assert len(test_reduced_results) == 8


def test_get_download_data_organisation_filter(seeded_test_client, additional_test_data):
    """Pass organisation filter params and check rows"""
    organisation = additional_test_data["organisation"]
    organisation_uuids = [organisation.id]

    test_query_org = download_data_base_query(organisation_uuids=organisation_uuids)

    test_query_org_ents = test_query_org.with_entities(
        Submission.submission_id,
        Organisation.id,
        Organisation.organisation_name,
        Project.project_id,
        Programme.programme_id,
    ).distinct()

    test_query_org_all = (
        download_data_base_query()
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

    fund = additional_test_data["fund"]
    fund_type_ids = [fund.fund_code]

    test_query_fund_type = download_data_base_query(fund_type_ids=fund_type_ids)

    test_query_fund_ents = test_query_fund_type.with_entities(
        Submission.submission_id,
        Programme.programme_id,
        Fund.fund_code,
        Project.project_id,
    ).distinct()

    # basic check that query filter returns expected amount of rows
    test_fund_filtered = test_query_fund_ents.all()
    assert len(test_fund_filtered) == 4


def test_get_download_data_region_filter(seeded_test_client, additional_test_data):
    # when ITL region is passed, projects should be filtered by ITL region and any parent programmes with entirely
    # filtered out child projects should not be returned
    itl1_regions = [GeospatialDim.query.filter(GeospatialDim.postcode_prefix == "BS").one().itl1_region_code]
    test_query_region = download_data_base_query(itl1_regions=itl1_regions)

    test_query_region_ents = test_query_region.with_entities(
        Project.id,
        Project.project_id,
    ).distinct()

    test_fund_filtered_df = pd.read_sql(test_query_region_ents.statement, con=db.session.connection())

    project4 = additional_test_data["project4"]
    sw_projects = Project.query.filter(Project.id.in_(test_fund_filtered_df.id)).all()

    assert project4.id not in test_fund_filtered_df.id  # not in SW region
    # Asserting against index -1 as one seeded project has two geospatial associations, the first being for postcode BT
    assert all(itl1_regions[0] == project.geospatial_dims[-1].itl1_region_code for project in sw_projects)


def test_get_download_data_region_and_fund(seeded_test_client, additional_test_data):
    # when both ITL region and fund_type filter params are passed, return relevant results

    fund = additional_test_data["fund"]
    project4 = additional_test_data["project4"]
    itl1_regions = [GeospatialDim.query.filter(GeospatialDim.postcode_prefix == "BS").one().itl1_region_code]
    fund_type_ids = [fund.fund_code]

    test_query_region_fund = download_data_base_query(fund_type_ids=fund_type_ids, itl1_regions=itl1_regions)

    test_query_region_funds_ents = test_query_region_fund.with_entities(
        Project.id,
        Project.project_id,
        ProgrammeJunction.programme_id,
    ).distinct()

    test_region_fund_filtered_df = pd.read_sql(test_query_region_funds_ents.statement, con=db.session.connection())
    sw_projects = Project.query.filter(Project.id.in_(test_region_fund_filtered_df.id)).all()

    assert project4.id not in test_region_fund_filtered_df.id  # not in SW region
    assert all(
        programme.fund_type_id == programme.fund_type_id
        for programme in Programme.query.filter(Programme.id.in_(test_region_fund_filtered_df.programme_id))
    )
    # Asserting against index -1 as one seeded project has two geospatial associations, the first being for postcode BT
    assert all(itl1_regions[0] == project.geospatial_dims[-1].itl1_region_code for project in sw_projects)


def test_project_if_no_outcomes(seeded_test_client_rollback, additional_test_data):
    """
    Test that other tables still show up if no outcome data/outcome refs.

    This is testing the outer joins in the base_query (this tests a bugfix whereby no projects were returned if
    no Outcome data)
    """
    db.session.query(OutcomeData).delete()
    db.session.query(OutcomeDim).delete()
    test_query = download_data_base_query()
    test_query_proj = test_query.with_entities(Project.project_name).distinct()

    test_df = pd.read_sql(test_query_proj.statement, con=db.session.connection())
    assert list(test_df["project_name"])


def test_transaction_retry_wrapper_wrapper_max_retries(mocker, test_session, caplog):
    """
    Test the behavior of 'transaction_retry_wrapper' in case of IntegrityError.

    This test simulates a scenario where a function raises an IntegrityError
    and ensures that the 'transaction_retry_wrapper' wrapper retries the operation up to the
    specified maximum number of times. It also checks whether the error is properly
    logged after reaching the maximum number of retries.
    """
    max_retries = 5
    sleep_duration = 0.1
    error_type = exc.IntegrityError

    mocked_function = mocker.Mock(side_effect=exc.IntegrityError("Mocked IntegrityError", None, None))
    mocked_function.__name__ = "mocked_function"
    decorated_function = transaction_retry_wrapper(max_retries, sleep_duration, error_type)(mocked_function)

    with caplog.at_level(logging.ERROR) and patch("time.sleep") as patched_time_sleep:
        with pytest.raises(error_type):
            decorated_function()

    assert mocked_function.call_count == max_retries
    assert caplog.messages[-1] == "Number of max retries exceeded for function '{func_name}'"
    assert caplog.records[-1].func_name == "mocked_function"
    assert patched_time_sleep.call_count == 4


def test_transaction_retry_wrapper_wrapper_successful_retry(mocker, test_session, caplog):
    """
    Test the behavior of 'transaction_retry_wrapper' wrapper succeeding after failing once.
    """
    max_retries = 3
    sleep_duration = 0.1
    error_type = exc.IntegrityError

    mocked_function = mocker.Mock(
        side_effect=[
            exc.IntegrityError("Mocked IntegrityError", None, None),
            None,
            None,
        ]
    )
    mocked_function.__name__ = "mocked_function"
    decorated_function = transaction_retry_wrapper(max_retries, sleep_duration, error_type)(mocked_function)

    with caplog.at_level(logging.ERROR) and patch("time.sleep") as patched_time_sleep:
        decorated_function()

    assert mocked_function.call_count == 2
    assert "Retry count: {retry}" in caplog.messages[0]
    assert caplog.records[0].retry == 1
    assert patched_time_sleep.call_count == 1


def test_transaction_retry_wrapper_success_first_try(mocker, test_session, caplog):
    """
    Test the behavior of 'transaction_retry_wrapper' when the operation succeeds on the first try.
    It ensures that no error is logged in this case.
    """
    max_retries = 3
    sleep_duration = 0.1
    error_type = exc.IntegrityError

    mocked_function = mocker.Mock()
    mocked_function.__name__ = "mocked_function"
    decorated_function = transaction_retry_wrapper(max_retries, sleep_duration, error_type)(mocked_function)

    with caplog.at_level(logging.ERROR) and patch("time.sleep") as patched_time_sleep:
        decorated_function()

    assert mocked_function.call_count == 1
    assert not caplog.messages
    assert not patched_time_sleep.called


def test_get_programme_by_id_and_round(seeded_test_client, additional_test_data):
    programme = get_programme_by_id_and_round("FHSF001", 3)

    assert programme.programme_id == "FHSF001"
    assert len(programme.in_round_programmes[0].projects) == 8


def test_get_programme_by_id_and_previous_round(seeded_test_client, additional_test_data):
    programme = get_programme_by_id_and_previous_round("FHSF001", 4)

    assert programme.programme_id == "FHSF001"
    assert len(programme.in_round_programmes[0].projects) == 8


def test_get_project_id_fk(seeded_test_client, additional_test_data):
    project_id = get_project_id_fk("LUF0052", "97386631-d515-481b-8a79-46cc1317ea54")

    assert project_id == UUID("f3f3e2e2-0830-4ff0-9d8a-57463f45fc28")


def test_get_latest_submission_id_by_round_and_fund(seeded_test_client_rollback, additional_test_data):
    submission_2 = Submission(
        submission_id="S-R03-2",
        reporting_round=3,
        reporting_period_start=datetime(2019, 10, 10),
        reporting_period_end=datetime(2021, 10, 10),
    )

    programme_2 = Programme(
        programme_id="HS-ROW",
        programme_name="TEST-PROGRAMME-NAME",
        fund_type_id=Fund.query.first().id,
        organisation_id=Organisation.query.first().id,
    )

    db.session.add_all((submission_2, programme_2))
    db.session.flush()

    programme_junction_2 = ProgrammeJunction(
        programme_id=programme_2.id,
        submission_id=submission_2.id,
        reporting_round=submission_2.reporting_round,
    )

    db.session.add(programme_junction_2)
    db.session.flush()

    sub_tf = get_latest_submission_by_round_and_fund(3, "HS")

    assert sub_tf.submission_id == "S-R03-2"

    sub_pf = get_latest_submission_by_round_and_fund(3, "PF")

    assert sub_pf is None
