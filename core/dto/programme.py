from dataclasses import dataclass
from typing import TYPE_CHECKING

from core.db.entities import Programme

if TYPE_CHECKING:
    from core.dto.fund import FundDTO
    from core.dto.organisation import OrganisationDTO
    from core.dto.project_ref import ProjectRefDTO


@dataclass
class ProgrammeDTO:
    id: str
    programme_id: str
    programme_name: str
    organisation_id: str
    fund_type_id: str
    _project_ref_ids: list[str]

    @property
    def organisation(self) -> "OrganisationDTO":
        from core.dto.organisation import get_organisation_by_id

        return get_organisation_by_id(self.organisation_id)

    @property
    def fund(self) -> "FundDTO":
        from core.dto.fund import get_fund_by_id

        return get_fund_by_id(self.fund_type_id)

    @property
    def project_refs(self) -> list["ProjectRefDTO"]:
        from core.dto.project_ref import get_project_refs_by_ids

        return get_project_refs_by_ids(self._project_ref_ids)


def get_programme_by_id(programme_id: str) -> ProgrammeDTO:
    programme: Programme = Programme.query.get(programme_id)
    project_ref_ids = [project_ref.id for project_ref in programme.project_refs]
    return ProgrammeDTO(
        id=str(programme.id),
        programme_id=programme.programme_id,
        programme_name=programme.programme_name,
        organisation_id=programme.organisation_id,
        fund_type_id=programme.fund_type_id,
        _project_ref_ids=project_ref_ids,
    )


def get_programmes_by_ids(programme_ids: list[str]) -> list[ProgrammeDTO]:
    programmes = Programme.query.filter(Programme.id.in_(programme_ids)).all()
    return [get_programme_by_id(programme.id) for programme in programmes]
