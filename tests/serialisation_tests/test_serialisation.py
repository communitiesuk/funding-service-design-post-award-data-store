import datetime

import numpy as np
import pandas as pd

from core.const import ITLRegion
from core.db import db
from core.db.entities import (
    Organisation,
    OutcomeData,
    OutcomeDim,
    Project,
    RiskRegister,
    Submission,
)
from core.db.queries import download_data_base_query, query_extend_with_outcome_filter
from core.serialisation.data_serialiser import serialise_download_data


def test_serialise_download_data_specific_tab(seeded_test_client, additional_test_data):
    """Test that serialiser func doesn't return all "sheets" of data if "sheets_required" passed as param."""
    base_query = download_data_base_query()
    test_generator = serialise_download_data(base_query, outcome_categories=None, sheets_required=["ProgrammeRef"])
    test_serialised_data = {sheet: data for sheet, data in test_generator}

    assert test_serialised_data.keys() == {"ProgrammeRef"}


def test_serialise_datetimes(seeded_test_client, additional_test_data):
    """Check that dates are exported as datetime/date objects instead of plain strings"""
    base_query = download_data_base_query()
    test_generator = serialise_download_data(base_query, outcome_categories=None, sheets_required=["Funding"])
    serialised_data = {sheet: data for sheet, data in test_generator}

    df_output_data = pd.DataFrame.from_records(serialised_data["Funding"])

    assert isinstance(df_output_data["StartDate"].dropna().unique()[0], np.datetime64)
    assert isinstance(df_output_data["EndDate"].dropna().unique()[0], np.datetime64)


def test_serialise_download_data_no_filters(seeded_test_client, additional_test_data):
    base_query = download_data_base_query()
    test_serialised_data = {
        sheet: data
        for sheet, data in serialise_download_data(base_query, outcome_categories=None, sheets_required=None)
    }

    # non-data-specific assertions to check parts of the extract are populated
    assert test_serialised_data.get("PlaceDetails")
    assert test_serialised_data.get("ProjectDetails")
    assert test_serialised_data.get("OrganisationRef")
    assert test_serialised_data.get("ProgrammeRef")
    assert test_serialised_data.get("ProgrammeProgress")
    assert test_serialised_data.get("ProjectProgress")
    assert test_serialised_data.get("FundingQuestions")
    assert test_serialised_data.get("Funding")
    assert test_serialised_data.get("FundingComments")
    assert test_serialised_data.get("PrivateInvestments")
    assert test_serialised_data.get("OutputRef")
    assert test_serialised_data.get("OutputData")
    assert test_serialised_data.get("OutcomeRef")
    assert test_serialised_data.get("OutcomeData")
    assert test_serialised_data.get("RiskRegister")
    assert test_serialised_data.get("ProjectFinanceChange")
    assert test_serialised_data.get("SubmissionRef")
    assert test_serialised_data.get("ProgrammeManagementFunding")
    assert len(test_serialised_data) == 18

    # assert all tables contain place and organisation (apart from OrgRef, OutputRef, SubmissionRef and OutcomeRef)
    for section_name, data in test_serialised_data.items():
        if section_name in ["ProgrammeRef", "OrganisationRef", "OutputRef", "OutcomeRef", "SubmissionRef"]:
            continue
        assert "Place" in data[0].keys()
        assert "OrganisationName" in data[0].keys()

    # assert correct number of column headers in each serialised table
    assert list(pd.DataFrame.from_records(test_serialised_data["PlaceDetails"]).columns) == [
        "OrganisationName",
        "SubmissionID",
        "ProgrammeID",
        "Question",
        "Indicator",
        "Answer",
        "Place",
    ]
    assert len(test_serialised_data["PlaceDetails"]) == 16
    assert list(pd.DataFrame.from_records(test_serialised_data["ProjectDetails"]).columns) == [
        "SubmissionID",
        "ProjectID",
        "PrimaryInterventionTheme",
        "SingleorMultipleLocations",
        "Locations",
        "AreYouProvidingAGISMapWithYourReturn",
        "LatLongCoordinates",
        "ExtractedPostcodes",
        "ProjectName",
        "Place",
        "OrganisationName",
    ]
    assert len(test_serialised_data["ProjectDetails"]) == 12
    assert list(pd.DataFrame.from_records(test_serialised_data["OrganisationRef"]).columns) == [
        "OrganisationName",
        "Geography",
    ]
    assert len(test_serialised_data["OrganisationRef"]) == 2
    assert list(pd.DataFrame.from_records(test_serialised_data["ProgrammeRef"]).columns) == [
        "ProgrammeID",
        "ProgrammeName",
        "FundTypeID",
        "OrganisationName",
    ]
    assert len(test_serialised_data["ProgrammeRef"]) == 2
    assert list(pd.DataFrame.from_records(test_serialised_data["ProgrammeProgress"]).columns) == [
        "SubmissionID",
        "ProgrammeID",
        "Question",
        "Answer",
        "Place",
        "OrganisationName",
    ]
    assert len(test_serialised_data["ProgrammeProgress"]) == 8
    assert list(pd.DataFrame.from_records(test_serialised_data["ProjectProgress"]).columns) == [
        "SubmissionID",
        "ProjectID",
        "StartDate",
        "CompletionDate",
        "ProjectAdjustmentRequestStatus",
        "ProjectDeliveryStatus",
        "LeadingFactorOfDelay",
        "CurrentProjectDeliveryStage",
        "Delivery(RAG)",
        "Spend(RAG)",
        "Risk(RAG)",
        "CommentaryonStatusandRAGRatings",
        "MostImportantUpcomingCommsMilestone",
        "DateofMostImportantUpcomingCommsMilestone",
        "ProjectName",
        "Place",
        "OrganisationName",
    ]
    assert len(test_serialised_data["ProjectProgress"]) == 3
    assert list(pd.DataFrame.from_records(test_serialised_data["FundingQuestions"]).columns) == [
        "SubmissionID",
        "ProgrammeID",
        "Question",
        "Indicator",
        "Answer",
        "GuidanceNotes",
        "Place",
        "OrganisationName",
    ]
    assert len(test_serialised_data["FundingQuestions"]) == 17
    assert list(pd.DataFrame.from_records(test_serialised_data["Funding"]).columns) == [
        "SubmissionID",
        "ProgrammeID",
        "ProjectID",
        "FundingSourceName",
        "FundingSourceType",
        "Secured",
        "StartDate",
        "EndDate",
        "SpendforReportingPeriod",
        "ActualOrForecast",
        "ProjectName",
        "Place",
        "OrganisationName",
    ]
    assert len(test_serialised_data["Funding"]) == 14
    assert list(pd.DataFrame.from_records(test_serialised_data["FundingComments"]).columns) == [
        "SubmissionID",
        "ProjectID",
        "Comment",
        "ProjectName",
        "Place",
        "OrganisationName",
    ]
    assert len(test_serialised_data["FundingComments"]) == 8
    assert list(pd.DataFrame.from_records(test_serialised_data["PrivateInvestments"]).columns) == [
        "SubmissionID",
        "ProjectID",
        "TotalProjectValue",
        "TownsfundFunding",
        "PrivateSectorFundingRequired",
        "PrivateSectorFundingSecured",
        "PSIAdditionalComments",
        "ProjectName",
        "Place",
        "OrganisationName",
    ]
    assert len(test_serialised_data["PrivateInvestments"]) == 8
    assert list(pd.DataFrame.from_records(test_serialised_data["OutputRef"]).columns) == [
        "OutputName",
        "OutputCategory",
    ]
    assert len(test_serialised_data["OutputRef"]) == 2
    assert list(pd.DataFrame.from_records(test_serialised_data["OutputData"]).columns) == [
        "SubmissionID",
        "ProgrammeID",
        "ProjectID",
        "FinancialPeriodStart",
        "FinancialPeriodEnd",
        "Output",
        "UnitofMeasurement",
        "ActualOrForecast",
        "Amount",
        "AdditionalInformation",
        "ProjectName",
        "Place",
        "OrganisationName",
    ]
    assert len(test_serialised_data["OutputData"]) == 44
    assert list(pd.DataFrame.from_records(test_serialised_data["OutcomeRef"]).columns) == [
        "OutcomeName",
        "OutcomeCategory",
    ]
    assert len(test_serialised_data["OutcomeRef"]) == 4
    assert list(pd.DataFrame.from_records(test_serialised_data["OutcomeData"]).columns) == [
        "SubmissionID",
        "ProgrammeID",
        "ProjectID",
        "StartDate",
        "EndDate",
        "Outcome",
        "UnitofMeasurement",
        "GeographyIndicator",
        "Amount",
        "ActualOrForecast",
        "SpecifyIfYouAreAbleToProvideThisMetricAtAHigherFrequencyLevelThanAnnually",
        "ProjectName",
        "Place",
        "OrganisationName",
    ]
    assert len(test_serialised_data["OutcomeData"]) == 30
    assert list(pd.DataFrame.from_records(test_serialised_data["RiskRegister"]).columns) == [
        "SubmissionID",
        "ProgrammeID",
        "ProjectID",
        "RiskName",
        "RiskCategory",
        "ShortDescription",
        "FullDescription",
        "Consequences",
        "PreMitigatedImpact",
        "PreMitigatedLikelihood",
        "Mitigations",
        "PostMitigatedImpact",
        "PostMitigatedLikelihood",
        "Proximity",
        "RiskOwnerRole",
        "ProjectName",
        "Place",
        "OrganisationName",
    ]
    assert len(test_serialised_data["RiskRegister"]) == 28
    assert list(pd.DataFrame.from_records(test_serialised_data["ProjectFinanceChange"]).columns) == [
        "SubmissionID",
        "ProgrammeID",
        "ChangeNumber",
        "ProjectFundingMovedFrom",
        "InterventionThemeMovedFrom",
        "ProjectFundingMovedTo",
        "InterventionThemeMovedTo",
        "AmountMoved",
        "ChangesMade",
        "ReasonsForChange",
        "ForecastOrActualChange",
        "ReportingPeriodChangeTakesPlace",
        "Place",
        "OrganisationName",
    ]
    assert len(test_serialised_data["ProjectFinanceChange"]) == 1
    assert list(pd.DataFrame.from_records(test_serialised_data["SubmissionRef"]).columns) == [
        "SubmissionID",
        "ProgrammeID",
        "ReportingPeriodStart",
        "ReportingPeriodEnd",
        "ReportingRound",
    ]
    assert list(pd.DataFrame.from_records(test_serialised_data["ProgrammeManagementFunding"]).columns) == [
        "SubmissionID",
        "ProgrammeID",
        "PaymentType",
        "SpendForReportingPeriod",
        "ActualOrForecast",
        "StartDate",
        "EndDate",
        "Place",
        "OrganisationName",
    ]
    assert len(test_serialised_data["ProgrammeManagementFunding"]) == 24

    # check a couple of tables that all results are returned
    assert len(test_serialised_data["SubmissionRef"]) == len(Submission.query.all()) == 2
    assert len(test_serialised_data["RiskRegister"]) == len(RiskRegister.query.all()) == 28
    assert len(test_serialised_data["ProjectDetails"]) == len(Project.query.all()) == 12


def test_serialise_download_data_organisation_filter(seeded_test_client, additional_test_data):
    """Assert filter applied reduces results returned."""
    organisation = additional_test_data["organisation"]
    organisation_uuids = [organisation.id]
    test_query_org = download_data_base_query(organisation_uuids=organisation_uuids)
    test_serialised_data = {
        sheet: data
        for sheet, data in serialise_download_data(test_query_org, outcome_categories=None, sheets_required=None)
    }

    assert len(test_serialised_data["OrganisationRef"]) == 1
    assert len(test_serialised_data["OrganisationRef"]) < len(Organisation.query.all())

    assert len(test_serialised_data["ProjectDetails"]) == 4
    assert len(test_serialised_data["ProjectDetails"]) < len(Project.query.all())


def test_serialise_data_region_filter(seeded_test_client, additional_test_data):
    """
    when ITL region is passed, projects should be filtered by ITL region and any parent programmes with entirely
    filtered out child projects should not be returned.
    """
    itl_regions = {ITLRegion.SouthWest}
    test_query_region = download_data_base_query(itl_regions=itl_regions)

    test_serialised_data = {
        sheet: data
        for sheet, data in serialise_download_data(test_query_region, outcome_categories=None, sheets_required=None)
    }
    #  read into pandas for ease of inspection
    test_fund_filtered_df = pd.DataFrame.from_records(test_serialised_data["ProjectDetails"])

    project4 = additional_test_data["project4"]
    assert project4.project_id not in test_fund_filtered_df["ProjectID"]  # not in SW region
    assert all(
        ITLRegion.SouthWest in project.itl_regions
        for project in Project.query.filter(Project.project_id.in_(test_fund_filtered_df["ProjectID"]))
    )


def test_serialise_postcode(seeded_test_client, additional_test_data):
    base_query = download_data_base_query()
    test_serialised_data = {
        sheet: data for sheet, data in serialise_download_data(base_query, sheets_required=["ProjectDetails"])
    }

    postcodes_results = {x["ExtractedPostcodes"] for x in test_serialised_data["ProjectDetails"]}
    assert "BS3 1AB" in postcodes_results  # check single postcodes
    assert "SW1A 2AA, BT1 1AA" in postcodes_results  # check multiple postcodes found
    assert "" in postcodes_results  # check no postcodes found
    assert len(postcodes_results) == 4  # consistency check


def test_serialise_submission_metadata(seeded_test_client, additional_test_data):
    base_query = download_data_base_query()
    test_serialised_data = {
        sheet: data for sheet, data in serialise_download_data(base_query, sheets_required=["SubmissionRef"])
    }

    assert len(test_serialised_data["SubmissionRef"]) == 2

    assert {
        "SubmissionID": "S-R03-1",
        "ProgrammeID": "FHSF001",
        "ReportingPeriodStart": datetime.datetime(2023, 2, 1, 0, 0),
        "ReportingPeriodEnd": datetime.datetime(2023, 2, 12, 0, 0),
        "ReportingRound": 3,
    } in test_serialised_data["SubmissionRef"]

    assert {
        "SubmissionID": "TEST-SUBMISSION-ID",
        "ProgrammeID": "TEST-PROGRAMME-ID",
        "ReportingPeriodStart": datetime.datetime(2019, 10, 10, 0, 0),
        "ReportingPeriodEnd": datetime.datetime(2021, 10, 10, 0, 0),
        "ReportingRound": 1,
    } in test_serialised_data["SubmissionRef"]


def test_outcomes_table_empty(seeded_test_client_rollback, additional_test_data):
    """
    Test that OutcomeData query actually returns empty if DB table is empty

    Specifically testing the behaviour of the conditional expressions in outcome_data_query(), combined with
    conditional join to OutcomeData
    """
    db.session.query(OutcomeData).delete()
    db.session.query(OutcomeDim).delete()
    test_query = download_data_base_query()

    test_serialiser = serialise_download_data(
        test_query, outcome_categories=None, sheets_required=["OutcomeData", "OutcomeRef"]
    )
    test_data = {sheet: data for sheet, data in test_serialiser}
    test_df_outcome_data = pd.DataFrame.from_records(test_data["OutcomeData"]).dropna(how="all")

    assert len(test_df_outcome_data) == 0

    test_df_outcome_ref = pd.DataFrame.from_records(test_data["OutcomeData"]).dropna(how="all")
    assert len(test_df_outcome_ref) == 0


def test_risks_table_empty(seeded_test_client_rollback, additional_test_data):
    """
    Test that RiskRegister query actually returns empty if DB table is empty

    Specifically testing the behaviour of the conditional expressions in outcome_data_query() combined with join.
    """

    db.session.query(RiskRegister).delete()
    test_query = download_data_base_query()

    test_serialiser = serialise_download_data(test_query, outcome_categories=False, sheets_required=["RiskRegister"])
    test_data = {sheet: data for sheet, data in test_serialiser}
    test_df = pd.DataFrame.from_records(test_data["RiskRegister"]).dropna(how="all")

    assert len(test_df) == 0


def test_funding_question_programme_joins(seeded_test_client, additional_test_data):
    """
    Test Funding Question query don't get unexpected data via it's join.

    Specifically testing that programme level table (Funding question) does not get rows from
    other rounds that share the same parent programme.
    """

    # this is a funding question with the same parent programme, that shouldn't be returned in this query.
    funding_question = additional_test_data["funding_question"]
    unwanted_submission = additional_test_data["submission"]
    rp_start_wanted = unwanted_submission.reporting_period_end

    base_query = download_data_base_query(min_rp_start=rp_start_wanted)
    test_serialised_data = {sheet: data for sheet, data in serialise_download_data(base_query)}

    df_funding_questions = pd.DataFrame.from_records(test_serialised_data["FundingQuestions"])

    assert funding_question.data_blob["indicator"] not in list(df_funding_questions["Indicator"])

    base_query_all = download_data_base_query()
    test_serialised_data_all = {sheet: data for sheet, data in serialise_download_data(base_query_all)}
    df_funding_questions_all = pd.DataFrame.from_records(test_serialised_data_all["FundingQuestions"])

    assert funding_question.data_blob["indicator"] in list(df_funding_questions_all["Indicator"])

    # df filtered to only show rows with indicator that we don't want in date range filtered db results
    df_all_filtered = df_funding_questions_all.loc[
        df_funding_questions_all["Indicator"] == funding_question.data_blob["indicator"]
    ]
    # test funding_question.indicator only has programme of "TEST-PROGRAMME-ID" in df_all
    assert set(df_all_filtered["ProgrammeID"]) == {"TEST-PROGRAMME-ID"}


def test_programme_progress_joins(seeded_test_client, additional_test_data):
    """
    Test the programme level table (Programme Progress) doesn't get unexpected data via it's join.

    Specifically testing that Programme Progress does not get rows from
    other rounds that share the same parent programme.
    """

    # this is a programme progress record with the same parent programme, that shouldn't be returned in this query.
    programme_progress = additional_test_data["programme_progress"]
    unwanted_submission = additional_test_data["submission"]
    rp_start_wanted = unwanted_submission.reporting_period_end

    base_query = download_data_base_query(min_rp_start=rp_start_wanted)
    test_serialised_data = {sheet: data for sheet, data in serialise_download_data(base_query)}

    df_programme_progress = pd.DataFrame.from_records(test_serialised_data["ProgrammeProgress"])

    assert programme_progress.data_blob["question"] not in list(df_programme_progress["Question"])

    base_query_all = download_data_base_query()
    test_serialised_data_all = {sheet: data for sheet, data in serialise_download_data(base_query_all)}
    df_programme_progress_all = pd.DataFrame.from_records(test_serialised_data_all["ProgrammeProgress"])

    assert programme_progress.data_blob["question"] in list(df_programme_progress_all["Question"])

    # df filtered to only show rows with question that we don't want in date range filtered db results
    df_all_filtered = df_programme_progress_all.loc[
        df_programme_progress_all["Question"] == programme_progress.data_blob["question"]
    ]
    # test programme_progress.question only has programme of "TEST-PROGRAMME-ID" in df_all
    assert set(df_all_filtered["ProgrammeID"]) == {"TEST-PROGRAMME-ID"}


def test_place_detail_joins(seeded_test_client, additional_test_data):
    """
    Test the programme level table (Place Details) doesn't get unexpected data via it's join.

    Specifically testing that Place Details does not get rows from
    other rounds that share the same parent programme.
    """

    # this is a place details record with the same parent programme, that shouldn't be returned in this query.
    place_detail = additional_test_data["place_detail"]
    unwanted_submission = additional_test_data["submission"]
    rp_start_wanted = unwanted_submission.reporting_period_end

    base_query = download_data_base_query(min_rp_start=rp_start_wanted)
    test_serialised_data = {sheet: data for sheet, data in serialise_download_data(base_query)}

    df_place_detail = pd.DataFrame.from_records(test_serialised_data["PlaceDetails"])

    assert place_detail.data_blob["question"] not in list(df_place_detail["Question"])

    base_query_all = download_data_base_query()
    test_serialised_data_all = {sheet: data for sheet, data in serialise_download_data(base_query_all)}
    df_place_detail_all = pd.DataFrame.from_records(test_serialised_data_all["PlaceDetails"])

    assert place_detail.data_blob["question"] in list(df_place_detail_all["Question"])

    # df filtered to only show rows with question that we don't want in date range filtered db results
    df_all_filtered = df_place_detail_all.loc[df_place_detail_all["Question"] == place_detail.data_blob["question"]]
    # test place_detail.question only has programme of "TEST-PROGRAMME-ID" in df_all
    assert set(df_all_filtered["ProgrammeID"]) == {"TEST-PROGRAMME-ID"}


def test_risk_table_for_programme_join(seeded_test_client, additional_test_data):
    """
    Test Risk Register doesn't get unexpected data via joins.

    Specifically that the programme level risks only show up from the expected round, when they
    share a parent programme with historical round data risks.
    """

    programme_risk = additional_test_data["prog_risk"]
    unwanted_submission = additional_test_data["submission"]
    rp_start_wanted = unwanted_submission.reporting_period_end
    base_query = download_data_base_query(min_rp_start=rp_start_wanted)
    test_serialised_data = {sheet: data for sheet, data in serialise_download_data(base_query)}

    df_risk = pd.DataFrame.from_records(test_serialised_data["RiskRegister"])
    assert programme_risk.data_blob["risk_name"] not in list(df_risk["RiskName"])

    base_query_all = download_data_base_query()
    test_serialised_data_all = {sheet: data for sheet, data in serialise_download_data(base_query_all)}
    df_risk_all = pd.DataFrame.from_records(test_serialised_data_all["RiskRegister"])
    assert programme_risk.data_blob["risk_name"] in list(df_risk_all["RiskName"])

    # df filtered to only show rows with risk that we don't want in date range filtered db results
    df_all_filtered = df_risk_all.loc[df_risk_all["RiskName"] == programme_risk.data_blob["risk_name"]]
    # test programme_risk.risk_name only has programme of "TEST-PROGRAMME-ID" in df_all
    assert set(df_all_filtered["ProgrammeID"]) == {"TEST-PROGRAMME-ID"}
    assert df_all_filtered["ProjectID"].isna().all()
    assert set(df_all_filtered["SubmissionID"]) == {"TEST-SUBMISSION-ID"}


def test_outcome_table_for_programme_join(seeded_test_client, additional_test_data):
    """
    Test Outcome Data doesn't get unexpected data via joins.

    Specifically that the programme level Outcomes only show up from the expected round, when they
    share a parent programme with historical round data risks.
    """

    programme_outcome = additional_test_data["outcome_programme"]
    unwanted_submission = additional_test_data["submission"]
    rp_start_wanted = unwanted_submission.reporting_period_end
    base_query = download_data_base_query(min_rp_start=rp_start_wanted)
    test_serialised_data = {sheet: data for sheet, data in serialise_download_data(base_query)}
    df_outcome = pd.DataFrame.from_records(test_serialised_data["OutcomeData"])
    assert programme_outcome.data_blob["unit_of_measurement"] not in list(df_outcome["UnitofMeasurement"])

    base_query_all = download_data_base_query()
    test_serialised_data_all = {sheet: data for sheet, data in serialise_download_data(base_query_all)}
    df_outcome_all = pd.DataFrame.from_records(test_serialised_data_all["OutcomeData"])
    assert programme_outcome.data_blob["unit_of_measurement"] in list(df_outcome_all["UnitofMeasurement"])

    # df filtered to only show rows with outcome that we don't want in date range filtered db results
    df_all_filtered = df_outcome_all.loc[
        df_outcome_all["UnitofMeasurement"] == programme_outcome.data_blob["unit_of_measurement"]
    ]
    # test filtered outcome only has programme of "TEST-PROGRAMME-ID" in df_all
    assert set(df_all_filtered["ProgrammeID"]) == {"TEST-PROGRAMME-ID"}
    assert df_all_filtered["ProjectID"].isna().all()
    assert set(df_all_filtered["SubmissionID"]) == {"TEST-SUBMISSION-ID"}


def test_outcomes_with_non_outcome_filters(seeded_test_client, additional_test_data):
    """Specifically testing the OutcomeData joins when filters applied to OTHER tables."""

    organisation = additional_test_data["organisation"]
    fund = additional_test_data["fund"]
    organisation_uuids = [organisation.id]
    itl_regions = {ITLRegion.SouthWest}
    fund_type_ids = [fund.fund_code]

    base_query = download_data_base_query(
        fund_type_ids=fund_type_ids, itl_regions=itl_regions, organisation_uuids=organisation_uuids
    )

    test_serialised_data = {
        sheet: data
        for sheet, data in serialise_download_data(
            base_query, sheets_required=["ProjectDetails", "OutcomeData", "ProgrammeRef"]
        )
    }
    # Project table with filters applied, for assertion comparison
    project_filtered_df = pd.DataFrame.from_records(test_serialised_data["ProjectDetails"])
    outcome_data_filtered_df = pd.DataFrame.from_records(test_serialised_data["OutcomeData"])
    programme_filtered_df = pd.DataFrame.from_records(test_serialised_data["ProgrammeRef"])

    outcome_data_structure_common_test(outcome_data_filtered_df)

    # check projects column in outcomeData is subset of all projects
    assert np.isin(
        outcome_data_filtered_df["ProjectID"].dropna().unique(), project_filtered_df["ProjectID"].values
    ).all()

    # only project-level outcome rows Explicitly returned by filter should be included in OutcomeData,
    # whereas all child projects of Outcome Programmes should be included in project level tables too.
    assert len(set(outcome_data_filtered_df["ProjectID"].dropna())) < len(
        set(project_filtered_df["ProjectID"].dropna())
    )

    # only 1 programme returned in filter. Only outcome data with either this programme, or projects with this
    # programme as a parent should be returned in outcome data.
    assert set(project_filtered_df["Place"].values) == set(outcome_data_filtered_df["Place"].dropna().values)
    assert set(project_filtered_df["Place"]) == set(programme_filtered_df["ProgrammeName"])


def outcome_data_structure_common_test(outcome_data_df):
    """Common test methods for testing structure of OutcomeData tables."""
    # check each outcome only occurs once (ie not duplicated)
    duplicates = outcome_data_df[outcome_data_df.duplicated()]
    assert len(duplicates) == 0

    # check 1 and only 1 of these 2 columns is always null
    assert (
        (outcome_data_df["ProgrammeID"].isnull() & outcome_data_df["ProjectID"].notnull())
        | (outcome_data_df["ProgrammeID"].notnull() & outcome_data_df["ProjectID"].isnull())
    ).all()
    assert (
        (outcome_data_df["Place"].isnull() & outcome_data_df["ProjectName"].notnull())
        | (outcome_data_df["Place"].notnull() & outcome_data_df["ProjectName"].isnull())
    ).all()


def test_outcome_category_filter(seeded_test_client, additional_test_data, non_transport_outcome_data):
    """
    Test expected Outcome filter behaviour.

    specific case:
    - 1 Programme matches outcome filter, 2 projects match outcome filter.
    - 1 of the projects is a child of matching programme, one isn't
    check in outcomes table, that only these 3 project/programmes show up, 2 proj, 1 prog)
    also, all instances of outcomes show up (can be multiple outcomes per each proj/prog)
    check in project table, all children of prog turn up + 1 proj in filter with different prog
    check in programme table, both turn up.

    "Transport" is used just as a var name to represent the test specific outcome data.
    """
    programme_no_transport_outcome_or_transport_child_projects = non_transport_outcome_data

    assert len(OutcomeData.query.all()) == 31  # smoke test

    #  serialised tables project data (for assertion / comparison)
    test_query_unfiltered = download_data_base_query()
    test_serialised_data_unfiltered = {
        sheet: data
        for sheet, data in serialise_download_data(
            test_query_unfiltered,
            sheets_required=["ProjectDetails", "OutcomeData", "OutcomeRef"],
        )
    }
    outcome_data_unfiltered_df = pd.DataFrame.from_records(test_serialised_data_unfiltered["OutcomeData"])
    outcome_ref_unfiltered_df = pd.DataFrame.from_records(test_serialised_data_unfiltered["OutcomeRef"])
    projects_unfiltered_df = pd.DataFrame.from_records(test_serialised_data_unfiltered["ProjectDetails"])

    #  apply filter to and serialise project and outcome data tables.
    test_query_filtered = query_extend_with_outcome_filter(download_data_base_query(), ["Transport"])
    test_serialised_data_filtered = {
        sheet: data
        for sheet, data in serialise_download_data(
            test_query_filtered,
            sheets_required=["ProjectDetails", "OutcomeData", "OutcomeRef"],
            outcome_categories=["Transport"],
        )
    }
    outcome_data_filtered_df = pd.DataFrame.from_records(test_serialised_data_filtered["OutcomeData"])
    outcome_ref_filtered_df = pd.DataFrame.from_records(test_serialised_data_filtered["OutcomeRef"])

    projects_filtered_df = pd.DataFrame.from_records(test_serialised_data_filtered["ProjectDetails"])

    programme_with_outcome = "Leaky Cauldron regeneration"
    child_project_with_outcome = "ProjectName2"  # project is also child of programme_with_outcome
    non_child_project_with_outcome = "TEST-PROJECT-NAME3"  # project has no parent programme referenced in OutcomeData

    # test structure of outcome FKs is as expected
    outcome_data_structure_common_test(outcome_data_unfiltered_df)
    outcome_data_structure_common_test(outcome_data_filtered_df)

    #  check in outcomes table, that only these 3 project/programmes show up, 2 proj, 1 prog)
    assert set(outcome_data_filtered_df["Place"].dropna().unique()) == {programme_with_outcome}
    assert set(outcome_data_filtered_df["ProjectName"].dropna().unique()) == {
        child_project_with_outcome,
        non_child_project_with_outcome,
    }

    # Tests join between outcome dim and outcome ref, with filter
    assert (outcome_ref_unfiltered_df["OutcomeCategory"] == "Transport").sum() == 2
    assert set(outcome_ref_filtered_df["OutcomeName"]) == set(
        outcome_ref_unfiltered_df.query("OutcomeCategory=='Transport'")["OutcomeName"]
    )
    assert set(outcome_ref_unfiltered_df.query("OutcomeCategory=='Transport'")["OutcomeName"]) == set(
        outcome_data_filtered_df["Outcome"]
    )

    #  check in project table, all children of prog turn up + 1 proj in filter with different prog
    child_projects_of_programme = list(
        projects_unfiltered_df.query("Place=='Leaky Cauldron regeneration'")["ProjectName"]
    )  # all project children of programme with Outcome row

    child_projects_of_programme.append(non_child_project_with_outcome)
    expected_projects = set(
        child_projects_of_programme
    )  # plus extra project with an Outcome but without corresponding programme with outcome

    # check this constructed set matches project filtered by outcome
    assert expected_projects == set(projects_filtered_df["ProjectName"])

    # check that child projects of programme with no matching programme level outcome are not in filtered project table
    assert set(projects_unfiltered_df["ProjectName"]) - set(projects_filtered_df["ProjectName"])

    #  check in programme table, both turn up
    assert len(set(projects_filtered_df["Place"])) == 2

    # check a programme with no links to transport outcomes is not included in the results
    assert (
        programme_no_transport_outcome_or_transport_child_projects.programme_name not in projects_filtered_df["Place"]
    )
