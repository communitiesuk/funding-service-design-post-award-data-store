import pytest

from core.db.entities import Programme, Project
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
