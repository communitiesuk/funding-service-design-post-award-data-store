import copy

from core.db import db
from core.db.entities import PendingSubmission, Programme, Project


def _naive_dict_merge(merge_into: dict, merge_from: dict):
    for key in merge_from:
        if key not in merge_into:
            merge_into[key] = copy.deepcopy(merge_from[key])
        else:
            if isinstance(merge_into[key], dict):
                _naive_dict_merge(merge_into[key], merge_from[key])
            else:
                merge_into[key] = merge_from[key]


def get_programme_submission_data(programme: Programme):
    pending_submission = PendingSubmission.query.filter_by(programme_id=programme.id).one_or_none()
    if not pending_submission:
        return None

    return pending_submission.data_blob["programme"]


def set_programme_submission_data(programme: Programme, data_blob_to_merge: dict):
    pending_submission = PendingSubmission.query.filter_by(programme_id=programme.id).one_or_none()
    if not pending_submission:
        pending_submission = PendingSubmission(programme_id=programme.id)
        pending_submission.data_blob = {"programme": {}, "projects": {}}
        db.session.add(pending_submission)

    _naive_dict_merge(pending_submission.data_blob["programme"], data_blob_to_merge)
    db.session.commit()


def get_project_submission_data(programme: Programme, project: Project):
    pending_submission = PendingSubmission.query.filter_by(programme_id=programme.id).one_or_none()
    if not pending_submission:
        return None

    return pending_submission.data_blob["projects"].get(str(project.id), {})


def set_project_submission_data(programme: Programme, project: Project, data_blob_to_merge: dict):
    pending_submission = PendingSubmission.query.filter_by(programme_id=programme.id).one_or_none()
    if not pending_submission:
        pending_submission = PendingSubmission(programme_id=programme.id)
        pending_submission.data_blob = {"programme": {}, "projects": {}}
        db.session.add(pending_submission)

    project_data_blob = pending_submission.data_blob["projects"].setdefault(str(project.id), {})
    _naive_dict_merge(project_data_blob, data_blob_to_merge)
    db.session.commit()
