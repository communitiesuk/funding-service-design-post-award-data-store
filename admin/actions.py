from flask import flash, g, redirect, request, url_for
from flask_admin import BaseView, expose
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_required
from sqlalchemy.exc import NoResultFound
from werkzeug.datastructures import FileStorage

from admin.forms import ReingestAdminForm
from core.controllers.ingest import ingest
from core.controllers.retrieve_submission_file import retrieve_submission_file
from core.db import db
from core.db.entities import Submission


class BaseAdminView(BaseView):
    def is_accessible(self):
        # We could use a microsoft AD group to control access to the admin pages
        @login_required(roles_required=["FSD_ADMIN"], return_app=SupportedApp.POST_AWARD_ADMIN)
        def check_auth():
            return

        check_auth()

        return g.is_authenticated


class ReingestAdminView(BaseAdminView):
    @expose("/", methods=["GET", "POST"])
    def index(self):
        form = ReingestAdminForm(request.form)

        if request.method == "POST" and form.validate():
            try:
                submission = Submission.query.filter_by(submission_id=form.submission_id.data).one()
            except NoResultFound as e:
                flash(str(e), "error")
                return self.render("admin2/reingest.html", form=form)

            try:
                file, filename, content_type = retrieve_submission_file(submission.submission_id)
            except (LookupError, FileNotFoundError) as e:
                flash(str(e), "error")
                return self.render("admin2/reingest.html", form=form)

            file_storage = FileStorage(file, filename, filename, content_type, file.getbuffer().nbytes)
            fund_name = (
                "Pathfinders" if submission.programme_junction.programme_ref.fund.fund_code == "PF" else "Towns Fund"
            )
            reporting_round = submission.programme_junction.reporting_round
            account_id, user_email = submission.submitting_account_id, submission.submitting_user_email
            db.session.close()  # ingest (specifically `populate_db`) wants to start a new clean session/transaction

            response_data, status_code = ingest(
                dict(
                    fund_name=fund_name,
                    reporting_round=reporting_round,
                    auth=None,  # Don't run any auth checks because we're admins
                    do_load=True,
                    submitting_account_id=account_id,
                    submitting_user_email=user_email,
                ),
                file_storage,
            )
            if status_code == 200:
                flash(f"Successfully re-ingested submission {submission.submission_id}", "success")
            else:
                flash(f"Issues re-ingesting submission {submission.submission_id}: {response_data}", "error")

            return redirect(url_for("reingest.index"))

        return self.render("admin2/reingest.html", form=form)
