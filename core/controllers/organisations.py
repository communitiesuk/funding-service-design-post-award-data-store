from core.db.entities import Organisation


def get_organisations_by_id(organisation_ids: list[str]) -> list[Organisation]:
    return Organisation.query.filter(Organisation.id.in_(organisation_ids)).all()
