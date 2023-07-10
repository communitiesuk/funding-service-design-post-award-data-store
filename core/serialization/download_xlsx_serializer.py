from sqlalchemy import or_
from sqlalchemy.orm import joinedload

import core.db.entities as ents

# isort: off
from core.db.queries import get_programme_child_with_natural_keys_query, get_project_child_with_natural_keys_query

# isort: on

from core.util import ids


def serialize_xlsx_data(programmes, programme_outcomes, projects, project_outcomes) -> dict[str, list[dict]]:
    """Top level serialization of the download data."""

    programme_ids = ids(programmes)

    # get mappings used to supplement (almost) every table with additional information
    organisation_mapping = get_organisation_mapping(programme_ids)
    programme_name_mapping = get_programme_name_mapping(programme_ids)

    # Organisation level data
    organisation_refs = [OrganisationSerializer(programme.organisation).to_dict() for programme in programmes]

    # Programme level data
    programme_refs = [
        ProgrammeSerializer(
            prog,
            programme_name_mapping[prog.programme_id],
            organisation_mapping[prog.programme_id],
        ).to_dict()
        for prog in programmes
    ]
    programme_progresses = get_programme_progress(programme_ids, programme_name_mapping, organisation_mapping)
    place_details = get_place_details(programme_ids, programme_name_mapping, organisation_mapping)
    funding_questions = get_funding_questions(programme_ids, programme_name_mapping, organisation_mapping)
    programme_outcomes = [
        OutcomeDataSerializer(
            outcome_data,
            programme_name_mapping[outcome_data.programme.programme_id],
            organisation_mapping[outcome_data.programme.programme_id],
        ).to_dict()
        for outcome_data in programme_outcomes
    ]

    # Project level data
    project_ids = ids(projects)
    project_details = get_project_details(projects, organisation_mapping, programme_name_mapping)
    project_progresses = get_project_progresses(project_ids, programme_name_mapping, organisation_mapping)
    funding = get_funding(project_ids, programme_name_mapping, organisation_mapping)
    funding_comments = get_funding_comments(project_ids, programme_name_mapping, organisation_mapping)
    private_investments = get_private_investments(project_ids, programme_name_mapping, organisation_mapping)
    outputs_ref = [OutputDimSerializer(output_dim).to_dict() for output_dim in ents.OutputDim.query.all()]
    output_data = get_outputs(project_ids, programme_name_mapping, organisation_mapping)
    outcome_ref = [OutcomeDimSerializer(outcome_dim).to_dict() for outcome_dim in ents.OutcomeDim.query.all()]
    project_outcomes = [
        OutcomeDataSerializer(
            outcome_data,
            programme_name_mapping[
                outcome_data.programme.programme_id if outcome_data.programme else outcome_data.project.project_id
            ],
            organisation_mapping[
                outcome_data.programme.programme_id if outcome_data.programme else outcome_data.project.project_id
            ],
        ).to_dict()
        for outcome_data in project_outcomes
    ]

    risks = get_risks(
        programme_ids, project_ids, programme_name_mapping, organisation_mapping
    )  # risks are combination of programme and project risks
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


def get_organisation_mapping(programme_ids):
    """Returns a mapping to an organisation name for all programmes and their child projects.

    :param programme_ids: programmes (which also provide child projects) to map from
    :return: project/programme to organisation mapping
    """
    organisations = {}

    programmes = (
        ents.Programme.query.filter(ents.Programme.id.in_(programme_ids))
        .options(
            joinedload(ents.Programme.organisation),  # preload org
            joinedload(ents.Programme.projects),  # preload child projects
        )
        .all()
    )

    for programme in programmes:
        # add the programme -> org mapping
        organisations[programme.programme_id] = programme.organisation.organisation_name

        # add the project -> org mapping for each child project of programme
        for project in programme.projects:
            organisations[project.project_id] = programme.organisation.organisation_name

    return organisations


def get_programme_name_mapping(programme_ids):
    """Returns a mapping to a programme name for all programmes and their child projects.

    :param programme_ids: programmes (which also provide child projects) to map from
    :return: project/programme to organisation mapping
    """
    places = {}
    programmes = (
        ents.Programme.query.filter(ents.Programme.id.in_(programme_ids))
        .options(
            joinedload(ents.Programme.projects),  # preload child projects
        )
        .all()
    )

    for programme in programmes:
        # add the programme -> programme name mapping
        places[programme.programme_id] = programme.programme_name

        # add the project -> programme name mapping for each child project of programme
        for project in programme.projects:
            places[project.project_id] = programme.programme_name

    return places


def get_project_details(projects, programme_name_mapping, organisation_mapping):
    """Returns serialized Project models related to provided programmes.

    :param projects: IDs of selected projects
    :param programme_name_mapping: place metadata to add to the serialized output
    :param organisation_mapping: organisation metadata to add to the serialized output
    :return: project details as dictionaries
    """
    project_details = [
        ProjectSerializer(
            proj, programme_name_mapping[proj.programme.programme_id], organisation_mapping[proj.programme.programme_id]
        ).to_dict()
        for proj in projects
    ]
    return project_details


def get_programme_progress(programme_ids, programme_name_mapping, organisation_mapping) -> list[dict[str, str]]:
    """Returns serialized ProgrammeProgress models related to provided programmes.

    :param programme_ids: IDs of selected programmes
    :param programme_name_mapping: place metadata to add to the serialized output
    :param organisation_mapping: organisation metadata to add to the serialized output
    :return: programme progresses as dictionaries
    """
    programme_progress_models = get_programme_child_with_natural_keys_query(ents.ProgrammeProgress, programme_ids).all()
    output = [
        ProgrammeProgressSerializer(
            model,
            programme_name_mapping[model.programme.programme_id],
            organisation_mapping[model.programme.programme_id],
        ).to_dict()
        for model in programme_progress_models
    ]
    return output


def get_place_details(programme_ids, programme_name_mapping, organisation_mapping) -> list[dict[str, str]]:
    """Returns serialized PlaceDetail models related to provided programmes.

    :param programme_ids: IDs of selected programmes
    :param programme_name_mapping: place metadata to add to the serialized output
    :param organisation_mapping: organisation metadata to add to the serialized output
    :return: place details as dictionaries
    """
    place_detail_models = get_programme_child_with_natural_keys_query(ents.PlaceDetail, programme_ids).all()
    output = [
        PlaceDetailSerializer(
            model,
            programme_name_mapping[model.programme.programme_id],
            organisation_mapping[model.programme.programme_id],
        ).to_dict()
        for model in place_detail_models
    ]
    return output


def get_funding_questions(programme_ids, programme_name_mapping, organisation_mapping) -> list[dict[str, str]]:
    """Returns serialized FundingQuestion models related to provided programmes.

    :param programme_ids: IDs of selected programmes
    :param programme_name_mapping: place metadata to add to the serialized output
    :param organisation_mapping: organisation metadata to add to the serialized output
    :return: funding as dictionaries
    """
    funding_questions_models = get_programme_child_with_natural_keys_query(ents.FundingQuestion, programme_ids).all()
    output = [
        FundingQuestionSerializer(
            model,
            programme_name_mapping[model.programme.programme_id],
            organisation_mapping[model.programme.programme_id],
        ).to_dict()
        for model in funding_questions_models
    ]
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


def get_project_progresses(project_ids, programme_name_mapping, organisation_mapping) -> list[dict[str, str]]:
    """Returns serialized ProjectProgress models related to provided projects.

    :param project_ids: IDs of selected projects
    :param programme_name_mapping: place metadata to add to the serialized output
    :param organisation_mapping: organisation metadata to add to the serialized output
    :return: project progress as dictionaries
    """
    project_progress_models = get_project_child_with_natural_keys_query(ents.ProjectProgress, project_ids).all()
    output = [
        ProjectProgressSerializer(
            model,
            programme_name_mapping[model.project.programme.programme_id],
            organisation_mapping[model.project.programme.programme_id],
        ).to_dict()
        for model in project_progress_models
    ]
    return output


def get_funding(project_ids, programme_name_mapping, organisation_mapping) -> list[dict[str, str]]:
    """Returns serialized Funding models related to provided projects.

    :param project_ids: IDs of selected projects
    :param programme_name_mapping: place metadata to add to the serialized output
    :param organisation_mapping: organisation metadata to add to the serialized output
    :return: funding as dictionaries
    """
    funding_models = get_project_child_with_natural_keys_query(ents.Funding, project_ids).all()
    output = [
        FundingSerializer(
            model,
            programme_name_mapping[model.project.programme.programme_id],
            organisation_mapping[model.project.programme.programme_id],
        ).to_dict()
        for model in funding_models
    ]
    return output


def get_funding_comments(project_ids, programme_name_mapping, organisation_mapping) -> list[dict[str, str]]:
    """Returns serialized FundingComment models related to provided projects.

    :param project_ids: IDs of selected projects
    :param programme_name_mapping: place metadata to add to the serialized output
    :param organisation_mapping: organisation metadata to add to the serialized output
    :return: funding comments as dictionaries
    """
    funding_comment_models = get_project_child_with_natural_keys_query(ents.FundingComment, project_ids).all()
    output = [
        FundingCommentSerializer(
            model,
            programme_name_mapping[model.project.programme.programme_id],
            organisation_mapping[model.project.programme.programme_id],
        ).to_dict()
        for model in funding_comment_models
    ]
    return output


def get_private_investments(project_ids, programme_name_mapping, organisation_mapping) -> list[dict[str, str]]:
    """Returns serialized PrivateInvestment models related to provided projects.

    :param project_ids: IDs of selected projects
    :param programme_name_mapping: place metadata to add to the serialized output
    :param organisation_mapping: organisation metadata to add to the serialized output
    :return: private investment as dictionaries
    """
    private_investment_models = get_project_child_with_natural_keys_query(ents.PrivateInvestment, project_ids).all()
    output = [
        PrivateInvestmentSerializer(
            model,
            programme_name_mapping[model.project.programme.programme_id],
            organisation_mapping[model.project.programme.programme_id],
        ).to_dict()
        for model in private_investment_models
    ]
    return output


def get_outputs(project_ids, programme_name_mapping, organisation_mapping) -> list[dict[str, str]]:
    """Returns serialized Output models related to provided projects.

    :param project_ids: IDs of selected projects
    :param programme_name_mapping: place metadata to add to the serialized output
    :param organisation_mapping: organisation metadata to add to the serialized output
    :return: outputs as dictionaries
    """
    output_models = get_project_child_with_natural_keys_query(ents.OutputData, project_ids).all()
    output = [
        OutputDataSerializer(
            model,
            programme_name_mapping[model.project.programme.programme_id],
            organisation_mapping[model.project.programme.programme_id],
        ).to_dict()
        for model in output_models
    ]
    return output


def get_risks(programme_ids, project_ids, programme_name_mapping, organisation_mapping) -> list[dict[str, str]]:
    """Returns serialized Risk models related to provided projects or programmes.

    :param programme_ids: IDs of selected programmes
    :param project_ids: IDs of selected projects
    :param programme_name_mapping: place metadata to add to the serialized output
    :param organisation_mapping: organisation metadata to add to the serialized output
    :return: risks as dictionaries
    """
    risk_models = (
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

    output = []
    for model in risk_models:
        if model.programme:
            # programme risks
            output.append(
                RiskRegisterSerializer(
                    model,
                    programme_name_mapping[model.programme.programme_id],
                    organisation_mapping[model.programme.programme_id],
                ).to_dict()
            )
        else:
            # project risks
            output.append(
                RiskRegisterSerializer(
                    model,
                    programme_name_mapping[model.project.project_id],
                    organisation_mapping[model.project.project_id],
                ).to_dict()
            )

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
    def __init__(self, programme: ents.Programme, programme_name: str, organisation_data: str):
        self.programme = programme
        self.programme_name = programme_name
        self.organisation_data = organisation_data

    def to_dict(self):
        return {
            "ProgrammeID": self.programme.programme_id,
            "ProgrammeName": self.programme.programme_name,
            "OrganisationName": self.organisation_data,
            "Place": self.programme_name,
            "FundTypeID": self.programme.fund_type_id,
        }


class ProgrammeProgressSerializer:
    def __init__(self, programme_progress: ents.ProgrammeProgress, programme_name: str, organisation_data: str):
        self.programme_progress = programme_progress
        self.programme_name = programme_name
        self.organisation_data = organisation_data

    def to_dict(self):
        return {
            "SubmissionID": self.programme_progress.submission.submission_id,
            "ProgrammeID": self.programme_progress.programme.programme_id,
            "OrganisationName": self.organisation_data,
            "Place": self.programme_name,
            "Question": self.programme_progress.question,
            "Answer": self.programme_progress.answer,
        }


class PlaceDetailSerializer:
    def __init__(self, place_detail: ents.PlaceDetail, programme_name: str, org: str):
        self.place_detail = place_detail
        self.programme_name = programme_name
        self.org = org

    def to_dict(self):
        return {
            "SubmissionID": self.place_detail.submission.submission_id,
            "ProgrammeID": self.place_detail.programme.programme_id,
            "OrganisationName": self.org,
            "Place": self.programme_name,
            "Question": self.place_detail.question,
            "Indicator": self.place_detail.indicator,
            "Answer": self.place_detail.answer,
        }


class FundingQuestionSerializer:
    def __init__(self, funding_question: ents.FundingQuestion, programme_name: str, org: str):
        self.funding_question = funding_question
        self.programme_name = programme_name
        self.org = org

    def to_dict(self):
        return {
            "SubmissionID": self.funding_question.submission.submission_id,
            "ProgrammeID": self.funding_question.programme.programme_id,
            "OrganisationName": self.org,
            "Place": self.programme_name,
            "Question": self.funding_question.question,
            "Indicator": self.funding_question.indicator,
            "Answer": self.funding_question.response,
        }


class ProjectSerializer:
    def __init__(self, project: ents.Project, programme_name: str, org: str):
        self.project = project
        self.programme_name = programme_name
        self.org = org

    def to_dict(self):
        return {
            "SubmissionID": self.project.submission.submission_id,
            "ProjectID": self.project.project_id,
            "ProjectName": self.project.project_name,
            "OrganisationName": self.org,
            "Place": self.programme_name,
            "PrimaryInterventionTheme": self.project.primary_intervention_theme,
            "SingleorMultipleLocations": self.project.location_multiplicity,
            "Locations": self.project.locations,
            "ExtractedPostcodes": self.project.postcodes,
            "AreYouProvidingAGISMapWithYourReturn": self.project.gis_provided,
            "LatLongCoordinates": self.project.lat_long,
        }


class ProjectProgressSerializer:
    def __init__(self, project_progress: ents.ProjectProgress, programme_name: str, org: str):
        self.project_progress = project_progress
        self.programme_name = programme_name
        self.org = org

    def to_dict(self):
        return {
            "SubmissionID": self.project_progress.submission.submission_id,
            "ProjectID": self.project_progress.project.project_id,
            "ProjectName": self.project_progress.project.project_name,
            "OrganisationName": self.org,
            "Place": self.programme_name,
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
    def __init__(self, funding: ents.Funding, programme_name: str, org: str):
        self.funding = funding
        self.programme_name = programme_name
        self.org = org

    def to_dict(self):
        return {
            "SubmissionID": self.funding.submission.submission_id,
            "ProjectID": self.funding.project.project_id,
            "ProjectName": self.funding.project.project_name,
            "OrganisationName": self.org,
            "Place": self.programme_name,
            "FundingSourceName": self.funding.funding_source_name,
            "FundingSourceType": self.funding.funding_source_type,
            "Secured": self.funding.secured,
            "StartDate": str(self.funding.start_date),
            "EndDate": str(self.funding.end_date),
            "SpendforReportingPeriod": self.funding.spend_for_reporting_period,
            "ActualOrForecast": self.funding.status,
        }


class FundingCommentSerializer:
    def __init__(self, funding_comment: ents.FundingComment, programme_name: str, org: str):
        self.funding_comment = funding_comment
        self.programme_name = programme_name
        self.org = org

    def to_dict(self):
        return {
            "SubmissionID": self.funding_comment.submission.submission_id,
            "ProjectID": self.funding_comment.project.project_id,
            "ProjectName": self.funding_comment.project.project_name,
            "OrganisationName": self.org,
            "Place": self.programme_name,
            "Comment": self.funding_comment.comment,
        }


class PrivateInvestmentSerializer:
    def __init__(self, private_investment: ents.PrivateInvestment, programme_name: str, org: str):
        self.private_investment = private_investment
        self.programme_name = programme_name
        self.org = org

    def to_dict(self):
        return {
            "SubmissionID": self.private_investment.submission.submission_id,
            "ProjectID": self.private_investment.project.project_id,
            "ProjectName": self.private_investment.project.project_name,
            "OrganisationName": self.org,
            "Place": self.programme_name,
            "TotalProjectValue": self.private_investment.total_project_value,
            "TownsfundFunding": self.private_investment.townsfund_funding,
            "PrivateSectorFundingRequired": self.private_investment.private_sector_funding_required,
            "PrivateSectorFundingSecured": self.private_investment.private_sector_funding_secured,
            "PSIAdditionalComments": self.private_investment.additional_comments,
        }


class OutputDataSerializer:
    def __init__(self, output_data: ents.OutputData, programme_name: str, org: str):
        self.output_data = output_data
        self.programme_name = programme_name
        self.org = org

    def to_dict(self):
        return {
            "SubmissionID": self.output_data.submission.submission_id,
            "ProjectID": self.output_data.project.project_id,
            "ProjectName": self.output_data.project.project_name,
            "OrganisationName": self.org,
            "Place": self.programme_name,
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
    def __init__(self, outcome_data: ents.OutcomeData, programme_name: str, org: str):
        self.outcome_data = outcome_data
        self.programme_name = programme_name
        self.org = org

    def to_dict(self):
        return {
            "SubmissionID": self.outcome_data.submission.submission_id,
            "ProgrammeID": self.outcome_data.programme.programme_id if self.outcome_data.programme else None,
            "ProjectID": self.outcome_data.project.project_id if self.outcome_data.project else None,
            "ProjectName": self.outcome_data.project.project_name if self.outcome_data.project else None,
            "OrganisationName": self.org,
            "Place": self.programme_name,
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
    def __init__(self, risk_register: ents.RiskRegister, programme_name: str, org: str):
        self.risk_register = risk_register
        self.programme_name = programme_name
        self.org = org

    def to_dict(self):
        return {
            "SubmissionID": self.risk_register.submission.submission_id,
            "ProgrammeID": self.risk_register.programme.programme_id if self.risk_register.programme else None,
            "ProjectID": self.risk_register.project.project_id if self.risk_register.project else None,
            "ProjectName": self.risk_register.project.project_name if self.risk_register.project else None,
            "OrganisationName": self.org,
            "Place": self.programme_name,
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
