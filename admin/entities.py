from abc import abstractmethod
from datetime import datetime

from flask import current_app, g
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla.typefmt import DEFAULT_FORMATTERS
from flask_wtf import FlaskForm

from admin.base import AdminAuthorizationMixin
from data_store.db.entities import Fund, GeospatialDim, Organisation, OutcomeDim, OutputDim, ReportingRound, Submission


class BaseAdminView(AdminAuthorizationMixin, sqla.ModelView):
    form_base_class = FlaskForm

    page_size = 50
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


class SubmissionAdminView(BaseAdminView):
    _model = Submission

    # This view is SQL-query heavy due to relationships, so let's restrict page size
    page_size = 25
    can_set_page_size = False

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


class FundAdminView(BaseAdminView):
    _model = Fund


class GeospatialAdminView(BaseAdminView):
    _model = GeospatialDim

    column_default_sort = [(GeospatialDim.postcode_prefix, False)]


class OutputDimAdminView(BaseAdminView):
    _model = OutputDim

    column_default_sort = [(OutputDim.output_category, False), (OutputDim.output_name, False)]
    column_searchable_list = [OutputDim.output_name]
    column_filters = [
        OutputDim.output_category,
    ]


class OutcomeDimAdminView(BaseAdminView):
    _model = OutcomeDim

    column_default_sort = [(OutcomeDim.outcome_category, False), (OutcomeDim.outcome_name, False)]
    column_searchable_list = [OutcomeDim.outcome_name]
    column_filters = [
        OutcomeDim.outcome_category,
    ]


class ReportingRoundAdminView(BaseAdminView):
    _model = ReportingRound

    can_create = True

    # Change how values are rendered in the table
    column_type_formatters = {
        **DEFAULT_FORMATTERS,
        Fund: lambda view, value, name: value.fund_code,
        datetime: lambda view, value, name: value.strftime("%d %b %Y, %H:%M:%S"),
    }
    column_type_formatters_detail = column_type_formatters

    # Hide these relationship fields when creating/viewing/editing
    form_excluded_columns = [
        "programme_junctions",
        "submissions",
    ]

    def after_model_change(self, form, model, is_created):
        verb = "created" if is_created else "updated"

        current_app.logger.warning(
            (
                "%s %s reporting round %s: "
                "fund=%s, round_number=%s, "
                "observation_period_start=%s, observation_period_end=%s, "
                "submission_period_start=%s, submission_period_end=%s"
            ),
            g.user.email,
            verb,
            model.id,
            model.fund.fund_code,
            model.round_number,
            model.observation_period_start,
            model.observation_period_end,
            model.submission_period_start,
            model.submission_period_end,
        )
