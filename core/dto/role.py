from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from core.db.entities import Role

if TYPE_CHECKING:
    from core.dto.user_programme_role import UserProgrammeRoleDTO


@dataclass
class RoleDTO:
    id: str
    name: str
    description: str
    _user_programme_role_ids: list[str]

    @cached_property
    def user_programme_roles(self) -> list["UserProgrammeRoleDTO"]:
        from core.dto.user_programme_role import get_user_programme_roles_by_ids

        return get_user_programme_roles_by_ids(self._user_programme_role_ids)


def get_role_by_id(role_id: str) -> RoleDTO:
    role: Role = Role.query.get(role_id)
    user_programme_role_ids = [str(user_programme_role.id) for user_programme_role in role.user_programme_roles]
    return RoleDTO(
        id=str(role.id),
        name=role.name,
        description=role.description,
        _user_programme_role_ids=user_programme_role_ids,
    )


def get_roles_by_ids(role_ids: list[str]) -> list[RoleDTO]:
    return [get_role_by_id(role_id) for role_id in role_ids]
