import pandas as pd

from core.const import ITLRegion
from core.db import db
from core.db.entities import (
    Organisation,
    OutcomeData,
    OutcomeDim,
    Project,
    RiskRegister,
)
from core.db.queries import download_data_base_query
from core.serialisation.data_serialiser import serialise_download_data


def test_serialise_download_data_specific_tab(seeded_test_client, additional_test_data):
    """Test that serialiser func doesn't return all "sheets" of data if "sheets_required" passed as param."""
    base_query = download_data_base_query()
    test_generator = serialise_download_data(base_query, sheets_required=["ProgrammeRef"])
    test_serialised_data = {sheet: data for sheet, data in test_generator}

    assert test_serialised_data.keys() == {"ProgrammeRef"}


def test_serialise_download_data_no_filters(seeded_test_client, additional_test_data):
    base_query = download_data_base_query()
    test_serialised_data = {sheet: data for sheet, data in serialise_download_data(base_query)}

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
    assert test_serialised_data.get("OutputsRef")
    assert test_serialised_data.get("OutputData")
    assert test_serialised_data.get("OutcomeRef")
    assert test_serialised_data.get("OutcomeData")
    assert test_serialised_data.get("RiskRegister")
    assert len(test_serialised_data) == 15

    # assert all tables contain place and organisation (apart from OrgRef, OutputsRef and OutcomeRef)
    for section_name, data in test_serialised_data.items():
        if section_name in ["ProgrammeRef", "OrganisationRef", "OutputsRef", "OutcomeRef"]:
            continue
        assert "Place" in data[0].keys()
        assert "OrganisationName" in data[0].keys()

    # assert correct number of column headers in each serialised table
    assert list(test_serialised_data["PlaceDetails"][0].keys()) == [
        "SubmissionID",
        "ProgrammeID",
        "Question",
        "Indicator",
        "Answer",
        "Place",
        "OrganisationName",
    ]
    assert list(test_serialised_data["ProjectDetails"][0].keys()) == [
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
    assert list(test_serialised_data["OrganisationRef"][0].keys()) == ["OrganisationName", "Geography"]
    assert list(test_serialised_data["ProgrammeRef"][0].keys()) == [
        "ProgrammeID",
        "ProgrammeName",
        "FundTypeID",
        "OrganisationName",
    ]
    assert list(test_serialised_data["ProgrammeProgress"][0].keys()) == [
        "SubmissionID",
        "ProgrammeID",
        "Question",
        "Answer",
        "Place",
        "OrganisationName",
    ]
    assert list(test_serialised_data["ProjectProgress"][0].keys()) == [
        "SubmissionID",
        "ProjectID",
        "StartDate",
        "CompletionDate",
        "ProjectAdjustmentRequestStatus",
        "ProjectDeliveryStatus",
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
    assert list(test_serialised_data["FundingQuestions"][0].keys()) == [
        "SubmissionID",
        "ProgrammeID",
        "Question",
        "Indicator",
        "Answer",
        "GuidanceNotes",
        "Place",
        "OrganisationName",
    ]
    assert list(test_serialised_data["Funding"][0].keys()) == [
        "SubmissionID",
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
    assert list(test_serialised_data["FundingComments"][0].keys()) == [
        "SubmissionID",
        "ProjectID",
        "Comment",
        "ProjectName",
        "Place",
        "OrganisationName",
    ]
    assert list(test_serialised_data["PrivateInvestments"][0].keys()) == [
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
    assert list(test_serialised_data["OutputsRef"][0].keys()) == ["OutputName", "OutputCategory"]
    assert list(test_serialised_data["OutputData"][0].keys()) == [
        "SubmissionID",
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
    assert list(test_serialised_data["OutcomeRef"][0].keys()) == ["OutcomeName", "OutcomeCategory"]
    assert list(test_serialised_data["OutcomeData"][0].keys()) == [
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
    assert list(test_serialised_data["RiskRegister"][0].keys()) == [
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

    # check a couple of tables that all results are returned
    assert len(test_serialised_data["RiskRegister"]) == len(RiskRegister.query.all()) == 28
    assert len(test_serialised_data["ProjectDetails"]) == len(Project.query.all()) == 12


def test_serialise_download_data_organisation_filter(seeded_test_client, additional_test_data):
    """Assert filter applied reduces results returned."""
    organisation = additional_test_data["organisation"]
    organisation_uuids = [organisation.id]
    test_query_org = download_data_base_query(organisation_uuids=organisation_uuids)
    test_serialised_data = {sheet: data for sheet, data in serialise_download_data(test_query_org)}

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

    test_serialised_data = {sheet: data for sheet, data in serialise_download_data(test_query_region)}
    #  read into pandas for ease of inspection
    test_fund_filtered_df = pd.DataFrame.from_records(test_serialised_data["ProjectDetails"])

    project4 = additional_test_data["project4"]
    assert project4.project_id not in test_fund_filtered_df["ProjectID"]  # not in SW region
    assert all(
        ITLRegion.SouthWest in project.itl_regions
        for project in Project.query.filter(Project.project_id.in_(test_fund_filtered_df["ProjectID"]))
    )


def test_outcomes_table_empty(seeded_test_client, additional_test_data):
    """
    Test that OutcomeData query actually returns empty if DB table is empty

    Specifically testing the behaviour of the conditional expressions in outcome_data_query(), combined with outer
    join to OutcomeData in main query
    """
    db.session.query(OutcomeData).delete()
    db.session.query(OutcomeDim).delete()
    db.session.flush()
    test_query = download_data_base_query()

    test_serialiser = serialise_download_data(test_query, sheets_required=["OutcomeData", "OutcomeRef"])
    test_data = {sheet: data for sheet, data in test_serialiser}
    test_df_outcome_data = pd.DataFrame.from_records(test_data["OutcomeData"]).dropna(how="all")

    assert len(test_df_outcome_data) == 0

    test_df_outcome_ref = pd.DataFrame.from_records(test_data["OutcomeData"]).dropna(how="all")
    assert len(test_df_outcome_ref) == 0


def test_risks_table_empty(seeded_test_client, additional_test_data):
    """
    Test that OutcomeData query actually returns empty if DB table is empty

    Specifically testing the behaviour of the conditional expressions in outcome_data_query() combined with inner join.
    """

    db.session.query(RiskRegister).delete()
    db.session.flush()
    test_query = download_data_base_query()

    test_serialiser = serialise_download_data(test_query, sheets_required=["RiskRegister"])
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

    assert funding_question.indicator not in list(df_funding_questions["Indicator"])

    base_query_all = download_data_base_query()
    test_serialised_data_all = {sheet: data for sheet, data in serialise_download_data(base_query_all)}
    df_funding_questions_all = pd.DataFrame.from_records(test_serialised_data_all["FundingQuestions"])

    assert funding_question.indicator in list(df_funding_questions_all["Indicator"])

    # df filtered to only show rows with indicator that we don't want in date range filtered db results
    df_all_filtered = df_funding_questions_all.loc[df_funding_questions_all["Indicator"] == funding_question.indicator]
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

    assert programme_progress.question not in list(df_programme_progress["Question"])

    base_query_all = download_data_base_query()
    test_serialised_data_all = {sheet: data for sheet, data in serialise_download_data(base_query_all)}
    df_programme_progress_all = pd.DataFrame.from_records(test_serialised_data_all["ProgrammeProgress"])

    assert programme_progress.question in list(df_programme_progress_all["Question"])

    # df filtered to only show rows with question that we don't want in date range filtered db results
    df_all_filtered = df_programme_progress_all.loc[
        df_programme_progress_all["Question"] == programme_progress.question
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

    assert place_detail.question not in list(df_place_detail["Question"])

    base_query_all = download_data_base_query()
    test_serialised_data_all = {sheet: data for sheet, data in serialise_download_data(base_query_all)}
    df_place_detail_all = pd.DataFrame.from_records(test_serialised_data_all["PlaceDetails"])

    assert place_detail.question in list(df_place_detail_all["Question"])

    # df filtered to only show rows with question that we don't want in date range filtered db results
    df_all_filtered = df_place_detail_all.loc[df_place_detail_all["Question"] == place_detail.question]
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
    assert programme_risk.risk_name not in list(df_risk["RiskName"])

    base_query_all = download_data_base_query()
    test_serialised_data_all = {sheet: data for sheet, data in serialise_download_data(base_query_all)}
    df_risk_all = pd.DataFrame.from_records(test_serialised_data_all["RiskRegister"])
    assert programme_risk.risk_name in list(df_risk_all["RiskName"])

    # df filtered to only show rows with risk that we don't want in date range filtered db results
    df_all_filtered = df_risk_all.loc[df_risk_all["RiskName"] == programme_risk.risk_name]
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
    assert programme_outcome.unit_of_measurement not in list(df_outcome["UnitofMeasurement"])

    base_query_all = download_data_base_query()
    test_serialised_data_all = {sheet: data for sheet, data in serialise_download_data(base_query_all)}
    df_outcome_all = pd.DataFrame.from_records(test_serialised_data_all["OutcomeData"])
    assert programme_outcome.unit_of_measurement in list(df_outcome_all["UnitofMeasurement"])

    # df filtered to only show rows with outcome that we don't want in date range filtered db results
    df_all_filtered = df_outcome_all.loc[df_outcome_all["UnitofMeasurement"] == programme_outcome.unit_of_measurement]
    # test filtered outcome only has programme of "TEST-PROGRAMME-ID" in df_all
    assert set(df_all_filtered["ProgrammeID"]) == {"TEST-PROGRAMME-ID"}
    assert df_all_filtered["ProjectID"].isna().all()
    assert set(df_all_filtered["SubmissionID"]) == {"TEST-SUBMISSION-ID"}
