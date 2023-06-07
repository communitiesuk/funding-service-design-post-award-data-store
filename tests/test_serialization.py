from core.db.entities import Organisation, Programme, Project
from core.serialization.download_json_serializer import serialize_download_data


def test_serialization(seeded_app_ctx):
    projects = Project.query.all()
    programmes = Programme.query.all()
    organisations = Organisation.query.all()
    outcomes = [outcome for project in projects for outcome in project.outcomes]
    serialized_data = serialize_download_data(
        projects=projects, programmes=programmes, organisations=organisations, outcomes=outcomes
    )
    assert serialized_data
