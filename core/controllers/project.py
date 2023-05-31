from flask import abort

from core.db.entities import Programme, Project


def get_programme(programme_id: str):
    """Takes a value for programme_id and returns the associated programme data

    /programme/{programme_id}

    :param programme_id: the programme_id provided as a string
    :return: JSON object with the programme dimensions
    """
    programme = Programme.query.filter_by(programme_id=programme_id).first()

    if not programme:
        return abort(
            404,
            f"The provided programme_id: {programme_id} did not return any results.",
        )

    return programme.to_dict(), 200


def get_project(project_id: str):
    """Takes a value for project_id and returns the associated project data.

    /project/{project_id}

    :param project_id: the project_id provided as a string
    :return: all data associated with a project
    """
    project = Project.query.filter_by(project_id=project_id).first()

    if not project:
        return abort(
            404,
            f"The provided project_id: {project_id} did not return any results.",
        )

    return project.to_dict(), 200
