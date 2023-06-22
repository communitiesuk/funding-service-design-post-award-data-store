from sqlalchemy.orm import joinedload

import core.db.entities as ents


def get_programme_child_with_natural_keys_query(child_model, programme_ids):
    """Filters a Programme child table by programme id and loads parent natural keys.

    This function pre-loads the parent submission.submission_id and programme.programme_id of the filtered results
    as an optimisation because they're required to take the place of the FK UUIDs in the serialized data output.

    :param child_model: A child model of Programme
    :param programme_ids: A list of programme ids
    :return: A list of child models with preloaded natural FKs.
    """
    return child_model.query.filter(child_model.programme_id.in_(programme_ids)).options(
        joinedload(child_model.submission).load_only(ents.Submission.submission_id),
        joinedload(child_model.programme).load_only(ents.Programme.programme_id),
    )


def get_project_child_with_natural_keys_query(child_model, project_ids):
    """Filters a Project child table by project id and loads parent natural keys.

    This function pre-loads the parent submission.submission_id and project.project_id of the filtered results
    as an optimisation because they're required to take the place of the FK UUIDs in the serialized data output.

    :param child_model: A child model of Project
    :param project_ids: A list of project ids
    :return: A list of child models with preloaded natural FKs.
    """
    return child_model.query.filter(child_model.project_id.in_(project_ids)).options(
        joinedload(child_model.submission).load_only(ents.Submission.submission_id),
        joinedload(child_model.project).load_only(ents.Project.project_id),
    )
