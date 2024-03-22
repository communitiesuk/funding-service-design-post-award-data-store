from datetime import datetime
from typing import Type

from sqlalchemy import UUID, Integer, Select, and_, case, desc, func, or_, select
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

    Conditionally apply a filter on OutcomeDim category field

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
                ents.ProgrammeJunction.id == ents.OutcomeData.programme_junction_id,
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

    Additional tables can be added using the .join method inside the base_query variable,
    for example .join(ents.AdditionalTable). Filter conditions can be added and removed in the same place.

    If param filters are set to all (i.e. empty) then corresponding condition is ignored (passed as True).

    :param min_rp_start: Minimum Reporting Period Start to filter by
    :param max_rp_end: Maximum Reporting Period End to filter by
    :param organisation_uuids: Organisations to filter by
    :param fund_type_ids: Fund Types to filter by
    :param itl_regions: ITL Regions to filter by
    :return: SQLAlchemy query (to extend as required).
    """
    all_regions_passed = itl_regions == {region for region in ITLRegion}
    itl_rows = filter_on_regions(itl_regions) if itl_regions and not all_regions_passed else []

    project_region_condition = ents.Project.id.in_(itl_rows) if itl_rows else True
    submission_period_condition = set_submission_period_condition(min_rp_start, max_rp_end)
    programme_fund_condition = ents.Programme.fund_type_id.in_(fund_type_ids) if fund_type_ids else True
    organisation_name_condition = ents.Organisation.id.in_(organisation_uuids) if organisation_uuids else True

    base_query = (
        ents.Submission.query.join(ents.ProgrammeJunction)
        .join(ents.Programme)
        .join(ents.Organisation)
        .join(ents.Project)
        .filter(project_region_condition)
        .filter(submission_period_condition)
        .filter(programme_fund_condition)
        .filter(organisation_name_condition)
    )

    return base_query


def funding_query(base_query: Query) -> Query:
    """
    Extend base query to select specified columns for Funding.

    Joins to Funding model table (not included in base query joins). Joined or either project_id OR programme_id.
    Creates and passes conditional statements to query, to show corresponding project_id, programme_id, project_name
    programme_name, if and only if there is a corresponding record directly in Funding (not in the join to
    Project or Programme model). These are labelled to allow the serialiser to read them as a model field in the case
    of returning None.

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :return: updated query.
    """
    conditional_expression_project_id = case((ents.Funding.project_id.is_(None), None), else_=ents.Project.project_id)
    conditional_expression_project_name = case(
        (ents.Funding.project_id.is_(None), None), else_=ents.Project.project_name
    )
    conditional_expression_programme_id = case(
        (ents.Funding.programme_junction_id.is_(None), None), else_=ents.Programme.programme_id
    )
    conditional_expression_programme_name = case(
        (ents.Funding.programme_junction_id.is_(None), None), else_=ents.Programme.programme_name
    )

    extended_query = (
        base_query.join(
            ents.Funding,
            or_(
                ents.Project.id == ents.Funding.project_id,
                ents.ProgrammeJunction.id == ents.Funding.programme_junction_id,
            ),
        )
        .with_entities(
            ents.Submission.submission_id,
            conditional_expression_programme_id.label("programme_id"),
            conditional_expression_project_id.label("project_id"),
            ents.Funding.data_blob,
            ents.Funding.start_date,
            ents.Funding.end_date,
            conditional_expression_project_name.label("project_name"),
            conditional_expression_programme_name.label("programme_name"),
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
            ents.FundingComment.data_blob,
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
        base_query.join(ents.FundingQuestion, ents.FundingQuestion.programme_junction_id == ents.ProgrammeJunction.id)
        .with_entities(
            ents.Submission.submission_id,
            ents.Programme.programme_id,
            ents.FundingQuestion.data_blob,
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
        ((ents.OutcomeData.project_id.is_(None) & ents.OutcomeData.programme_junction_id.is_(None)), None),
        else_=ents.Submission.submission_id,
    )
    conditional_expression_project_id = case(
        (ents.OutcomeData.project_id.is_(None), None), else_=ents.Project.project_id
    )
    conditional_expression_project_name = case(
        (ents.OutcomeData.project_id.is_(None), None), else_=ents.Project.project_name
    )
    conditional_expression_programme_id = case(
        (ents.OutcomeData.programme_junction_id.is_(None), None), else_=ents.Programme.programme_id
    )
    conditional_expression_programme_name = case(
        (ents.OutcomeData.programme_junction_id.is_(None), None), else_=ents.Programme.programme_name
    )
    conditional_expression_organisation = case(
        ((ents.OutcomeData.project_id.is_(None) & ents.OutcomeData.programme_junction_id.is_(None)), None),
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
        ents.OutcomeData.data_blob,
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

    Joins to OutputData model table (not included in base query joins). Joined or either project_id OR programme_id.
    Creates and passes conditional statements to query, to show corresponding project_id, programme_id, project_name
    programme_name, if and only if there is a corresponding record directly in OutputData (not in the join to
    Project or Programme model). These are labelled to allow the serialiser to read them as a model field in the case
    of returning None.

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :return: updated query.
    """
    conditional_expression_project_id = case(
        (ents.OutputData.project_id.is_(None), None), else_=ents.Project.project_id
    )
    conditional_expression_project_name = case(
        (ents.OutputData.project_id.is_(None), None), else_=ents.Project.project_name
    )
    conditional_expression_programme_id = case(
        (ents.OutputData.programme_junction_id.is_(None), None), else_=ents.Programme.programme_id
    )
    conditional_expression_programme_name = case(
        (ents.OutputData.programme_junction_id.is_(None), None), else_=ents.Programme.programme_name
    )

    extended_query = (
        base_query.join(
            ents.OutputData,
            or_(
                ents.Project.id == ents.OutputData.project_id,
                ents.ProgrammeJunction.id == ents.OutputData.programme_junction_id,
            ),
        )
        .join(ents.OutputDim)
        .with_entities(
            ents.Submission.submission_id,
            conditional_expression_programme_id.label("programme_id"),
            conditional_expression_project_id.label("project_id"),
            ents.OutputData.start_date,
            ents.OutputData.end_date,
            ents.OutputDim.output_name,
            ents.OutputData.data_blob,
            conditional_expression_project_name.label("project_name"),
            conditional_expression_programme_name.label("programme_name"),
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
        base_query.join(
            ents.PlaceDetail, ents.PlaceDetail.programme_junction_id == ents.ProgrammeJunction.id
        ).with_entities(
            ents.PlaceDetail.data_blob,
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
            ents.PrivateInvestment.data_blob,
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
        base_query.join(
            ents.ProgrammeProgress, ents.ProgrammeProgress.programme_junction_id == ents.ProgrammeJunction.id
        )
        .with_entities(
            ents.Submission.submission_id,
            ents.Programme.programme_id,
            ents.ProgrammeProgress.data_blob,
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
        ents.Project.data_blob,
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
            ents.ProjectProgress.data_blob,
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
        (ents.RiskRegister.programme_junction_id.is_(None), None), else_=ents.Programme.programme_id
    )
    conditional_expression_programme_name = case(
        (ents.RiskRegister.programme_junction_id.is_(None), None), else_=ents.Programme.programme_name
    )

    extended_query = (
        base_query.join(
            ents.RiskRegister,
            or_(
                ents.Project.id == ents.RiskRegister.project_id,
                ents.ProgrammeJunction.id == ents.RiskRegister.programme_junction_id,
            ),
        )
        .with_entities(
            ents.Submission.submission_id,
            conditional_expression_programme_id.label("programme_id"),
            conditional_expression_project_id.label("project_id"),
            ents.RiskRegister.data_blob,
            conditional_expression_project_name.label("project_name"),
            conditional_expression_programme_name.label("programme_name"),
            ents.Organisation.organisation_name,
        )
        .distinct()
    )

    return extended_query


def project_finance_change_query(base_query: Query) -> Query:
    """
    Extend base query to select specified columns for ProjectFinanceChange.

    Joins to ProjectFinanceChange model table (not included in base query joins)

    :param base_query: SQLAlchemy Query of core tables with filters applied.
    :return: updated query.
    """
    extended_query = (
        base_query.join(
            ents.ProjectFinanceChange, ents.ProjectFinanceChange.programme_junction_id == ents.ProgrammeJunction.id
        )
        .with_entities(
            ents.Submission.submission_id,
            ents.Programme.programme_id,
            ents.ProjectFinanceChange.data_blob,
            ents.Programme.programme_name,
            ents.Organisation.organisation_name,
        )
        .distinct()
    )

    return extended_query


def submission_metadata_query(base_query: Query) -> Query:
    return base_query.with_entities(
        ents.Submission.submission_id,
        ents.Programme.programme_id,
        ents.Submission.reporting_period_start,
        ents.Submission.reporting_period_end,
        ents.Submission.reporting_round,
    ).distinct()


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


def get_project_id_fk(human_readable_project_id: str, current_submission_id: str):
    """Returns project id based on the human-readable id and the current submission id.

    :param human_readable_project_id: the human-readable project id, e.g. 'HR-WRC-01'
    :param current_submission_id: the submission id of the current submission being ingested
    :return: a Select query
    """
    project = (
        ents.Project.query.join(ents.ProgrammeJunction)
        .filter(ents.Project.project_id == human_readable_project_id)
        .filter(ents.ProgrammeJunction.submission_id == current_submission_id)
        .first()
    )

    return project.id if project else None


def get_programme_by_id_and_round(programme_id: str, reporting_round: int) -> ents.Programme | None:
    """
    Retrieves a programme based on the provided programme_id and reporting_round.

    :param programme_id: The ID of the programme.
    :param reporting_round: The reporting round.
    :return: The Programme object if found, otherwise None.
    """
    programme_exists_same_round = (
        ents.Programme.query.join(ents.ProgrammeJunction)
        .join(ents.Submission)
        .filter(ents.Programme.programme_id == programme_id)
        .filter(ents.Submission.reporting_round == reporting_round)
        .first()
    )
    return programme_exists_same_round


def get_programme_by_id_and_previous_round(programme_id: str, reporting_round: int) -> ents.Programme | None:
    """
    Retrieves a programme based on the provided programme_id and reporting_round,
    including programmes from previous reporting rounds.

    :param programme_id: The ID of the programme.
    :param reporting_round: The reporting round.
    :return: The Programme object if found, otherwise None.
    """
    programme_exists_previous_round = (
        ents.Programme.query.join(ents.ProgrammeJunction)
        .join(ents.Submission)
        .filter(ents.Programme.programme_id == programme_id)
        .filter(ents.Submission.reporting_round <= reporting_round)
        .first()
    )
    return programme_exists_previous_round


def get_organisation_exists(organisation_name: str) -> ents.Organisation | None:
    """Queries database based on organisation_name to see if corresponding Organisation object in database.

    :param organisation_name: a string representing the organisation_name field
    :return: the Organisation object for the matching name, or None
    """
    return ents.Organisation.query.filter(ents.Organisation.organisation_name == organisation_name).first()


def get_latest_submission_by_round_and_fund(reporting_round: int, fund_id: str) -> ents.Submission:
    """Get the latest submission id for a given reporting round and fund.

    Different fund ids have differing lengths, and so require a different substring to order by.

    HS and TD belong to TF submissions, and so require retrieval of the same incremention of submission ids.

    :param reporting_round: integer representing the reporting round.
    :param fund_id: the two-letter code representing the fund.
    :return: a Submission object.
    """

    # TODO: https://dluhcdigital.atlassian.net/jira/software/c/projects/FMD/boards/139/backlog?selectedIssue=FMD-258
    id_character_offset = {
        "TD": 7,
        "HS": 7,
        "PF": 10,
    }

    fund_types = ["TD", "HS"] if fund_id in ["TD", "HS"] else [fund_id]

    latest_submission_id = (
        ents.Submission.query.join(ents.ProgrammeJunction)
        .join(ents.Programme)
        .filter(ents.Submission.reporting_round == reporting_round)
        .filter(ents.Programme.fund_type_id.in_(fund_types))
        .order_by(desc(func.cast(func.substr(ents.Submission.submission_id, id_character_offset[fund_id]), Integer)))
        .first()
    )
    return latest_submission_id
