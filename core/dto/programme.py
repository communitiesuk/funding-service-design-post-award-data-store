from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from core.db import db
from core.db.entities import PendingSubmission, Programme

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
    programme_name: str
    organisation_id: str
    fund_type_id: str
    _pending_submission_id: str
    _project_ref_ids: list[str]
    _user_programme_role_ids: list[str] = None

    @cached_property
    def organisation(self) -> "OrganisationDTO" | None:
        from core.dto.organisation import get_organisation_by_id

        if not self.organisation_id:
            return None
        return get_organisation_by_id(self.organisation_id)

    @cached_property
    def fund(self) -> "FundDTO" | None:
        from core.dto.fund import get_fund_by_id

        if not self.fund_type_id:
            return None
        return get_fund_by_id(self.fund_type_id)

    @cached_property
    def pending_submission(self) -> "PendingSubmissionDTO" | None:
        from core.dto.pending_submission import get_pending_submission_by_id

        if not self._pending_submission_id:
            return None
        return get_pending_submission_by_id(self._pending_submission_id)

    @cached_property
    def project_refs(self) -> list["ProjectRefDTO"]:
        from core.dto.project_ref import get_project_refs_by_ids

        if not self._project_ref_ids:
            return []
        return get_project_refs_by_ids(self._project_ref_ids)

    @cached_property
    def user_programme_roles(self) -> list["UserProgrammeRoleDTO"]:
        from core.dto.user_programme_role import get_user_programme_roles_by_ids

        if not self._user_programme_role_ids:
            return []
        return get_user_programme_roles_by_ids(self._user_programme_role_ids)


def get_programme_by_id(programme_id: str) -> ProgrammeDTO:
    programme: Programme = Programme.query.get(programme_id)
    project_ref_ids = [str(project_ref.id) for project_ref in programme.project_refs]
    user_programme_role_ids = [str(user_programme_role.id) for user_programme_role in programme.user_programme_roles]
    return ProgrammeDTO(
        id=str(programme.id),
        programme_id=str(programme.programme_id),
        programme_name=programme.programme_name,
        organisation_id=str(programme.organisation_id),
        fund_type_id=str(programme.fund_type_id),
        _pending_submission_id=str(programme.pending_submission.id) if programme.pending_submission else "",
        _project_ref_ids=project_ref_ids,
        _user_programme_role_ids=user_programme_role_ids,
    )


def get_programmes_by_ids(programme_ids: list[str]) -> list[ProgrammeDTO]:
    programmes = Programme.query.filter(Programme.id.in_(programme_ids)).all()
    return [get_programme_by_id(programme.id) for programme in programmes]


def persist_pending_submission(programme_dto: ProgrammeDTO, data_blob: dict) -> None:
    pending_submission_dto = programme_dto.pending_submission
    if pending_submission_dto:
        pending_submission: PendingSubmission = PendingSubmission.query.get(pending_submission_dto.id)
        pending_submission.data_blob = data_blob
    else:
        pending_submission = PendingSubmission(
            programme_id=programme_dto.id,
            data_blob=data_blob,
        )
        db.session.add(pending_submission)
    db.session.commit()
