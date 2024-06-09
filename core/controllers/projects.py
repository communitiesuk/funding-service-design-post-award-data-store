from core.db.entities import ProjectRef


def get_canonical_projects_by_programme_id(programme_id: str) -> list[ProjectRef]:
    return ProjectRef.query.filter(ProjectRef.programme_id == programme_id).all()
