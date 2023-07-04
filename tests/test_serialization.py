from core.db.entities import Programme, Project
from core.serialization.download_json_serializer import serialize_download_data


def test_serialization(seeded_test_client):
    """Tests that serialization returns at data for each table. Does not assert on the data itself."""
    projects = Project.query.all()
    programmes = Programme.query.all()
    project_outcomes = [outcome for project in projects for outcome in project.outcomes]
    programme_outcomes = [outcome for programme in programmes for outcome in programme.outcomes]
    serialized_data = serialize_download_data(
        projects=projects,
        programmes=programmes,
        project_outcomes=project_outcomes,
        programme_outcomes=programme_outcomes,
    )

    assert serialized_data  # blunt test for run time errors

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
