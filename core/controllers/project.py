from flask import abort

from core.db.entities import Package, Project


def get_package(package_id):
    """Takes a value for package_id and returns the associated package data

    :param package_id: the package_id provided as a string
    :return: JSON object with the package dimensions
    """
    package = Package.query.filter_by(package_id=package_id).first()

    if not package:
        return abort(
            404,
            f"The provided package_id: {package_id} did not return any results.",
        )

    return package.to_dict(), 200


def get_project(project_id: str):
    """Takes a value for project_id and returns the associated project data.

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
