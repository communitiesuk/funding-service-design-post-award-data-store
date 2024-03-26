"""
Mappings to define serialiser outputs for DB models.

This project uses the Marshmallow library to define the serialization schema. Additional classes can be defined inside
this file, each inheriting the SQLAlchemySchema base class.

Each class defines the fields it serialises by directly importing attributes from DB model definitions in
core/db/entities.py via the auto_field method. Defining a model in the class Meta sets the default model for any
serialization class, but ones from other models (looked up via joins etc) can be explicitly defined as a KWARG to
auto_field when defining the attribute.

Each class should correspond to a table definition in core/db/entities.py, ensuring that the attribute name matches
the DB field name as defined in entities. The data_key argument is the corresponding field name that will be output
into the data extract, allowing for easy customization. The order of attributes defined in each class is the order
they will appear in any download, providing an easy way to control the output order.

"""

from typing import Generator

from marshmallow import fields
from marshmallow_sqlalchemy import SQLAlchemySchema, auto_field
from sqlalchemy.orm import Query
from sqlalchemy.sql import text

from core.db import db
from core.db.entities import (
    Funding,
    FundingComment,
    FundingQuestion,
    Organisation,
    OutcomeData,
    OutcomeDim,
    OutputData,
    OutputDim,
    PlaceDetail,
    PrivateInvestment,
    Programme,
    ProgrammeFundingManagement,
    ProgrammeProgress,
    Project,
    ProjectProgress,
    RiskRegister,
    Submission,
)
from core.db.queries import (
    funding_comment_query,
    funding_query,
    funding_question_query,
    organisation_query,
    outcome_data_query,
    outcome_dim_query,
    output_data_query,
    output_dim_query,
    place_detail_query,
    private_investment_query,
    programme_funding_management_query,
    programme_progress_query,
    programme_query,
    project_finance_change_query,
    project_progress_query,
    project_query,
    risk_register_query,
    submission_metadata_query,
)


class PostcodeList(fields.Field):
    """Used to convert between a postcode array (as stored in the DB) and a CSV string (as appears in json/excel)"""

    def _serialize(self, value, attr, obj, **kwargs):
        if value is None:
            return ""
        return ", ".join(value)


def serialise_download_data(
    base_query: Query,
    outcome_categories: list[str] | None = None,
    sheets_required: list[str] | None = None,
) -> Generator[tuple[str, list[dict]], None, None]:
    """
    Query and serialise data from multiple tables for download, each yielded individually.

    Extend base query to return relevant fields for each table, and serialise accordingly. Calls individual
    query methods and Marshmallow schema serialisers for each table, based on method names in table_queries dict.

    Each extended query and its corresponding schema should be added to the table_queries object in order to be
    serialised. Each additional query uses the base_query parameter as a starting point.

    :param base_query: An SQLAlchemy Query of core tables with filters applied.
    :param outcome_categories: Optional. List of outcome categories
    :param sheets_required: Optional. List of sheets to query/serialise/yield.
    :yield: A tuple containing table name and serialised data.
    """

    table_queries = {
        "PlaceDetails": (place_detail_query, PlaceDetailSchema),
        "ProjectDetails": (project_query, ProjectSchema),
        "OrganisationRef": (organisation_query, OrganisationSchema),
        "ProgrammeRef": (programme_query, ProgrammeSchema),
        "ProgrammeProgress": (programme_progress_query, ProgrammeProgressSchema),
        "ProjectProgress": (project_progress_query, ProjectProgressSchema),
        "FundingQuestions": (funding_question_query, FundingQuestionSchema),
        "Funding": (funding_query, FundingSchema),
        "FundingComments": (funding_comment_query, FundingCommentSchema),
        "PrivateInvestments": (private_investment_query, PrivateInvestmentSchema),
        "OutputRef": (output_dim_query, OutputDimSchema),
        "OutputData": (output_data_query, OutputDataSchema),
        "OutcomeRef": (outcome_dim_query, OutcomeDimSchema),
        "OutcomeData": (outcome_data_query, OutcomeDataSchema),
        "RiskRegister": (risk_register_query, RiskRegisterSchema),
        "ProjectFinanceChange": (project_finance_change_query, ProjectFinanceChangeSchema),
        "ProgrammeFundingManagement": (programme_funding_management_query, ProgrammeFundingManagementSchema),
        "SubmissionRef": (submission_metadata_query, SubmissionSchema),
    }

    sheets_required = sheets_required if sheets_required else list(table_queries.keys())

    for sheet in sheets_required:
        query_extender, schema = table_queries[sheet]

        # NOTE: We intentionally increase and then decrease this value on a per sheet basis
        #       rather than doing this at the beginning of the function and then RESETing at
        #       the end. At the moment we do this for every sheet but in the future might only
        #       increase it for the larger ones.
        db.session.execute(text("SET LOCAL work_mem TO '128MB'"))

        if not outcome_categories and sheet in ["OutcomeRef", "OutcomeData"]:
            extended_query = query_extender(base_query, join_outcome_info=True)
        else:
            extended_query = query_extender(base_query)

        table_data = extended_query.all()
        table_serialised = schema(many=True).dump(table_data)
        db.session.execute(text("RESET work_mem"))
        yield sheet, table_serialised


class FundingCommentSchema(SQLAlchemySchema):
    """Serialise FundingComment data"""

    class Meta:
        model = FundingComment

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    programme_id = auto_field(model=Programme, data_key="ProgrammeID")
    project_id = auto_field(model=Project, data_key="ProjectID")
    comment = fields.String(attribute="data_blob.comment", data_key="Comment")
    project_name = auto_field(model=Project, data_key="ProjectName")
    programme_name = auto_field(model=Programme, data_key="Place")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")


class FundingQuestionSchema(SQLAlchemySchema):
    """Serialise FundingQuestion data"""

    class Meta:
        model = FundingQuestion

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    programme_id = auto_field(model=Programme, data_key="ProgrammeID")
    question = fields.String(attribute="data_blob.question", data_key="Question", dump_default=None)
    indicator = fields.String(attribute="data_blob.indicator", data_key="Indicator", dump_default=None)
    response = fields.String(attribute="data_blob.response", data_key="Answer", dump_default=None)
    guidance_notes = fields.String(attribute="data_blob.guidance_notes", data_key="GuidanceNotes", dump_default=None)
    programme_name = auto_field(model=Programme, data_key="Place")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")


class FundingSchema(SQLAlchemySchema):
    """Serialise Funding data"""

    class Meta:
        model = Funding
        datetimeformat = "%d/%m/%Y"

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    programme_id = auto_field(model=Programme, data_key="ProgrammeID")
    project_id = auto_field(model=Project, data_key="ProjectID")
    funding_source_name = fields.String(
        attribute="data_blob.funding_source_name", data_key="FundingSourceName", dump_default=None
    )
    funding_source_type = fields.String(
        attribute="data_blob.funding_source_type", data_key="FundingSourceType", dump_default=None
    )
    secured = fields.String(attribute="data_blob.secured", data_key="Secured", dump_default=None)
    start_date = fields.Raw(data_key="StartDate", dump_default=None)
    end_date = fields.Raw(data_key="EndDate", dump_default=None)
    spend_for_reporting_period = fields.Number(
        attribute="data_blob.spend_for_reporting_period", data_key="SpendforReportingPeriod", dump_default=None
    )
    status = fields.String(attribute="data_blob.status", data_key="ActualOrForecast", dump_default=None)
    project_name = auto_field(model=Project, data_key="ProjectName")
    programme_name = auto_field(model=Programme, data_key="Place")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")


class OrganisationSchema(SQLAlchemySchema):
    """Serialise Organisation Reference data."""

    class Meta:
        model = Organisation

    organisation_name = auto_field(data_key="OrganisationName")
    geography = auto_field(data_key="Geography")


class OutcomeDataSchema(SQLAlchemySchema):
    """Serialise OutcomeData Reference data."""

    class Meta:
        model = OutcomeData
        datetimeformat = "%d/%m/%Y"

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    programme_id = auto_field(model=Programme, data_key="ProgrammeID")
    project_id = auto_field(model=Project, data_key="ProjectID")
    start_date = fields.Raw(data_key="StartDate", dump_default=None)
    end_date = fields.Raw(data_key="EndDate", dump_default=None)
    outcome_name = auto_field(model=OutcomeDim, data_key="Outcome")
    unit_of_measurement = fields.String(
        attribute="data_blob.unit_of_measurement", data_key="UnitofMeasurement", dump_default=None
    )
    geography_indicator = fields.String(
        attribute="data_blob.geography_indicator", data_key="GeographyIndicator", dump_default=None
    )
    amount = fields.Float(attribute="data_blob.amount", data_key="Amount", dump_default=None)
    state = fields.String(attribute="data_blob.state", data_key="ActualOrForecast", dump_default=None)
    higher_frequency = fields.String(
        attribute="data_blob.higher_frequency",
        data_key="SpecifyIfYouAreAbleToProvideThisMetricAtAHigherFrequencyLevelThanAnnually",
        dump_default=None,
    )
    project_name = auto_field(model=Project, data_key="ProjectName")
    programme_name = auto_field(model=Programme, data_key="Place")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")


class OutcomeDimSchema(SQLAlchemySchema):
    """Serialise OutcomeDim Reference data."""

    class Meta:
        model = OutcomeDim

    outcome_name = auto_field(data_key="OutcomeName")
    outcome_category = auto_field(data_key="OutcomeCategory")


class OutputDataSchema(SQLAlchemySchema):
    """Serialise OutputData Reference data."""

    class Meta:
        model = OutputData
        datetimeformat = "%d/%m/%Y"

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    programme_id = auto_field(model=Programme, data_key="ProgrammeID")
    project_id = auto_field(model=Project, data_key="ProjectID")
    start_date = fields.Raw(data_key="FinancialPeriodStart", dump_default=None)
    end_date = fields.Raw(data_key="FinancialPeriodEnd", dump_default=None)
    output_name = auto_field(model=OutputDim, data_key="Output", dump_default=None)
    unit_of_measurement = fields.String(
        attribute="data_blob.unit_of_measurement", data_key="UnitofMeasurement", dump_default=None
    )
    state = fields.String(attribute="data_blob.state", data_key="ActualOrForecast", dump_default=None)
    amount = fields.Float(attribute="data_blob.amount", data_key="Amount", dump_default=None)
    additional_information = fields.String(
        attribute="data_blob.additional_information", data_key="AdditionalInformation", dump_default=None
    )
    project_name = auto_field(model=Project, data_key="ProjectName")
    programme_name = auto_field(model=Programme, data_key="Place")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")


class OutputDimSchema(SQLAlchemySchema):
    """Serialise OutputDim Reference data."""

    class Meta:
        model = OutputDim

    output_name = auto_field(data_key="OutputName")
    output_category = auto_field(data_key="OutputCategory")


class PlaceDetailSchema(SQLAlchemySchema):
    """Serialise PlaceDetail data."""

    class Meta:
        model = PlaceDetail

    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")
    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    programme_id = auto_field(model=Programme, data_key="ProgrammeID")
    question = fields.String(attribute="data_blob.question", data_key="Question", dump_default=None)
    indicator = fields.String(attribute="data_blob.indicator", data_key="Indicator", dump_default=None)
    answer = fields.String(attribute="data_blob.answer", data_key="Answer", dump_default=None)
    programme_name = auto_field(model=Programme, data_key="Place")


class PrivateInvestmentSchema(SQLAlchemySchema):
    """Serialise PrivateInvestment data."""

    class Meta:
        model = PrivateInvestment

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    project_id = auto_field(model=Project, data_key="ProjectID")
    total_project_value = fields.Float(
        attribute="data_blob.total_project_value", data_key="TotalProjectValue", dump_default=None
    )
    townsfund_funding = fields.Float(
        attribute="data_blob.townsfund_funding", data_key="TownsfundFunding", dump_default=None
    )
    private_sector_funding_required = fields.Float(
        attribute="data_blob.private_sector_funding_required",
        data_key="PrivateSectorFundingRequired",
        dump_default=None,
    )
    private_sector_funding_secured = fields.Float(
        attribute="data_blob.private_sector_funding_secured", data_key="PrivateSectorFundingSecured", dump_default=None
    )
    additional_comments = fields.String(
        attribute="data_blob.additional_comments", data_key="PSIAdditionalComments", dump_default=None
    )
    project_name = auto_field(model=Project, data_key="ProjectName")
    programme_name = auto_field(model=Programme, data_key="Place")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")


class ProgrammeFundingManagementSchema(SQLAlchemySchema):
    """Serialise ProgrammeFundingManagement data"""

    class Meta:
        model = ProgrammeFundingManagement

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    programme_id = auto_field(model=Programme, data_key="ProgrammeID")
    payment_type = fields.String(attribute="data_blob.payment_type", data_key="PaymentType", dump_default=None)
    spend_for_reporting_period = fields.Float(
        attribute="data_blob.spend_for_reporting_period", data_key="SpendForReportingPeriod", dump_default=None
    )
    state = fields.String(attribute="data_blob.state", data_key="ActualOrForecast", dump_default=None)
    start_date = fields.Raw(data_key="StartDate", dump_default=None)
    end_date = fields.Raw(data_key="EndDate", dump_default=None)
    programme_name = auto_field(model=Programme, data_key="Place")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")


class ProgrammeProgressSchema(SQLAlchemySchema):
    """Serialise ProgrammeProgress data"""

    class Meta:
        model = ProgrammeProgress

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    programme_id = auto_field(model=Programme, data_key="ProgrammeID")
    question = fields.String(attribute="data_blob.question", data_key="Question", dump_default=None)
    answer = fields.String(attribute="data_blob.answer", data_key="Answer", dump_default=None)
    programme_name = auto_field(model=Programme, data_key="Place")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")


class ProgrammeSchema(SQLAlchemySchema):
    """Serialise Programme data."""

    class Meta:
        model = Programme

    programme_id = auto_field(data_key="ProgrammeID")
    programme_name = auto_field(data_key="ProgrammeName")
    fund_type_id = auto_field(data_key="FundTypeID")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")


class ProjectFinanceChangeSchema(SQLAlchemySchema):
    """Serialise ProjectFinanceChange data"""

    class Meta:
        model = FundingComment

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    programme_id = auto_field(model=Programme, data_key="ProgrammeID")
    change_number = fields.Integer(attribute="data_blob.change_number", data_key="ChangeNumber", dump_default=None)
    project_funding_moved_from = fields.String(
        attribute="data_blob.project_funding_moved_from", data_key="ProjectFundingMovedFrom", dump_default=None
    )
    intervention_theme_moved_from = fields.String(
        attribute="data_blob.intervention_theme_moved_from", data_key="InterventionThemeMovedFrom", dump_default=None
    )
    project_funding_moved_to = fields.String(
        attribute="data_blob.project_funding_moved_to", data_key="ProjectFundingMovedTo", dump_default=None
    )
    intervention_theme_moved_to = fields.String(
        attribute="data_blob.intervention_theme_moved_to", data_key="InterventionThemeMovedTo", dump_default=None
    )
    amount_moved = fields.Float(attribute="data_blob.amount_moved", data_key="AmountMoved", dump_default=None)
    changes_made = fields.String(attribute="data_blob.changes_made", data_key="ChangesMade", dump_default=None)
    reasons_for_change = fields.String(
        attribute="data_blob.reasons_for_change", data_key="ReasonsForChange", dump_default=None
    )
    forecast_or_actual_change = fields.String(
        attribute="data_blob.forecast_or_actual_change", data_key="ForecastOrActualChange", dump_default=None
    )
    reporting_period_change_takes_place = fields.String(
        attribute="data_blob.reporting_period_change_takes_place",
        data_key="ReportingPeriodChangeTakesPlace",
        dump_default=None,
    )
    programme_name = auto_field(model=Programme, data_key="Place")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")


class ProjectSchema(SQLAlchemySchema):
    """Serialise Project data."""

    class Meta:
        model = Project

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    project_id = auto_field(data_key="ProjectID")
    primary_intervention_theme = fields.String(
        attribute="data_blob.primary_intervention_theme", data_key="PrimaryInterventionTheme", dump_default=None
    )
    location_multiplicity = fields.String(
        attribute="data_blob.location_multiplicity", data_key="SingleorMultipleLocations", dump_default=None
    )
    locations = fields.String(attribute="data_blob.locations", data_key="Locations", dump_default=None)
    gis_provided = fields.String(
        attribute="data_blob.gis_provided", data_key="AreYouProvidingAGISMapWithYourReturn", dump_default=None
    )
    lat_long = fields.String(attribute="data_blob.lat_long", data_key="LatLongCoordinates", dump_default=None)
    postcodes = PostcodeList(data_key="ExtractedPostcodes", dump_default=None)
    project_name = auto_field(data_key="ProjectName")
    programme_name = auto_field(model=Programme, data_key="Place")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")


class ProjectProgressSchema(SQLAlchemySchema):
    """Serialise ProjectProgress data."""

    class Meta:
        model = ProjectProgress
        datetimeformat = "%d/%m/%Y"

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    project_id = auto_field(model=Project, data_key="ProjectID")
    start_date = fields.Raw(data_key="StartDate", dump_default=None)
    end_date = fields.Raw(data_key="CompletionDate", dump_default=None)
    adjustment_request_status = fields.String(
        attribute="data_blob.adjustment_request_status", data_key="ProjectAdjustmentRequestStatus", dump_default=None
    )
    delivery_status = fields.String(
        attribute="data_blob.delivery_status", data_key="ProjectDeliveryStatus", dump_default=None
    )
    leading_factor_of_delay = fields.String(
        attribute="data_blob.leading_factor_of_delay", data_key="LeadingFactorOfDelay", dump_default=None
    )
    delivery_stage = fields.String(
        attribute="data_blob.delivery_stage", data_key="CurrentProjectDeliveryStage", dump_default=None
    )
    delivery_rag = fields.String(attribute="data_blob.delivery_rag", data_key="Delivery(RAG)", dump_default=None)
    spend_rag = fields.String(attribute="data_blob.spend_rag", data_key="Spend(RAG)", dump_default=None)
    risk_rag = fields.String(attribute="data_blob.risk_rag", data_key="Risk(RAG)", dump_default=None)
    commentary = fields.String(
        attribute="data_blob.commentary", data_key="CommentaryonStatusandRAGRatings", dump_default=None
    )
    important_milestone = fields.String(
        attribute="data_blob.important_milestone", data_key="MostImportantUpcomingCommsMilestone", dump_default=None
    )
    date_of_important_milestone = fields.Raw(data_key="DateofMostImportantUpcomingCommsMilestone", dump_default=None)
    project_name = auto_field(model=Project, data_key="ProjectName")
    programme_name = auto_field(model=Programme, data_key="Place")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")


class RiskRegisterSchema(SQLAlchemySchema):
    """Serialise RiskRegister Reference data."""

    class Meta:
        model = RiskRegister
        datetimeformat = "%d/%m/%Y"

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    programme_id = auto_field(model=Programme, data_key="ProgrammeID")
    project_id = auto_field(model=Project, data_key="ProjectID")
    risk_name = fields.String(attribute="data_blob.risk_name", data_key="RiskName", dump_default=None)
    risk_category = fields.String(attribute="data_blob.risk_category", data_key="RiskCategory", dump_default=None)
    short_desc = fields.String(attribute="data_blob.short_desc", data_key="ShortDescription", dump_default=None)
    full_desc = fields.String(attribute="data_blob.full_desc", data_key="FullDescription", dump_default=None)
    consequences = fields.String(attribute="data_blob.consequences", data_key="Consequences", dump_default=None)
    pre_mitigated_impact = fields.String(
        attribute="data_blob.pre_mitigated_impact", data_key="PreMitigatedImpact", dump_default=None
    )
    pre_mitigated_likelihood = fields.String(
        attribute="data_blob.pre_mitigated_likelihood", data_key="PreMitigatedLikelihood", dump_default=None
    )
    mitigations = fields.String(attribute="data_blob.mitigations", data_key="Mitigations", dump_default=None)
    post_mitigated_impact = fields.String(
        attribute="data_blob.post_mitigated_impact", data_key="PostMitigatedImpact", dump_default=None
    )
    post_mitigated_likelihood = fields.String(
        attribute="data_blob.post_mitigated_likelihood", data_key="PostMitigatedLikelihood", dump_default=None
    )
    proximity = fields.String(attribute="data_blob.proximity", data_key="Proximity", dump_default=None)
    risk_owner_role = fields.String(attribute="data_blob.risk_owner_role", data_key="RiskOwnerRole", dump_default=None)
    project_name = auto_field(model=Project, data_key="ProjectName")
    programme_name = auto_field(model=Programme, data_key="Place")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")


class SubmissionSchema(SQLAlchemySchema):
    """Serialise Submission Reference data."""

    class Meta:
        model = Submission
        datetimeformat = "%d/%m/%Y"

    submission_id = auto_field(data_key="SubmissionID")
    programme_id = auto_field(model=Programme, data_key="ProgrammeID")
    reporting_period_start = fields.Raw(data_key="ReportingPeriodStart")
    reporting_period_end = fields.Raw(data_key="ReportingPeriodEnd")
    reporting_round = auto_field(data_key="ReportingRound")
