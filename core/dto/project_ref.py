from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.db.entities import ProjectRef

if TYPE_CHECKING:
    from core.dto.programme import ProgrammeDTO


@dataclass
class ProjectRefDTO:
    id: str
    project_code: str
    project_name: str
    postcodes: list[str]
    state: str
    data_blob: dict
    programme_id: str

    @property
    def programme(self) -> "ProgrammeDTO":
        from core.dto.programme import get_programme_by_id

        return get_programme_by_id(self.programme_id)


def get_project_ref_by_id(project_ref_id: str) -> ProjectRefDTO:
    project_ref = ProjectRef.query.get(project_ref_id)
    return ProjectRefDTO(
        id=(project_ref.id),
        project_code=project_ref.project_code,
        project_name=project_ref.project_name,
        postcodes=project_ref.postcodes,
        state=project_ref.state,
        data_blob=project_ref.data_blob,
        programme_id=project_ref.programme_id,
    )


def get_project_refs_by_ids(project_ref_ids: list[str]) -> list[ProjectRefDTO]:
    project_refs = ProjectRef.query.filter(ProjectRef.id.in_(project_ref_ids)).all()
    return [get_project_ref_by_id(project_ref.id) for project_ref in project_refs]
