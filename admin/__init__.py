from admin.actions import ReingestAdminView, RetrieveFailedSubmissionAdminView, RetrieveSubmissionAdminView
from admin.entities import (
    FundAdminView,
    GeospatialAdminView,
    OrganisationAdminView,
    OutcomeDimAdminView,
    OutputDimAdminView,
    ReportingRoundAdminView,
    SubmissionAdminView,
)


def register_admin_views(flask_admin, db):
    flask_admin.add_view(FundAdminView(db.session, category="Reference data"))
    flask_admin.add_view(GeospatialAdminView(db.session, category="Reference data"))
    flask_admin.add_view(OrganisationAdminView(db.session, category="Reference data"))
    flask_admin.add_view(OutcomeDimAdminView(db.session, category="Reference data"))
    flask_admin.add_view(OutputDimAdminView(db.session, category="Reference data"))

    flask_admin.add_view(SubmissionAdminView(db.session, category="Reporting data"))
    flask_admin.add_view(ReportingRoundAdminView(db.session, category="Reporting data"))

    flask_admin.add_view(ReingestAdminView(name="Reingest", endpoint="reingest", category="Admin actions"))
    flask_admin.add_view(
        RetrieveSubmissionAdminView(
            name="Retrieve Submission", endpoint="retrieve_submission", category="Admin actions"
        ),
    )
    flask_admin.add_view(
        RetrieveFailedSubmissionAdminView(
            name="Retrieve Failed Submission", endpoint="retrieve_failed_submission", category="Admin actions"
        )
    )