from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from core.db.entities import UserProgrammeRole

if TYPE_CHECKING:
    from core.dto.programme import ProgrammeDTO
    from core.dto.role import RoleDTO
    from core.dto.user import UserDTO


@dataclass
class UserProgrammeRoleDTO:
    id: str
    user_id: str
    programme_id: str
    role_id: str

    @cached_property
    def user(self) -> "UserDTO" | None:
        from core.dto.user import get_user_by_id

        if not self.user_id:
            return None
        return get_user_by_id(self.user_id)

    @cached_property
    def programme(self) -> "ProgrammeDTO" | None:
        from core.dto.programme import get_programme_by_id

        if not self.programme_id:
            return None
        return get_programme_by_id(self.programme_id)

    @cached_property
    def role(self) -> "RoleDTO" | None:
        from core.dto.role import get_role_by_id

        if not self.role_id:
            return None
        return get_role_by_id(self.role_id)


def get_user_programme_role_by_id(user_programme_role_id: str) -> UserProgrammeRoleDTO:
    user_programme_role: UserProgrammeRole = UserProgrammeRole.query.get(user_programme_role_id)
    return UserProgrammeRoleDTO(
        id=str(user_programme_role.id),
        user_id=str(user_programme_role.user_id),
        programme_id=str(user_programme_role.programme_id),
        role_id=str(user_programme_role.role_id),
    )


def get_user_programme_roles_by_ids(user_programme_role_ids: list[str]) -> list[UserProgrammeRoleDTO]:
    return [get_user_programme_role_by_id(user_programme_role_id) for user_programme_role_id in user_programme_role_ids]
