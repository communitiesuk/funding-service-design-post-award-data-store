from sqlalchemy import or_
from sqlalchemy.orm import joinedload

import core.db.entities as ents

# isort: off
from core.db.queries import get_programme_child_with_natural_keys_query, get_project_child_with_natural_keys_query

# isort: on

from core.util import ids


def serialize_download_data(programmes, programme_outcomes, projects, project_outcomes) -> dict[str, list[dict]]:
    """Top level serialization of the download data."""
    # Organisation level data
    organisation_refs = [OrganisationSerializer(programme.organisation).to_dict() for programme in programmes]

    # Programme level data
    programme_ids = ids(programmes)
    programme_refs = [ProgrammeSerializer(prog).to_dict() for prog in programmes]
    programme_progresses = get_programme_progress(programme_ids)
    place_details = get_place_details(programme_ids)
    funding_questions = get_funding_questions(programme_ids)
    programme_outcomes = [OutcomeDataSerializer(outcome_data).to_dict() for outcome_data in programme_outcomes]

    # Project level data
    project_ids = ids(projects)
    project_details = [ProjectSerializer(proj).to_dict() for proj in projects]
    project_progresses = get_project_progresses(project_ids)
    funding = get_funding(project_ids)
    funding_comments = get_funding_comments(project_ids)
    private_investments = get_private_investments(project_ids)
    outputs_ref = [OutputDimSerializer(output_dim).to_dict() for output_dim in ents.OutputDim.query.all()]
    output_data = get_outputs(project_ids)
    outcome_ref = [OutcomeDimSerializer(outcome_dim).to_dict() for outcome_dim in ents.OutcomeDim.query.all()]
    project_outcomes = [OutcomeDataSerializer(outcome_data).to_dict() for outcome_data in project_outcomes]

    risks = get_risks(programme_ids, project_ids)  # risks are combination of programme and project risks
    outcomes = [*programme_outcomes, *project_outcomes]  # outcomes are combination of programme and project outcomes

    # Provides sheet order for when outputted in Excel format.
    download_data = {
        "PlaceDetails": place_details,
        "ProjectDetails": project_details,
        "OrganisationRef": organisation_refs,
        "ProgrammeRef": programme_refs,
        "ProgrammeProgress": programme_progresses,
        "ProjectProgress": project_progresses,
        "FundingQuestions": funding_questions,
        "Funding": funding,
        "FundingComments": funding_comments,
        "PrivateInvestments": private_investments,
        "OutputsRef": outputs_ref,
        "OutputData": output_data,
        "OutcomeRef": outcome_ref,
        "OutcomeData": outcomes,
        "RiskRegister": risks,
    }
    return download_data


def get_programme_progress(programme_ids) -> list[dict[str, str]]:
    """Returns serialized ProgrammeProgress models related to provided programmes.

    :param programme_ids: IDs of selected programmes
    :return: programme progresses as dictionaries
    """
    programme_progress_models = get_programme_child_with_natural_keys_query(ents.ProgrammeProgress, programme_ids).all()
    output = [ProgrammeProgressSerializer(model).to_dict() for model in programme_progress_models]
    return output


def get_place_details(programme_ids) -> list[dict[str, str]]:
    """Returns serialized PlaceDetail models related to provided programmes.

    :param programme_ids: IDs of selected programmes
    :return: place details as dictionaries
    """
    place_detail_models = get_programme_child_with_natural_keys_query(ents.PlaceDetail, programme_ids).all()
    output = [PlaceDetailSerializer(model).to_dict() for model in place_detail_models]
    return output


def get_funding_questions(programme_ids) -> list[dict[str, str]]:
    """Returns serialized FundingQuestion models related to provided programmes.

    :param programme_ids: IDs of selected programmes
    :return: funding as dictionaries
    """
    funding_questions_models = get_programme_child_with_natural_keys_query(ents.FundingQuestion, programme_ids).all()
    output = [FundingQuestionSerializer(model).to_dict() for model in funding_questions_models]
    return output


def get_programme_risks(programme_ids) -> list[dict[str, str]]:
    """Returns serialized Risk models related to provided programmes.

    :param programme_ids: IDs of selected programmes
    :return: risks as dictionaries
    """
    programme_risks_models = ents.RiskRegister.query.filter(ents.RiskRegister.programme_id.in_(programme_ids)).options(
        joinedload(ents.RiskRegister.submission).load_only(ents.Submission.submission_id),
        joinedload(ents.RiskRegister.programme).load_only(ents.Programme.programme_id),
        joinedload(ents.RiskRegister.project).load_only(ents.Project.project_id),
    )
    output = [RiskRegisterSerializer(model).to_dict() for model in programme_risks_models]
    return output


def get_project_progresses(project_ids) -> list[dict[str, str]]:
    """Returns serialized ProjectProgress models related to provided projects.

    :param project_ids: IDs of selected projects
    :return: project progress as dictionaries
    """
    project_progress_models = get_project_child_with_natural_keys_query(ents.ProjectProgress, project_ids).all()
    output = [ProjectProgressSerializer(model).to_dict() for model in project_progress_models]
    return output


def get_funding(project_ids) -> list[dict[str, str]]:
    """Returns serialized Funding models related to provided projects.

    :param project_ids: IDs of selected projects
    :return: funding as dictionaries
    """
    funding_models = get_project_child_with_natural_keys_query(ents.Funding, project_ids).all()
    output = [FundingSerializer(model).to_dict() for model in funding_models]
    return output


def get_funding_comments(project_ids) -> list[dict[str, str]]:
    """Returns serialized FundingComment models related to provided projects.

    :param project_ids: IDs of selected projects
    :return: funding comments as dictionaries
    """
    funding_comment_models = get_project_child_with_natural_keys_query(ents.FundingComment, project_ids).all()
    output = [FundingCommentSerializer(model).to_dict() for model in funding_comment_models]
    return output


def get_private_investments(project_ids) -> list[dict[str, str]]:
    """Returns serialized PrivateInvestment models related to provided projects.

    :param project_ids: IDs of selected projects
    :return: private investment as dictionaries
    """
    private_investment_models = get_project_child_with_natural_keys_query(ents.PrivateInvestment, project_ids).all()
    output = [PrivateInvestmentSerializer(model).to_dict() for model in private_investment_models]
    return output


def get_outputs(project_ids) -> list[dict[str, str]]:
    """Returns serialized Output models related to provided projects.

    :param project_ids: IDs of selected projects
    :return: outputs as dictionaries
    """
    output_models = get_project_child_with_natural_keys_query(ents.OutputData, project_ids).all()
    output = [OutputDataSerializer(model).to_dict() for model in output_models]
    return output


def get_risks(programme_ids, project_ids) -> list[dict[str, str]]:
    """Returns serialized Risk models related to provided projects or programmes.

    :param programme_ids: IDs of selected programmes
    :param project_ids: IDs of selected projects
    :return: risks as dictionaries
    """
    project_risk_models = (
        ents.RiskRegister.query.filter(
            or_(ents.RiskRegister.programme_id.in_(programme_ids), ents.RiskRegister.project_id.in_(project_ids))
        )
        .options(
            joinedload(ents.RiskRegister.submission).load_only(ents.Submission.submission_id),
            joinedload(ents.RiskRegister.programme).load_only(ents.Programme.programme_id),
            joinedload(ents.RiskRegister.project).load_only(ents.Project.project_id),
        )
        .all()
    )
    output = [RiskRegisterSerializer(model).to_dict() for model in project_risk_models]
    return output


class OrganisationSerializer:
    def __init__(self, organisation: ents.Organisation):
        self.organisation = organisation

    def to_dict(self):
        return {
            "OrganisationID": str(self.organisation.id),
            "OrganisationName": self.organisation.organisation_name,
            "Geography": self.organisation.geography,
        }


class ProgrammeSerializer:
    def __init__(self, programme: ents.Programme):
        self.programme = programme

    def to_dict(self):
        return {
            "ProgrammeID": self.programme.programme_id,
            "ProgrammeName": self.programme.programme_name,
            "FundTypeID": self.programme.fund_type_id,
            "OrganisationID": str(self.programme.organisation_id),
        }


class ProgrammeProgressSerializer:
    def __init__(self, programme_progress: ents.ProgrammeProgress):
        self.programme_progress = programme_progress

    def to_dict(self):
        return {
            "SubmissionID": self.programme_progress.submission.submission_id,
            "ProgrammeID": self.programme_progress.programme.programme_id,
            "Question": self.programme_progress.question,
            "Answer": self.programme_progress.answer,
        }


class PlaceDetailSerializer:
    def __init__(self, place_detail: ents.PlaceDetail):
        self.place_detail = place_detail

    def to_dict(self):
        return {
            "SubmissionID": self.place_detail.submission.submission_id,
            "Question": self.place_detail.question,
            "Answer": self.place_detail.answer,
            "ProgrammeID": self.place_detail.programme.programme_id,
            "Indicator": self.place_detail.indicator,
        }


class FundingQuestionSerializer:
    def __init__(self, funding_question: ents.FundingQuestion):
        self.funding_question = funding_question

    def to_dict(self):
        return {
            "SubmissionID": self.funding_question.submission.submission_id,
            "ProgrammeID": self.funding_question.programme.programme_id,
            "Question": self.funding_question.question,
            "Indicator": self.funding_question.indicator,
            "Answer": self.funding_question.response,
            "GuidanceNotes": self.funding_question.guidance_notes,
        }


class ProjectSerializer:
    def __init__(self, project: ents.Project):
        self.project = project

    def to_dict(self):
        return {
            "SubmissionID": self.project.submission.submission_id,
            "ProgrammeID": self.project.programme.programme_id,
            "ProjectID": self.project.project_id,
            "ProjectName": self.project.project_name,
            "PrimaryInterventionTheme": self.project.primary_intervention_theme,
            "SingleorMultipleLocations": self.project.location_multiplicity,
            "Locations": self.project.locations,
            "AreYouProvidingAGISMapWithYourReturn": self.project.gis_provided,
            "LatLongCoordinates": self.project.lat_long,
        }


class ProjectProgressSerializer:
    def __init__(self, project_progress: ents.ProjectProgress):
        self.project_progress = project_progress

    def to_dict(self):
        return {
            "ProjectID": self.project_progress.project.project_id,
            "SubmissionID": self.project_progress.submission.submission_id,
            "StartDate": str(self.project_progress.start_date),
            "CompletionDate": str(self.project_progress.end_date),
            "ProjectAdjustmentRequestStatus": self.project_progress.adjustment_request_status,
            "ProjectDeliveryStatus": self.project_progress.delivery_status,
            "Delivery(RAG)": self.project_progress.delivery_rag,
            "Spend(RAG)": self.project_progress.spend_rag,
            "Risk(RAG)": self.project_progress.risk_rag,
            "CommentaryonStatusandRAGRatings": self.project_progress.commentary,
            "MostImportantUpcomingCommsMilestone": self.project_progress.important_milestone,
            "DateofMostImportantUpcomingCommsMilestone": str(self.project_progress.date_of_important_milestone),
        }


class FundingSerializer:
    def __init__(self, funding: ents.Funding):
        self.funding = funding

    def to_dict(self):
        return {
            "SubmissionID": self.funding.submission.submission_id,
            "ProjectID": self.funding.project.project_id,
            "FundingSourceName": self.funding.funding_source_name,
            "FundingSourceType": self.funding.funding_source_type,
            "Secured": self.funding.secured,
            "StartDate": str(self.funding.start_date),
            "EndDate": str(self.funding.end_date),
            "SpendforReportingPeriod": self.funding.spend_for_reporting_period,
            "ActualOrForecast": self.funding.status,
        }


class FundingCommentSerializer:
    def __init__(self, funding_comment: ents.FundingComment):
        self.funding_comment = funding_comment

    def to_dict(self):
        return {
            "SubmissionID": self.funding_comment.submission.submission_id,
            "ProjectID": self.funding_comment.project.project_id,
            "Comment": self.funding_comment.comment,
        }


class PrivateInvestmentSerializer:
    def __init__(self, private_investment: ents.PrivateInvestment):
        self.private_investment = private_investment

    def to_dict(self):
        return {
            "SubmissionID": self.private_investment.submission.submission_id,
            "ProjectID": self.private_investment.project.project_id,
            "TotalProjectValue": self.private_investment.total_project_value,
            "TownsfundFunding": self.private_investment.townsfund_funding,
            "PrivateSectorFundingRequired": self.private_investment.private_sector_funding_required,
            "PrivateSectorFundingSecured": self.private_investment.private_sector_funding_secured,
            "PSIAdditionalComments": self.private_investment.additional_comments,
        }


class OutputDataSerializer:
    def __init__(self, output_data: ents.OutputData):
        self.output_data = output_data

    def to_dict(self):
        return {
            "SubmissionID": self.output_data.submission.submission_id,
            "ProjectID": self.output_data.project.project_id,
            "FinancialPeriodStart": str(self.output_data.start_date),
            "FinancialPeriodEnd": str(self.output_data.end_date),
            "Output": self.output_data.output_dim.output_name,
            "UnitofMeasurement": self.output_data.unit_of_measurement,
            "ActualOrForecast": self.output_data.state,
            "Amount": self.output_data.amount,
            "AdditionalInformation": self.output_data.additional_information,
        }


class OutputDimSerializer:
    def __init__(self, output_dim: ents.OutputDim):
        self.output_dim = output_dim

    def to_dict(self):
        return {
            "OutputName": self.output_dim.output_name,
            "OutputCategory": self.output_dim.output_category,
        }


class OutcomeDataSerializer:
    def __init__(self, outcome_data: ents.OutcomeData):
        self.outcome_data = outcome_data

    def to_dict(self):
        return {
            "SubmissionID": self.outcome_data.submission.submission_id,
            "ProgrammeID": self.outcome_data.programme.programme_id if self.outcome_data.programme else None,
            "ProjectID": self.outcome_data.project.project_id if self.outcome_data.project else None,
            "StartDate": str(self.outcome_data.start_date),
            "EndDate": str(self.outcome_data.end_date),
            "Outcome": self.outcome_data.outcome_dim.outcome_name,
            "UnitofMeasurement": self.outcome_data.unit_of_measurement,
            "GeographyIndicator": self.outcome_data.geography_indicator,
            "Amount": self.outcome_data.amount,
            "ActualOrForecast": self.outcome_data.state,
            # fmt: off
            "SpecifyIfYouAreAbleToProvideThisMetricAtAHigherFrequencyLevelThanAnnually":
                self.outcome_data.higher_frequency,
            # fmt: on
        }


class OutcomeDimSerializer:
    def __init__(self, outcome_dim: ents.OutcomeDim):
        self.outcome_dim = outcome_dim

    def to_dict(self):
        return {
            "OutcomeName": self.outcome_dim.outcome_name,
            "OutcomeCategory": self.outcome_dim.outcome_category,
        }


class RiskRegisterSerializer:
    def __init__(self, risk_register: ents.RiskRegister):
        self.risk_register = risk_register

    def to_dict(self):
        return {
            "SubmissionID": self.risk_register.submission.submission_id,
            "ProgrammeID": self.risk_register.programme.programme_id if self.risk_register.programme else None,
            "ProjectID": self.risk_register.project.project_id if self.risk_register.project else None,
            "RiskName": self.risk_register.risk_name,
            "RiskCategory": self.risk_register.risk_category,
            "ShortDescription": self.risk_register.short_desc,
            "FullDescription": self.risk_register.full_desc,
            "Consequences": self.risk_register.consequences,
            "PreMitigatedImpact": self.risk_register.pre_mitigated_impact,
            "PreMitigatedLikelihood": self.risk_register.pre_mitigated_likelihood,
            "Mitigations": self.risk_register.mitigations,
            "PostMitigatedImpact": self.risk_register.post_mitigated_impact,
            "PostMitigatedLikelihood": self.risk_register.post_mitigated_likelihood,
            "Proximity": self.risk_register.proximity,
            "RiskOwnerRole": self.risk_register.risk_owner_role,
        }
