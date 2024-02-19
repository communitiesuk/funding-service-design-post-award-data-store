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
    programme_progress_query,
    programme_query,
    project_progress_query,
    project_query,
    risk_register_query,
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
    project_id = auto_field(model=Project, data_key="ProjectID")
    comment = fields.String(attribute="event_data_blob.comment", data_key="Comment")
    project_name = auto_field(model=Project, data_key="ProjectName")
    programme_name = auto_field(model=Programme, data_key="Place")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")


class FundingQuestionSchema(SQLAlchemySchema):
    """Serialise FundingQuestion data"""

    class Meta:
        model = FundingQuestion

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    programme_id = auto_field(model=Programme, data_key="ProgrammeID")
    question = auto_field(data_key="Question")
    indicator = auto_field(data_key="Indicator")
    response = auto_field(data_key="Answer")
    guidance_notes = auto_field(data_key="GuidanceNotes")
    programme_name = auto_field(model=Programme, data_key="Place")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")


class FundingSchema(SQLAlchemySchema):
    """Serialise Funding data"""

    class Meta:
        model = Funding
        datetimeformat = "%d/%m/%Y"

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    project_id = auto_field(model=Project, data_key="ProjectID")
    funding_source_name = fields.String(attribute="event_data_blob.funding_source_name", data_key="FundingSourceName")
    funding_source_type = fields.String(attribute="event_data_blob.funding_source_type", data_key="FundingSourceType")
    secured = fields.String(attribute="event_data_blob.secured", data_key="Secured")
    start_date = fields.Raw(data_key="StartDate")
    end_date = fields.Raw(data_key="EndDate")
    spend_for_reporting_period = fields.Number(
        attribute="event_data_blob.spend_for_reporting_period", data_key="SpendforReportingPeriod"
    )
    status = fields.String(attribute="event_data_blob.status", data_key="ActualOrForecast")
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
    start_date = fields.Raw(data_key="StartDate")
    end_date = fields.Raw(data_key="EndDate")
    outcome_name = auto_field(model=OutcomeDim, data_key="Outcome")
    unit_of_measurement = auto_field(data_key="UnitofMeasurement")
    geography_indicator = auto_field(data_key="GeographyIndicator")
    amount = auto_field(data_key="Amount")
    state = auto_field(data_key="ActualOrForecast")
    higher_frequency = auto_field(data_key="SpecifyIfYouAreAbleToProvideThisMetricAtAHigherFrequencyLevelThanAnnually")
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
    project_id = auto_field(model=Project, data_key="ProjectID")
    start_date = fields.Raw(data_key="FinancialPeriodStart")
    end_date = fields.Raw(data_key="FinancialPeriodEnd")
    output_name = auto_field(model=OutputDim, data_key="Output")
    unit_of_measurement = auto_field(data_key="UnitofMeasurement")
    state = auto_field(data_key="ActualOrForecast")
    amount = auto_field(data_key="Amount")
    additional_information = auto_field(data_key="AdditionalInformation")
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
    question = auto_field(data_key="Question")
    indicator = auto_field(data_key="Indicator")
    answer = auto_field(data_key="Answer")
    programme_name = auto_field(model=Programme, data_key="Place")


class PrivateInvestmentSchema(SQLAlchemySchema):
    """Serialise PrivateInvestment data."""

    class Meta:
        model = PrivateInvestment

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    project_id = auto_field(model=Project, data_key="ProjectID")
    total_project_value = fields.Number(attribute="event_data_blob.total_project_value", data_key="TotalProjectValue")
    townsfund_funding = fields.Number(attribute="event_data_blob.townsfund_funding", data_key="TownsfundFunding")
    private_sector_funding_required = fields.Number(
        attribute="event_data_blob.private_sector_funding_required", data_key="PrivateSectorFundingRequired"
    )
    private_sector_funding_secured = fields.Number(
        attribute="event_data_blob.private_sector_funding_secured", data_key="PrivateSectorFundingSecured"
    )
    additional_comments = fields.String(
        attribute="event_data_blob.additional_comments", data_key="PSIAdditionalComments"
    )
    project_name = auto_field(model=Project, data_key="ProjectName")
    programme_name = auto_field(model=Programme, data_key="Place")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")


class ProgrammeProgressSchema(SQLAlchemySchema):
    """Serialise ProgrammeProgress data"""

    class Meta:
        model = ProgrammeProgress

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    programme_id = auto_field(model=Programme, data_key="ProgrammeID")
    question = auto_field(data_key="Question")
    answer = auto_field(data_key="Answer")
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


class ProjectSchema(SQLAlchemySchema):
    """Serialise Project data."""

    class Meta:
        model = Project

    submission_id = auto_field(model=Submission, data_key="SubmissionID")
    project_id = auto_field(data_key="ProjectID")
    primary_intervention_theme = auto_field(data_key="PrimaryInterventionTheme")
    location_multiplicity = auto_field(data_key="SingleorMultipleLocations")
    locations = auto_field(data_key="Locations")
    gis_provided = auto_field(data_key="AreYouProvidingAGISMapWithYourReturn")
    lat_long = auto_field(data_key="LatLongCoordinates")
    postcodes = PostcodeList(data_key="ExtractedPostcodes")
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
    start_date = fields.Raw(data_key="StartDate")
    end_date = fields.Raw(data_key="CompletionDate")
    adjustment_request_status = fields.String(
        attribute="event_data_blob.adjustment_request_status", data_key="ProjectAdjustmentRequestStatus"
    )
    delivery_status = fields.String(attribute="event_data_blob.delivery_status", data_key="ProjectDeliveryStatus")
    leading_factor_of_delay = fields.String(
        attribute="event_data_blob.leading_factor_of_delay", data_key="LeadingFactorOfDelay", dump_default=""
    )
    delivery_stage = fields.String(
        attribute="event_data_blob.delivery_stage", data_key="CurrentProjectDeliveryStage", dump_default=""
    )
    delivery_rag = fields.String(attribute="event_data_blob.delivery_rag", data_key="Delivery(RAG)")
    spend_rag = fields.String(attribute="event_data_blob.spend_rag", data_key="Spend(RAG)")
    risk_rag = fields.String(attribute="event_data_blob.risk_rag", data_key="Risk(RAG)")
    commentary = fields.String(attribute="event_data_blob.commentary", data_key="CommentaryonStatusandRAGRatings")
    important_milestone = fields.String(
        attribute="event_data_blob.important_milestone", data_key="MostImportantUpcomingCommsMilestone"
    )
    date_of_important_milestone = fields.Raw(data_key="DateofMostImportantUpcomingCommsMilestone")
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
    risk_name = auto_field(data_key="RiskName")
    risk_category = auto_field(data_key="RiskCategory")
    short_desc = auto_field(data_key="ShortDescription")
    full_desc = auto_field(data_key="FullDescription")
    consequences = auto_field(data_key="Consequences")
    pre_mitigated_impact = auto_field(data_key="PreMitigatedImpact")
    pre_mitigated_likelihood = auto_field(data_key="PreMitigatedLikelihood")
    mitigations = auto_field(data_key="Mitigations")
    post_mitigated_impact = auto_field(data_key="PostMitigatedImpact")
    post_mitigated_likelihood = auto_field(data_key="PostMitigatedLikelihood")
    proximity = auto_field(data_key="Proximity")
    risk_owner_role = auto_field(data_key="RiskOwnerRole")
    project_name = auto_field(model=Project, data_key="ProjectName")
    programme_name = auto_field(model=Programme, data_key="Place")
    organisation_name = auto_field(model=Organisation, data_key="OrganisationName")
