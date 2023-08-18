import pandas as pd
import pytest

from core.const import ITLRegion
from core.db.entities import Organisation, Programme, Project, RiskRegister
from core.db.queries import download_data_base_query
from core.serialisation.data_serialiser import serialise_download_data
from core.serialisation.download_json_serializer import serialize_json_data
from core.serialisation.download_xlsx_serializer import serialize_xlsx_data


@pytest.fixture
def download_data(seeded_test_client):
    projects = Project.query.all()
    programmes = Programme.query.all()
    project_outcomes = [outcome for project in projects for outcome in project.outcomes]
    programme_outcomes = [outcome for programme in programmes for outcome in programme.outcomes]
    return programmes, projects, programme_outcomes, project_outcomes


def test_json_serialization(download_data):
    """Tests that serialisation returns at data for each table. Does not assert on the data itself."""
    programmes, projects, programme_outcomes, project_outcomes = download_data

    serialized_data = serialize_json_data(
        projects=projects,
        programmes=programmes,
        project_outcomes=project_outcomes,
        programme_outcomes=programme_outcomes,
    )

    assert serialized_data

    # non-data-specific assertions to check parts of the extract are populated
    assert serialized_data.get("PlaceDetails")
    assert serialized_data.get("ProjectDetails")
    assert serialized_data.get("OrganisationRef")
    assert serialized_data.get("ProgrammeRef")
    assert serialized_data.get("ProgrammeProgress")
    assert serialized_data.get("ProjectProgress")
    assert serialized_data.get("FundingQuestions")
    assert serialized_data.get("Funding")
    assert serialized_data.get("FundingComments")
    assert serialized_data.get("PrivateInvestments")
    assert serialized_data.get("OutputsRef")
    assert serialized_data.get("OutputData")
    assert serialized_data.get("OutcomeRef")
    assert serialized_data.get("OutcomeData")
    assert serialized_data.get("RiskRegister")


def test_xlsx_serialization(download_data):
    """Tests that serialisation returns at data for each table. Does not assert on the data itself."""
    programmes, projects, programme_outcomes, project_outcomes = download_data

    serialized_data = serialize_xlsx_data(
        projects=projects,
        programmes=programmes,
        project_outcomes=project_outcomes,
        programme_outcomes=programme_outcomes,
    )

    assert serialized_data

    # non-data-specific assertions to check parts of the extract are populated
    assert serialized_data.get("PlaceDetails")
    assert serialized_data.get("ProjectDetails")
    assert serialized_data.get("OrganisationRef")
    assert serialized_data.get("ProgrammeRef")
    assert serialized_data.get("ProgrammeProgress")
    assert serialized_data.get("ProjectProgress")
    assert serialized_data.get("FundingQuestions")
    assert serialized_data.get("Funding")
    assert serialized_data.get("FundingComments")
    assert serialized_data.get("PrivateInvestments")
    assert serialized_data.get("OutputsRef")
    assert serialized_data.get("OutputData")
    assert serialized_data.get("OutcomeRef")
    assert serialized_data.get("OutcomeData")
    assert serialized_data.get("RiskRegister")

    # assert all tables contain place and organisation (apart from OrgRef, OutputsRef and OutcomeRef)
    for section_name, data in serialized_data.items():
        if section_name in ["OrganisationRef", "OutputsRef", "OutcomeRef"]:
            continue
        assert "Place" in data[0].keys()
        assert "OrganisationName" in data[0].keys()


def test_serialise_download_data_specific_tab(seeded_test_client, additional_test_data):
    """Test that serialiser func doesn't return all "sheets" of data if "sheets_required" passed as param."""
    base_query = download_data_base_query()
    test_serialised_data = serialise_download_data(base_query, sheets_required=["ProgrammeRef"])
    assert test_serialised_data.keys() == {"ProgrammeRef"}


def test_serialise_download_data_no_filters(seeded_test_client, additional_test_data):
    base_query = download_data_base_query()
    test_serialised_data = serialise_download_data(base_query)

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
    assert len(test_serialised_data["RiskRegister"]) == len(RiskRegister.query.all()) == 27
    assert len(test_serialised_data["ProjectDetails"]) == len(Project.query.all()) == 12


def test_serialise_download_data_organisation_filter(seeded_test_client, additional_test_data):
    """Assert filter applied reduces results returned."""
    organisation = additional_test_data[0]
    organisation_uuids = [organisation.id]
    test_query_org = download_data_base_query(organisation_uuids=organisation_uuids)
    test_serialised_data = serialise_download_data(test_query_org)

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

    test_serialised_data = serialise_download_data(test_query_region)

    #  read into pandas for ease of inspection
    test_fund_filtered_df = pd.DataFrame.from_records(test_serialised_data["ProjectDetails"])

    project4 = additional_test_data[7]
    assert project4.project_id not in test_fund_filtered_df["ProjectID"]  # not in SW region
    assert all(
        ITLRegion.SouthWest in project.itl_regions
        for project in Project.query.filter(Project.project_id.in_(test_fund_filtered_df["ProjectID"]))
    )
