from io import BytesIO

import requests
from flask import current_app, flash, g, redirect, request, url_for
from flask_admin import BaseView, expose
from flask_admin.helpers import flash_errors
from sqlalchemy.exc import NoResultFound
from werkzeug.datastructures import FileStorage

from admin.base import AdminAuthorizationMixin
from admin.forms import ReingestAdminForm, RetrieveFailedSubmissionAdminForm, RetrieveSubmissionAdminForm
from data_store.controllers.failed_submission import get_failed_submission
from data_store.controllers.ingest import ingest
from data_store.controllers.retrieve_submission_file import retrieve_submission_file
from data_store.db import db
from data_store.db.entities import Submission


class BaseAdminView(AdminAuthorizationMixin, BaseView):
    pass


class ReingestAdminView(BaseAdminView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = ReingestAdminForm(request.form)

        if form.is_submitted():
            if form.validate():
                try:
                    submission = Submission.query.filter_by(submission_id=form.submission_id.data).one()
                except NoResultFound as e:
                    flash(str(e), "error")
                    return self.render("admin/reingest.html", form=form)

                try:
                    presigned_url = retrieve_submission_file(submission.submission_id)
                except (LookupError, FileNotFoundError) as e:
                    flash(str(e), "error")
                    return self.render("admin/reingest.html", form=form)

                file_response = requests.get(presigned_url)
                file_storage = FileStorage(
                    BytesIO(file_response.content),
                    file_response.headers["x-amz-meta-filename"],
                    file_response.headers["x-amz-meta-filename"],
                    file_response.headers["content-type"],
                    int(file_response.headers["content-length"]),
                )
                fund_name = (
                    "Pathfinders"
                    if submission.programme_junction.programme_ref.fund.fund_code == "PF"
                    else "Towns Fund"
                )
                reporting_round = submission.programme_junction.reporting_round
                account_id, user_email = submission.submitting_account_id, submission.submitting_user_email
                db.session.close()  # ingest (specifically `populate_db`) wants to start a new clean session/transaction

                response_data, status_code = ingest(
                    excel_file=file_storage,
                    fund_name=fund_name,
                    reporting_round=reporting_round,
                    do_load=True,
                    submitting_account_id=account_id,
                    submitting_user_email=user_email,
                    auth=None,  # Don't run any auth checks because we're admins
                )
                if status_code == 200:
                    current_app.logger.warning(
                        "Submission ID %s reingested by %s", form.submission_id.data, g.user.email
                    )
                    flash(f"Successfully re-ingested submission {submission.submission_id}", "success")
                else:
                    flash(f"Issues re-ingesting submission {submission.submission_id}: {response_data}", "error")

                return redirect(url_for("reingest.index"))

            flash_errors(form, "%(error)s")

        return self.render("admin/reingest.html", form=form)


class RetrieveSubmissionAdminView(BaseAdminView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = RetrieveSubmissionAdminForm(request.form)

        if form.is_submitted():
            if form.validate():
                submission_id = form.submission_id.data
                try:
                    Submission.query.filter_by(submission_id=submission_id).one()
                except NoResultFound as e:
                    flash(str(e), "error")
                    return self.render("admin/retrieve_submission.html", form=form)

                try:
                    presigned_url = retrieve_submission_file(submission_id)
                except (LookupError, FileNotFoundError) as e:
                    flash(str(e), "error")
                    return self.render("admin/retrieve_submission.html", form=form)

                current_app.logger.warning("Submission ID %s downloaded by %s", form.submission_id.data, g.user.email)
                return redirect(presigned_url)

            flash_errors(form, "%(error)s")

        return self.render("admin/retrieve_submission.html", form=form)


class RetrieveFailedSubmissionAdminView(BaseAdminView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = RetrieveFailedSubmissionAdminForm(request.form)

        if form.is_submitted():
            if form.validate():
                failure_uuid = form.failure_uuid.data
                try:
                    presigned_url = get_failed_submission(failure_uuid)
                except (ValueError, FileNotFoundError) as e:
                    flash(str(e), "error")
                    return self.render("admin/retrieve_failed_submission.html", form=form)

                return redirect(presigned_url)

            flash_errors(form, "%(error)s")

        return self.render("admin/retrieve_failed_submission.html", form=form)
