from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from core.db.entities import Fund, Organisation, Programme

if TYPE_CHECKING:
    from core.dto.fund import FundDTO
    from core.dto.organisation import OrganisationDTO
    from core.dto.pending_submission import PendingSubmissionDTO
    from core.dto.project_ref import ProjectRefDTO
    from core.dto.user_programme_role import UserProgrammeRoleDTO


@dataclass
class ProgrammeDTO:
    id: str
    programme_id: str
    organisation_id: str
    fund_type_id: str
    _pending_submission_ids: list[str]
    _project_ref_ids: list[str]
    _user_programme_role_ids: list[str]

    @cached_property
    def organisation(self) -> "OrganisationDTO":
        from core.dto.organisation import get_organisation_by_id

        return get_organisation_by_id(self.organisation_id)

    @cached_property
    def fund(self) -> "FundDTO":
        from core.dto.fund import get_fund_by_id

        return get_fund_by_id(self.fund_type_id)

    @cached_property
    def pending_submissions(self) -> list["PendingSubmissionDTO"]:
        from core.dto.pending_submission import get_pending_submissions_by_ids

        return get_pending_submissions_by_ids(self._pending_submission_ids)

    @cached_property
    def project_refs(self) -> list["ProjectRefDTO"]:
        from core.dto.project_ref import get_project_refs_by_ids

        return get_project_refs_by_ids(self._project_ref_ids)

    @cached_property
    def user_programme_roles(self) -> list["UserProgrammeRoleDTO"]:
        from core.dto.user_programme_role import get_user_programme_roles_by_ids

        return get_user_programme_roles_by_ids(self._user_programme_role_ids)


def _entity_to_dto(programme: Programme) -> ProgrammeDTO:
    return ProgrammeDTO(
        id=str(programme.id),
        programme_id=str(programme.programme_id),
        organisation_id=str(programme.organisation_id),
        fund_type_id=str(programme.fund_type_id),
        _pending_submission_ids=[str(pending_submission.id) for pending_submission in programme.pending_submissions],
        _project_ref_ids=[str(project_ref.id) for project_ref in programme.project_refs],
        _user_programme_role_ids=[
            str(user_programme_role.id) for user_programme_role in programme.user_programme_roles
        ],
    )


def get_programme_by_id(programme_id: str) -> ProgrammeDTO:
    programme: Programme = Programme.query.get(programme_id)
    return _entity_to_dto(programme)


def get_programmes_by_ids(programme_ids: list[str]) -> list[ProgrammeDTO]:
    programmes: list[Programme] = Programme.query.filter(Programme.id.in_(programme_ids)).all()
    return [get_programme_by_id(programme.id) for programme in programmes]


def get_programme_by_fund_and_organisation_slugs(fund_slug: str, organisation_slug: str) -> ProgrammeDTO:
    programme: Programme = (
        Programme.query.join(Fund)
        .join(Organisation)
        .filter(
            Fund.slug == fund_slug,
            Organisation.slug == organisation_slug,
        )
        .first()
    )
    return _entity_to_dto(programme)
