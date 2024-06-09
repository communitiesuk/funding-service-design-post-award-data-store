from sqlalchemy import func, or_

from core.db.entities import Organisation, Programme


def get_organisations_by_id_or_programme_id(
    organisation_ids: list[str], programme_ids: list[str]
) -> list[Organisation]:
    subquery = (
        Programme.query.filter(Programme.id.in_(programme_ids))
        .with_entities(Programme.organisation_id)
        .distinct()
        .subquery()
    )

    return (
        Organisation.query.filter(or_(Organisation.id.in_(organisation_ids), Organisation.id.in_(subquery)))
        .order_by(func.lower(Organisation.organisation_name))
        .all()
    )
