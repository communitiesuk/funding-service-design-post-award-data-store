from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from core.db.entities import ProjectRef

if TYPE_CHECKING:
    from core.dto.programme import ProgrammeDTO


@dataclass
class ProjectRefDTO:
    id: str
    project_id: str
    project_name: str
    slug: str
    state: str
    data_blob: dict
    programme_id: str

    @cached_property
    def programme(self) -> "ProgrammeDTO" | None:
        from core.dto.programme import get_programme_by_id

        if not self.programme_id:
            return None
        return get_programme_by_id(self.programme_id)


def _entity_to_dto(project_ref: ProjectRef) -> ProjectRefDTO:
    return ProjectRefDTO(
        id=str(project_ref.id),
        project_id=project_ref.project_id,
        project_name=project_ref.project_name,
        slug=project_ref.slug,
        state=project_ref.state,
        data_blob=project_ref.data_blob,
        programme_id=str(project_ref.programme_id),
    )


def get_project_ref_by_id(project_ref_id: str) -> ProjectRefDTO:
    project_ref: ProjectRef = ProjectRef.query.get(project_ref_id)
    return _entity_to_dto(project_ref)


def get_project_refs_by_ids(project_ref_ids: list[str]) -> list[ProjectRefDTO]:
    project_refs = ProjectRef.query.filter(ProjectRef.id.in_(project_ref_ids)).all()
    return [get_project_ref_by_id(project_ref.id) for project_ref in project_refs]


def get_project_ref_by_slug(slug: str) -> ProjectRefDTO:
    project_ref: ProjectRef = ProjectRef.query.filter_by(slug=slug).first()
    return _entity_to_dto(project_ref)
