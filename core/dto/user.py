from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from core.db.entities import User

if TYPE_CHECKING:
    from core.dto.user_programme_role import UserProgrammeRoleDTO


@dataclass
class UserDTO:
    id: str
    email_address: str
    full_name: str
    phone_number: str
    _user_programme_role_ids: list[str]

    @cached_property
    def user_programme_roles(self) -> list["UserProgrammeRoleDTO"]:
        from core.dto.user_programme_role import get_user_programme_roles_by_ids

        if not self._user_programme_role_ids:
            return []
        return get_user_programme_roles_by_ids(self._user_programme_role_ids)


def get_user_by_id(user_id: str) -> UserDTO:
    user: User = User.query.get(user_id)
    user_programme_role_ids = [str(user_programme_role.id) for user_programme_role in user.user_programme_roles]
    return UserDTO(
        id=str(user.id),
        email_address=user.email_address,
        full_name=user.full_name,
        phone_number=user.phone_number,
        _user_programme_role_ids=user_programme_role_ids,
    )
