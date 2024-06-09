from core.db.entities import Programme


def get_programme_by_id(programme_id: str) -> Programme:
    return Programme.query.get(programme_id)


def get_programmes_by_id(programme_ids: list[str]) -> list[Programme]:
    return Programme.query.filter(Programme.id.in_(programme_ids)).all()
