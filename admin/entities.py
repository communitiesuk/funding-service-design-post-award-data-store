from abc import abstractmethod

from flask import g
from flask_admin.contrib import sqla
from flask_admin.form import SecureForm
from fsd_utils.authentication.config import SupportedApp
from fsd_utils.authentication.decorators import login_required

from core.db.entities import Fund, GeospatialDim, Organisation, OutcomeDim, OutputDim, Submission


class BaseAdminView(sqla.ModelView):
    form_base_class = SecureForm

    can_set_page_size = True

    can_create = False
    can_view_details = True
    can_edit = False
    can_delete = False
    can_export = False

    def __init__(
        self,
        session,
        name=None,
        category=None,
        endpoint=None,
        url=None,
        static_folder=None,
        menu_class_name=None,
        menu_icon_type=None,
        menu_icon_value=None,
    ):
        super().__init__(
            self._model,
            session,
            name=name,
            category=category,
            endpoint=endpoint,
            url=url,
            static_folder=static_folder,
            menu_class_name=menu_class_name,
            menu_icon_type=menu_icon_type,
            menu_icon_value=menu_icon_value,
        )

    @property
    @abstractmethod
    def _model(self):
        pass

    def is_accessible(self):
        # We could use a microsoft AD group to control access to the admin pages
        @login_required(roles_required=["FSD_ADMIN"], return_app=SupportedApp.POST_AWARD_SUBMIT)
        def check_auth():
            return

        check_auth()

        return g.is_authenticated


class SubmissionAdminView(BaseAdminView):
    _model = Submission

    can_edit = False

    # This view is SQL-query heavy due to relationships, so let's restrict page size
    page_size = 25
    can_set_page_size = False  # lol this doesn't actually stop users setting their page size via url params

    column_list = [
        Submission.submission_id,
        "programme_junction.programme_ref.fund.fund_code",
        "programme_junction.reporting_round",
        Submission.submission_date,
        "programme_junction.programme_ref.programme_id",
        "programme_junction.programme_ref.organisation.organisation_name",
    ]
    column_labels = {
        "programme_junction.programme_ref.programme_id": "Programme ID",
        "programme_junction.programme_ref.organisation.organisation_name": "Organisation",
        "programme_junction.programme_ref.fund.fund_code": "Fund code",
        "programme_junction.reporting_round": "Reporting round",
    }
    column_sortable_list = [
        Submission.submission_id,
        "programme_junction.programme_ref.organisation.organisation_name",
        "programme_junction.reporting_round",
        Submission.submission_date,
    ]
    column_searchable_list = [Submission.id, Submission.submission_id]
    column_default_sort = [("programme_junction.reporting_round", True)]
    column_filters = [
        "programme_junction.reporting_round",
        "programme_junction.programme_ref.fund.fund_code",
        "programme_junction.programme_ref.programme_id",
        "programme_junction.programme_ref.organisation.organisation_name",
    ]


class OrganisationAdminView(BaseAdminView):
    _model = Organisation

    can_edit = True


class FundAdminView(BaseAdminView):
    _model = Fund


class GeospatialAdminView(BaseAdminView):
    _model = GeospatialDim

    column_default_sort = [(GeospatialDim.postcode_prefix, False)]


class OutputDimAdminView(BaseAdminView):
    _model = OutputDim

    can_create = True

    column_default_sort = [(OutputDim.output_category, False), (OutputDim.output_name, False)]
    column_searchable_list = [OutputDim.output_name]
    column_filters = [
        OutputDim.output_category,
    ]


class OutcomeDimAdminView(BaseAdminView):
    _model = OutcomeDim

    can_create = True

    column_default_sort = [(OutcomeDim.outcome_category, False), (OutcomeDim.outcome_name, False)]
    column_searchable_list = [OutcomeDim.outcome_name]
    column_filters = [
        OutcomeDim.outcome_category,
    ]
