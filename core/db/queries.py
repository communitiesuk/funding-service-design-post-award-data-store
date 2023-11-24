from datetime import datetime
from typing import Type

from sqlalchemy import UUID, Select, and_, case, or_, select
from sqlalchemy.orm import Query

import core.db.entities as ents
from core.const import ITLRegion
from core.util import get_itl_regions_from_postcodes


def filter_on_regions(itl_regions: set[str]) -> list[UUID]:
    """
    Query DB and return all project UUIDs filtered on region filter params.

    :param itl_regions: List of ITL regions to filter on.
    :return: List of Project id's filtered on region params.
    """
    results = ents.Project.query.with_entities(ents.Project.id, ents.Project.postcodes).distinct().all()

    updated_results = [
        row[0] for row in results if row[1] and get_itl_regions_from_postcodes(row[1]).intersection(itl_regions)
    ]  # if row[1] is None, Python short-circuiting behaviour will not evaluate the second condition.
    return updated_results


def query_extend_with_outcome_filter(base_query: Query, outcome_categories: list[str] | None = None) -> Query:
    """
    Extend base query to include join to OutcomeDim / OutcomeData.

    Conditionally apply a filter on OutcomeDim catergory field

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :param outcome_categories: (optional) List of additional outcome_categories

    :return: updated query.
    """
    outcome_category_condition = (
        ents.OutcomeDim.outcome_category.in_(outcome_categories) if outcome_categories else True
    )

    extended_query = (
        base_query.join(
            ents.OutcomeData,
            or_(
                ents.Project.id == ents.OutcomeData.project_id,
                and_(
                    ents.Submission.id == ents.OutcomeData.submission_id,
                    ents.OutcomeData.project_id.is_(None),
                ),
            ),
        )
        .join(ents.OutcomeDim)
        .filter(outcome_category_condition)
    )

    return extended_query


def download_data_base_query(
    min_rp_start: datetime | None = None,
    max_rp_end: datetime | None = None,
    organisation_uuids: list[str] | None = None,
    fund_type_ids: list[str] | None = None,
    itl_regions: list[str] | None = None,
) -> Query:
    """
    Build a query to join and filter database tables according to parameters passed.

    If param filters are set to all (i.e. empty) then corresponding condition is ignored (passed as True).

    :param min_rp_start: Minimum Reporting Period Start to filter by
    :param max_rp_end: Maximum Reporting Period End to filter by
    :param organisation_uuids: Organisations to filter by
    :param fund_type_ids: Fund Types to filter by
    :param itl_regions: ITL Regions to filter by
    :param outcome_categories: Outcome Categories to filter by
    :return: SQLAlchemy query (to extend as required).
    """
    all_regions_passed = itl_regions == {region for region in ITLRegion}
    itl_rows = filter_on_regions(itl_regions) if itl_regions and not all_regions_passed else []

    project_region_condition = ents.Project.id.in_(itl_rows) if itl_rows else True
    submission_period_condition = set_submission_period_condition(min_rp_start, max_rp_end)
    programme_fund_condition = ents.Programme.fund_type_id.in_(fund_type_ids) if fund_type_ids else True
    organisation_name_condition = ents.Organisation.id.in_(organisation_uuids) if organisation_uuids else True

    base_query = (
        ents.Project.query.join(ents.Submission)
        .join(ents.Programme)
        .join(ents.Organisation)
        .filter(project_region_condition)
        .filter(submission_period_condition)
        .filter(programme_fund_condition)
        .filter(organisation_name_condition)
    )

    return base_query


def funding_query(base_query: Query) -> Query:
    """
    Extend base query to select specified columns for Funding.

    Joins to Funding model table (not included in base query joins)

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :return: updated query.
    """
    extended_query = (
        base_query.join(ents.Funding, ents.Funding.project_id == ents.Project.id)
        .with_entities(
            ents.Submission.submission_id,
            ents.Project.project_id,
            ents.Funding.funding_source_name,
            ents.Funding.funding_source_type,
            ents.Funding.secured,
            ents.Funding.start_date,
            ents.Funding.end_date,
            ents.Funding.spend_for_reporting_period,
            ents.Funding.status,
            ents.Project.project_name,
            ents.Programme.programme_name,
            ents.Organisation.organisation_name,
        )
        .distinct()
    )

    return extended_query


def funding_comment_query(base_query: Query) -> Query:
    """
    Extend base query to select specified columns for FundingComment.

    Joins to FundingComment model table (not included in base query joins)

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :return: updated query.
    """
    extended_query = (
        base_query.join(ents.FundingComment, ents.FundingComment.project_id == ents.Project.id)
        .with_entities(
            ents.Submission.submission_id,
            ents.Project.project_id,
            ents.FundingComment.comment,
            ents.Project.project_name,
            ents.Programme.programme_name,
            ents.Organisation.organisation_name,
        )
        .distinct()
    )

    return extended_query


def funding_question_query(base_query: Query) -> Query:
    """
    Extend base query to select specified columns for FundingQuestion.

    Joins to FundingQuestion model table (not included in base query joins)

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :return: updated query.
    """
    extended_query = (
        base_query.join(ents.FundingQuestion, ents.FundingQuestion.submission_id == ents.Submission.id)
        .with_entities(
            ents.Submission.submission_id,
            ents.Programme.programme_id,
            ents.FundingQuestion.question,
            ents.FundingQuestion.indicator,
            ents.FundingQuestion.response,
            ents.FundingQuestion.guidance_notes,
            ents.Programme.programme_name,
            ents.Organisation.organisation_name,
        )
        .distinct()
    )

    return extended_query


def organisation_query(base_query: Query) -> Query:
    """
    Extend base query to select specified columns for Organisation.

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :return: updated query.
    """

    extended_query = (
        base_query.with_entities(
            ents.Organisation.organisation_name,
            ents.Organisation.geography,
        )
    ).distinct()

    return extended_query


def outcome_data_query(base_query: Query, join_outcome_info=False) -> Query:
    """
    Extend base query to select specified columns for OutcomeData.

    Joins to OutcomeData and OutcomeDim model tables (not included in base query joins).

    Creates and passes conditional statements to query, to show corresponding fields obtained from joins with other
    tables, based on conditions. These are labelled to allow the serialiser to read them as a model field in the case
    of returning None.

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :param join_outcome_info: boolean of whether to join OutcomeData and OutcomeDim
    :return: updated query.
    """
    conditional_expression_submission = case(
        (((ents.OutcomeData.project_id.is_(None) & ents.OutcomeData.programme_id.is_(None)), None)),
        else_=ents.Submission.submission_id,
    )
    conditional_expression_project_id = case(
        (ents.OutcomeData.project_id.is_(None), None), else_=ents.Project.project_id
    )
    conditional_expression_project_name = case(
        (ents.OutcomeData.project_id.is_(None), None), else_=ents.Project.project_name
    )
    conditional_expression_programme_id = case(
        (ents.OutcomeData.programme_id.is_(None), None), else_=ents.Programme.programme_id
    )
    conditional_expression_programme_name = case(
        (ents.OutcomeData.programme_id.is_(None), None), else_=ents.Programme.programme_name
    )
    conditional_expression_organisation = case(
        (((ents.OutcomeData.project_id.is_(None) & ents.OutcomeData.programme_id.is_(None)), None)),
        else_=ents.Organisation.organisation_name,
    )

    if join_outcome_info:
        base_query = query_extend_with_outcome_filter(base_query)

    extended_query = base_query.with_entities(
        conditional_expression_submission.label("submission_id"),
        conditional_expression_programme_id.label("programme_id"),
        conditional_expression_project_id.label("project_id"),
        ents.OutcomeData.start_date,
        ents.OutcomeData.end_date,
        ents.OutcomeDim.outcome_name,
        ents.OutcomeData.unit_of_measurement,
        ents.OutcomeData.geography_indicator,
        ents.OutcomeData.amount,
        ents.OutcomeData.state,
        ents.OutcomeData.higher_frequency,
        conditional_expression_project_name.label("project_name"),
        conditional_expression_programme_name.label("programme_name"),
        conditional_expression_organisation.label("organisation_name"),
    ).distinct()

    return extended_query


def outcome_dim_query(base_query: Query, join_outcome_info=False) -> Query:
    """
    Extend base query to select specified columns for OutcomeDim.

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :param join_outcome_info: boolean of whether to join OutcomeData and OutcomeDim
    :return: updated query.
    """
    if join_outcome_info:
        base_query = query_extend_with_outcome_filter(base_query)

    extended_query = base_query.with_entities(
        ents.OutcomeDim.outcome_name,
        ents.OutcomeDim.outcome_category,
    ).distinct()

    return extended_query


def output_data_query(base_query: Query) -> Query:
    """
    Extend base query to select specified columns for OutputData.

    Joins to OutputData and OutputDim model tables (not included in base query joins)

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :return: updated query.
    """
    extended_query = (
        base_query.join(ents.OutputData, ents.OutputData.project_id == ents.Project.id)
        .join(ents.OutputDim)
        .with_entities(
            ents.Submission.submission_id,
            ents.Project.project_id,
            ents.OutputData.start_date,
            ents.OutputData.end_date,
            ents.OutputDim.output_name,
            ents.OutputData.unit_of_measurement,
            ents.OutputData.state,
            ents.OutputData.amount,
            ents.OutputData.additional_information,
            ents.Project.project_name,
            ents.Programme.programme_name,
            ents.Organisation.organisation_name,
        )
        .distinct()
    )

    return extended_query


def output_dim_query(base_query: Query) -> Query:
    """
    Extend base query to select specified columns for OutputDim.

    Joins to OutputDim model table via OutputData (not included in base query joins)

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :return: updated query.
    """
    extended_query = (
        base_query.join(ents.OutputData, ents.OutputData.project_id == ents.Project.id)
        .join(ents.OutputDim)
        .with_entities(
            ents.OutputDim.output_name,
            ents.OutputDim.output_category,
        )
        .distinct()
    )

    return extended_query


def place_detail_query(base_query: Query) -> Query:
    """
    Extend base query to select specified columns for PlaceDetail.

    Joins to PlaceDetail model table (not included in base query joins)

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :return: updated query.
    """
    extended_query = (
        base_query.join(ents.PlaceDetail, ents.PlaceDetail.submission_id == ents.Submission.id).with_entities(
            ents.PlaceDetail.question,
            ents.PlaceDetail.answer,
            ents.PlaceDetail.indicator,
            ents.Submission.submission_id,
            ents.Programme.programme_id,
            ents.Programme.programme_name,
            ents.Organisation.organisation_name,
        )
    ).distinct()

    return extended_query


def private_investment_query(base_query: Query) -> Query:
    """
    Extend base query to select specified columns for PrivateInvestment.

    Joins to PrivateInvestment model table (not included in base query joins)

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :return: updated query.
    """
    extended_query = (
        base_query.join(ents.PrivateInvestment, ents.PrivateInvestment.project_id == ents.Project.id).with_entities(
            ents.Submission.submission_id,
            ents.Project.project_id,
            ents.PrivateInvestment.total_project_value,
            ents.PrivateInvestment.townsfund_funding,
            ents.PrivateInvestment.private_sector_funding_required,
            ents.PrivateInvestment.private_sector_funding_secured,
            ents.PrivateInvestment.additional_comments,
            ents.Project.project_name,
            ents.Programme.programme_name,
            ents.Organisation.organisation_name,
        )
    ).distinct()

    return extended_query


def programme_query(base_query: Query) -> Query:
    """
    Extend base query to select specified columns for Programme.

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :return: updated query.
    """
    extended_query = base_query.with_entities(
        ents.Programme.programme_id,
        ents.Programme.programme_name,
        ents.Programme.fund_type_id,
        ents.Organisation.organisation_name,
    ).distinct()

    return extended_query


def programme_progress_query(base_query: Query) -> Query:
    """
    Extend base query to select specified columns for ProgrammeProgress.

    Joins to ProgrammeProgress model table (not included in base query joins)

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :return: updated query.
    """
    extended_query = (
        base_query.join(ents.ProgrammeProgress, ents.ProgrammeProgress.submission_id == ents.Submission.id)
        .with_entities(
            ents.Submission.submission_id,
            ents.Programme.programme_id,
            ents.ProgrammeProgress.question,
            ents.ProgrammeProgress.answer,
            ents.Programme.programme_name,
            ents.Organisation.organisation_name,
        )
        .distinct()
    )

    return extended_query


def project_query(base_query: Query) -> Query:
    """
    Extend base query to select specified columns for Project.

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :return: updated query.
    """
    extended_query = base_query.with_entities(
        ents.Submission.submission_id,
        ents.Project.project_id,
        ents.Project.primary_intervention_theme,
        ents.Project.location_multiplicity,
        ents.Project.locations,
        ents.Project.gis_provided,
        ents.Project.lat_long,
        ents.Project.postcodes,
        ents.Project.project_name,
        ents.Programme.programme_name,
        ents.Organisation.organisation_name,
    ).distinct()

    return extended_query


def project_progress_query(base_query: Query) -> Query:
    """
    Extend base query to select specified columns for ProjectProgress.

    Joins to ProjectProgress model table (not included in base query joins)

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :return: updated query.
    """
    extended_query = (
        base_query.join(ents.ProjectProgress, ents.ProjectProgress.project_id == ents.Project.id)
        .with_entities(
            ents.Submission.submission_id,
            ents.Project.project_id,
            ents.ProjectProgress.start_date,
            ents.ProjectProgress.end_date,
            ents.ProjectProgress.adjustment_request_status,
            ents.ProjectProgress.leading_factor_of_delay,
            ents.ProjectProgress.delivery_stage,
            ents.ProjectProgress.delivery_status,
            ents.ProjectProgress.delivery_rag,
            ents.ProjectProgress.spend_rag,
            ents.ProjectProgress.risk_rag,
            ents.ProjectProgress.commentary,
            ents.ProjectProgress.important_milestone,
            ents.ProjectProgress.date_of_important_milestone,
            ents.Project.project_name,
            ents.Programme.programme_name,
            ents.Organisation.organisation_name,
        )
        .distinct()
    )

    return extended_query


def risk_register_query(base_query: Query) -> Query:
    """
    Extend base query to select specified columns for RiskRegister.

    Joins to RiskRegister model table (not included in base query joins). Joined or either project_id OR programme_id.
    Creates and passes conditional statements to query, to show corresponding project_id, programme_id, project_name
    programme_name, if and only if there is a corresponding record directly in RiskRegister (not in the join to
    Project or Programme model). These are labelled to allow the serialiser to read them as a model field in the case
    of returning None.

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :return: updated query.
    """

    conditional_expression_project_id = case(
        (ents.RiskRegister.project_id.is_(None), None), else_=ents.Project.project_id
    )
    conditional_expression_project_name = case(
        (ents.RiskRegister.project_id.is_(None), None), else_=ents.Project.project_name
    )
    conditional_expression_programme_id = case(
        (ents.RiskRegister.programme_id.is_(None), None), else_=ents.Programme.programme_id
    )
    conditional_expression_programme_name = case(
        (ents.RiskRegister.programme_id.is_(None), None), else_=ents.Programme.programme_name
    )

    extended_query = (
        base_query.join(
            ents.RiskRegister,
            or_(
                ents.Project.id == ents.RiskRegister.project_id,
                and_(
                    ents.RiskRegister.submission_id == ents.Submission.id,
                    ents.RiskRegister.project_id.is_(None),
                ),
            ),
        )
        .with_entities(
            ents.Submission.submission_id,
            conditional_expression_programme_id.label("programme_id"),
            conditional_expression_project_id.label("project_id"),
            ents.RiskRegister.risk_name,
            ents.RiskRegister.risk_category,
            ents.RiskRegister.short_desc,
            ents.RiskRegister.full_desc,
            ents.RiskRegister.consequences,
            ents.RiskRegister.pre_mitigated_impact,
            ents.RiskRegister.pre_mitigated_likelihood,
            ents.RiskRegister.mitigations,
            ents.RiskRegister.post_mitigated_impact,
            ents.RiskRegister.post_mitigated_likelihood,
            ents.RiskRegister.proximity,
            ents.RiskRegister.risk_owner_role,
            conditional_expression_project_name.label("project_name"),
            conditional_expression_programme_name.label("programme_name"),
            ents.Organisation.organisation_name,
        )
        .distinct()
    )

    return extended_query


def set_submission_period_condition(min_rp_start: datetime | None, max_rp_end: datetime | None):
    """Set SQLAlchemy query condition for filtering on Submission date field entities.

    :param min_rp_start: Min reporting period start
    :param max_rp_end: Max reporting period end
    :return: sqlalchemy Query[QueryCondition]
    """

    conditions = []

    if min_rp_start:
        conditions.append(ents.Submission.reporting_period_start >= min_rp_start)
    if max_rp_end:
        conditions.append(ents.Submission.reporting_period_end <= max_rp_end)

    submission_period_condition = True if not conditions else and_(*conditions)
    return submission_period_condition


def generic_select_where_query(model: Type[ents.BaseModel], where_conditions) -> Select:
    """Returns a SELECT query with a set of WHERE conditions.

    :param model: an SQL Alchemy model
    :param where_conditions: a set of where conditions
    :return: a Select query
    """
    return select(model).where(*where_conditions)
