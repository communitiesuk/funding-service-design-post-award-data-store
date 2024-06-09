from core.db.entities import User, UserPermissionJunctionTable, UserRoles


def get_users_for_programme_with_role(programme_id: str, role: UserRoles) -> list[User]:
    users_subquery = (
        UserPermissionJunctionTable.query.filter(
            UserPermissionJunctionTable.programme_id == programme_id,
            UserPermissionJunctionTable.role_name.any(role),
        )
        .distinct()
        .with_entities(UserPermissionJunctionTable.user_id)
        .subquery()
    )

    return User.query.filter(User.id.in_(users_subquery)).all()


def get_users_for_organisation_with_role(organisation_id: str, role: UserRoles) -> list[User]:
    users_subquery = (
        UserPermissionJunctionTable.query.filter(
            UserPermissionJunctionTable.organisation_id == organisation_id,
            UserPermissionJunctionTable.role_name.any(role),
        )
        .distinct()
        .with_entities(UserPermissionJunctionTable.user_id)
        .subquery()
    )

    return User.query.filter(User.id.in_(users_subquery)).all()
