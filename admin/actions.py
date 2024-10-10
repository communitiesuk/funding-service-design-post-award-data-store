from io import BytesIO

import requests
from flask import current_app, flash, g, redirect, request, url_for
from flask_admin import BaseView, expose
from flask_admin.helpers import flash_errors
from sqlalchemy.exc import NoResultFound
from werkzeug.datastructures import CombinedMultiDict, FileStorage

from admin.base import AdminAuthorizationMixin
from admin.forms import (
    ReingestFromFileAdminForm,
    ReingestFromS3AdminForm,
    RetrieveFailedSubmissionAdminForm,
    RetrieveSubmissionAdminForm,
)
from data_store.controllers.failed_submission import get_failed_submission
from data_store.controllers.ingest import ingest
from data_store.controllers.retrieve_submission_file import retrieve_submission_file
from data_store.db import db
from data_store.db.entities import Submission


class BaseAdminView(AdminAuthorizationMixin, BaseView):
    pass


class ReingestFromS3AdminView(BaseAdminView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = ReingestFromS3AdminForm(request.form)

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

                return redirect(url_for("reingest_s3.index"))

            flash_errors(form, "%(error)s")

        return self.render("admin/reingest.html", form=form)


class ReingestFileAdminView(BaseAdminView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = ReingestFromFileAdminForm(CombinedMultiDict((request.files, request.form)))

        if form.is_submitted():
            if form.validate():
                submission_id = form.submission_id.data.upper()

                try:
                    with db.session.begin():
                        submission = Submission.query.filter_by(submission_id=submission_id).one()
                        original_id = submission.id

                        match submission.programme_junction.programme_ref.fund.fund_code:
                            case "PF":
                                fund_name = "Pathfinders"
                            case "TD" | "HS":
                                fund_name = "Towns Fund"
                            case fund_code:
                                raise ValueError(f"Unknown fund: {fund_code}")

                        reporting_round = submission.reporting_round.round_number
                        account_id, user_email = submission.submitting_account_id, submission.submitting_user_email

                    response_data, status_code = ingest(
                        excel_file=form.excel_file.data,
                        fund_name=fund_name,
                        reporting_round=reporting_round,
                        do_load=True,
                        submitting_account_id=account_id,
                        submitting_user_email=user_email,
                        auth=None,  # Don't run any auth checks because we're admins
                    )

                    submission = Submission.query.filter_by(submission_id=submission_id).one()  # re-fetch after changes
                    if status_code == 200:
                        current_app.logger.warning(
                            "Submission ID %s (original db id=%s, new db id=%s) reingested by %s from a local file",
                            submission_id,
                            original_id,
                            submission.id,
                            g.user.email,
                        )
                        flash(f"Successfully re-ingested submission {submission.submission_id}")

                    else:
                        flash(
                            f"Issues re-ingesting submission {submission.submission_id}: {status_code} {response_data}"
                        )

                    return redirect(url_for("reingest_file.index"))

                except NoResultFound:
                    flash(f"Could not find a matching submission with ID {submission_id}", "error")

            else:
                flash_errors(form, "%(error)s")

        return self.render("admin/reingest_file.html", form=form)


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
