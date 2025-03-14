from abc import abstractmethod
from datetime import datetime

from flask import current_app, g, request
from flask_admin.babel import gettext
from flask_admin.base import expose
from flask_admin.contrib import sqla
from flask_admin.contrib.sqla.typefmt import DEFAULT_FORMATTERS
from flask_admin.form import DatePickerWidget
from flask_wtf import FlaskForm
from wtforms.fields.datetime import DateField

from admin.base import AdminAuthorizationMixin
from data_store.db.entities import (
    Fund,
    GeospatialDim,
    Organisation,
    OutcomeDim,
    OutputDim,
    ProjectProgress,
    ReportingRound,
    Submission,
)


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
        "programme_junction.reporting_round_entity.round_number",
        Submission.submission_date,
        "programme_junction.programme_ref.programme_id",
        "programme_junction.programme_ref.organisation.organisation_name",
    ]
    column_labels = {
        "programme_junction.programme_ref.programme_id": "Programme ID",
        "programme_junction.programme_ref.organisation.organisation_name": "Organisation",
        "programme_junction.programme_ref.fund.fund_code": "Fund code",
        "programme_junction.reporting_round_entity.round_number": "Reporting round",
    }
    column_sortable_list = [
        Submission.submission_id,
        "programme_junction.programme_ref.organisation.organisation_name",
        "programme_junction.reporting_round_entity.round_number",
        Submission.submission_date,
    ]
    column_searchable_list = [Submission.id, Submission.submission_id]
    column_default_sort = [("programme_junction.reporting_round_entity.round_number", True)]
    column_filters = [
        "programme_junction.reporting_round_entity.round_number",
        "programme_junction.programme_ref.fund.fund_code",
        "programme_junction.programme_ref.programme_id",
        "programme_junction.programme_ref.organisation.organisation_name",
    ]


class OrganisationAdminView(BaseAdminView):
    _model = Organisation
    can_edit = True
    fields_allowed_to_edit = ["external_reference_code"]
    edit_template = "admin/edit_organisation.html"

    column_list = [
        Organisation.organisation_name,
        Organisation.external_reference_code,
        Organisation.organisation_type,
    ]
    column_labels = {
        "external_reference_code": "External reference code",
        "organisation_type": "Organisation type",
    }
    column_sortable_list = [
        Organisation.organisation_name,
    ]
    column_searchable_list = [Organisation.organisation_name, Organisation.external_reference_code]
    column_default_sort = [("organisation_name", False)]
    form_excluded_columns = [
        "programmes",
        "organisation_name",
        "organisation_type",
    ]

    @expose("/edit/", methods=("GET", "POST"))
    def edit_view(self):
        if request.method == "GET":
            id = request.args.get("id")
            if id:
                instance = self.session.query(self.model).get(id)
                if instance:
                    self._template_args["organisation_name"] = instance.organisation_name

        return super(OrganisationAdminView, self).edit_view()

    def on_model_change(self, form, model, is_created):
        if not is_created:
            abort_edit = False
            for field in form.data:
                if field not in self.fields_allowed_to_edit and hasattr(model, field):
                    abort_edit = True
                    break
            if abort_edit:
                self.session.rollback()
                raise ValueError(gettext(f"{field} field can't be updated."))

        return super().on_model_change(form, model, is_created)


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


class DateTimeFieldWithHiddenTime(DateField):
    def __init__(self, label=None, validators=None, format="%Y-%m-%d", **kwargs):
        super().__init__(label, validators, format=format, **kwargs)

    def process_formdata(self, valuelist):
        if not valuelist:
            return

        date_str = " ".join(valuelist)
        for format in self.strptime_format:
            try:
                self.data = datetime.strptime(date_str, format)
                return
            except ValueError:
                self.data = None

        raise ValueError(self.gettext("Not a valid datetime value."))


class ReportingRoundAdminView(BaseAdminView):
    _model = ReportingRound

    can_create = True

    form_overrides = {
        "observation_period_start": DateTimeFieldWithHiddenTime,
        "observation_period_end": DateTimeFieldWithHiddenTime,
        "submission_period_start": DateTimeFieldWithHiddenTime,
        "submission_period_end": DateTimeFieldWithHiddenTime,
    }
    form_args = {
        "observation_period_start": {
            "widget": DatePickerWidget(),
            "description": "This period starts from midnight on the chosen date (00:00).",
        },
        "observation_period_end": {
            "widget": DatePickerWidget(),
            "description": "This period ends at midnight on the chosen date (23:59).",
        },
        "submission_period_start": {
            "widget": DatePickerWidget(),
            "description": "This period starts from midnight on the chosen date (00:00).",
        },
        "submission_period_end": {
            "widget": DatePickerWidget(),
            "description": "This period ends at midnight on the chosen date (23:59).",
        },
    }

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

    def on_model_change(self, form, model, is_created):
        model.observation_period_start = model.observation_period_start.replace(hour=0, minute=0, second=0)
        model.submission_period_start = model.submission_period_start.replace(hour=0, minute=0, second=0)

        model.observation_period_end = model.observation_period_end.replace(hour=23, minute=59, second=59)
        model.submission_period_end = model.submission_period_end.replace(hour=23, minute=59, second=59)

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


class ProjectProgressAdminView(BaseAdminView):
    _model = ProjectProgress

    column_list = [
        "project.programme_junction.programme_ref.programme_id",
        "project.programme_junction.submission.submission_id",
        "project.project_id",
        "start_date",
        "end_date",
        "data_blob",
    ]

    column_labels = {
        "project.programme_junction.programme_ref.programme_id": "Programme ID",
        "project.programme_junction.submission.submission_id": "Submission ID",
        "project.project_id": "Project ID",
    }

    column_filters = [
        "start_date",
        "end_date",
        "project.programme_junction.programme_ref.programme_id",
        "project.project_id",
        "project.programme_junction.submission.submission_id",
    ]
