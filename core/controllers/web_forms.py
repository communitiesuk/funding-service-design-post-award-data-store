from flask import Response, make_response, request

from core.db import db
from core.db.entities import PendingSubmission, PendingSubmissionForm


def create_pending_submission() -> Response:
    """
    Create a new pending submission.
    """
    fund_name = request.json.get("fund_name")
    organisation_name = request.json.get("organisation_name")
    pending_submission = PendingSubmission(fund_name=fund_name, organisation_name=organisation_name)
    db.session.add(pending_submission)
    db.session.commit()
    return make_response({"pending_submission_id": pending_submission.id}, 200)


def get_all_pending_submissions() -> Response:
    """
    Get all pending submissions for a given fund and organisation.
    """
    fund_name = request.args.get("fund_name")
    organisation_name = request.args.get("organisation_name")
    pending_submissions = PendingSubmission.query.filter_by(
        fund_name=fund_name, organisation_name=organisation_name
    ).all()
    pending_submissions = [submission.to_dict() for submission in pending_submissions]
    return make_response({"pending_submissions": pending_submissions}, 200)


def get_pending_submission(pending_submission_id: str) -> Response:
    """
    Get a pending submission by ID, including all forms and questions.
    """
    pending_submission = PendingSubmission.query.get(pending_submission_id)
    if not pending_submission:
        return make_response({"error": "Pending submission not found"}, 404)
    return make_response({"pending_submission": pending_submission.to_dict()}, 200)


def upload() -> Response:
    """
    Upload data to the database.
    """
    pending_submission_id = request.args.get("pending_submission_id")
    request_data = request.get_json()
    form_name = request_data.get("metadata", {}).get("form_name", "unknown")

    # Maybe filter out any incomplete fields?

    # Create a new instance of PendingSubmissionForm
    pending_submission_form = PendingSubmissionForm(
        pending_submission_id=pending_submission_id, form_name=form_name, data=request_data
    )

    # Add and commit to the database
    db.session.add(pending_submission_form)
    db.session.commit()

    return make_response("Data uploaded successfully", 200)
