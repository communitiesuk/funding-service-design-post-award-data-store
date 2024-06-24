from core.db import db
from core.db.entities import PendingSubmission, Programme
from report.persistence.report import Report
from report.persistence.submission import Submission


def get_submission(programme: Programme) -> Submission:
    pending_submission = PendingSubmission.query.filter_by(programme_id=programme.id).one_or_none()
    if not pending_submission:
        return Submission(programme_report=Report(name=programme.programme_name, sections=[]), project_reports=[])
    return Submission.load_from_json(pending_submission.data_blob)


def persist_submission(programme: Programme, submission: Submission):
    pending_submission = PendingSubmission.query.filter_by(programme_id=programme.id).one_or_none()
    if not pending_submission:
        pending_submission = PendingSubmission(programme_id=programme.id)
        db.session.add(pending_submission)
    pending_submission.data_blob = submission.serialize()
    db.session.commit()
