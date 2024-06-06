from core.db import db
from core.db.entities import PendingSubmission, Programme, Project


def get_programme_question_data(programme: Programme, question_key: str):
    pending_submission = PendingSubmission.query.filter_by(programme_id=programme.id).one_or_none()
    if not pending_submission:
        return None

    return pending_submission.data_blob["programme"][question_key]


def set_programme_question_data(programme: Programme, question_key: str, question_data):
    pending_submission = PendingSubmission.query.filter_by(programme_id=programme.id).one_or_none()
    if not pending_submission:
        pending_submission = PendingSubmission(programme_id=programme.id)
        pending_submission.data_blob = {"programme": {}, "projects": {}}
        db.session.add(pending_submission)

    pending_submission.data_blob["programme"][question_key] = question_data
    db.session.commit()


def get_project_question_data(programme: Programme, project: Project, question_key: str):
    pending_submission = PendingSubmission.query.filter_by(programme_id=programme.id).one_or_none()
    if not pending_submission:
        return None

    return pending_submission.data_blob["projects"].get(str(project.id), {}).get(question_key)


def set_project_question_data(programme: Programme, project: Project, question_key: str, question_data):
    pending_submission = PendingSubmission.query.filter_by(programme_id=programme.id).one_or_none()
    if not pending_submission:
        pending_submission = PendingSubmission(programme_id=programme.id)
        pending_submission.data_blob = {"programme": {}, "projects": {}}
        db.session.add(pending_submission)

    pending_submission.data_blob["projects"][str(project.id)] = pending_submission.data_blob["projects"].get(
        str(project.id), {}
    )
    pending_submission.data_blob["projects"][str(project.id)][question_key] = question_data
    db.session.commit()
