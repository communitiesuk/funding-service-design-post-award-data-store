from flask import abort

from core.db.entities import Organisation


def get_organisation_names():
    """Returns a list of all distinct organisation names.

    :return: List of organisation names
    """
    organisations = Organisation.query.with_entities(Organisation.id, Organisation.organisation_name).distinct().all()

    if not organisations:
        return abort(404, "No organisation names found.")

    organisation_list = [{"name": row.organisation_name, "id": str(row.id)} for row in organisations]

    return organisation_list, 200
