import dataclasses
from collections import defaultdict

from core.db.entities import User


@dataclasses.dataclass
class Access:
    organisation_roles: dict[str, set]
    programme_roles: dict[str, set]


def get_user_access(user_id) -> Access:
    user = User.query.get(user_id)

    organisation_roles: dict[str, set] = defaultdict(set)
    programme_roles: dict[str, set] = defaultdict(set)
    for permission in user.permissions:
        if permission.organisation_id:
            organisation_roles[str(permission.organisation_id)] |= set(permission.role_name)
        else:
            programme_roles[str(permission.programme_id)] |= set(permission.role_name)

    return Access(organisation_roles=organisation_roles, programme_roles=programme_roles)
