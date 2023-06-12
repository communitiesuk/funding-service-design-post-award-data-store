from core.db.entities import Programme, Project
from core.serialization.download_json_serializer import serialize_download_data


def test_serialization(seeded_test_client):
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
