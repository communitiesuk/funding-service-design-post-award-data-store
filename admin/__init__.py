from admin.actions import ReingestAdminView
from admin.entities import (
    FundAdminView,
    GeospatialAdminView,
    OrganisationAdminView,
    OutcomeDimAdminView,
    OutputDimAdminView,
    SubmissionAdminView,
)


def register_admin_views(flask_admin, db):
    flask_admin.add_view(FundAdminView(db.session, category="Reference data"))
    flask_admin.add_view(GeospatialAdminView(db.session, category="Reference data"))
    flask_admin.add_view(OrganisationAdminView(db.session, category="Reference data"))
    flask_admin.add_view(OutcomeDimAdminView(db.session, category="Reference data"))
    flask_admin.add_view(OutputDimAdminView(db.session, category="Reference data"))

    flask_admin.add_view(SubmissionAdminView(db.session))

    flask_admin.add_view(ReingestAdminView(name="Reingest", endpoint="reingest"))
