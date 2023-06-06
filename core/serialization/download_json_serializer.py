import core.db.entities as entities
from core.db.entities import OutcomeDim, OutputDim


def serialize_download_data(organisations, programmes, projects, outcomes):
    """Top level serialization of the download data."""

    # Organisation level data
    organisation_refs = [OrganisationSerializer(organisation).to_json() for organisation in organisations]

    # Programme level data
    programme_progresses = [
        ProgrammeProgressSerializer(prog_progress).to_json()
        for programme in programmes
        for prog_progress in programme.progress_records
    ]
    programme_refs = [ProgrammeSerializer(prog).to_json() for prog in programmes]
    place_details = [
        PlaceDetailSerializer(place_detail).to_json()
        for programme in programmes
        for place_detail in programme.place_details
    ]
    funding_questions = [
        FundingQuestionSerializer(funding_q).to_json()
        for programme in programmes
        for funding_q in programme.funding_questions
    ]
    programme_risks = [RiskRegisterSerializer(risk).to_json() for programme in programmes for risk in programme.risks]

    # Project level data
    project_details = [ProjectSerializer(proj).to_json() for proj in projects]
    project_progresses = [
        ProjectProgressSerializer(proj_prog).to_json() for project in projects for proj_prog in project.progress_records
    ]
    funding = [FundingSerializer(funding).to_json() for project in projects for funding in project.funding_records]
    funding_comments = [
        FundingCommentSerializer(funding_comment).to_json()
        for project in projects
        for funding_comment in project.funding_comments
    ]
    private_investments = [
        PrivateInvestmentSerializer(private_investment).to_json()
        for project in projects
        for private_investment in project.private_investments
    ]
    outputs_ref = [OutputDimSerializer(output_dim).to_json() for output_dim in OutputDim.query.all()]
    output_data = [
        OutputDataSerializer(output_data).to_json() for project in projects for output_data in project.outputs
    ]
    outcome_ref = [OutcomeDimSerializer(outcome_dim).to_json() for outcome_dim in OutcomeDim.query.all()]
    outcome_data = [OutcomeDataSerializer(outcome_data).to_json() for outcome_data in outcomes]
    project_risks = [RiskRegisterSerializer(risk).to_json() for project in projects for risk in project.risks]
    risks = [*programme_risks, *project_risks]  # risks are combination of programme and project risks

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
        "OutcomeData": outcome_data,
        "RiskRegister": risks,
    }
    return download_data


class OrganisationSerializer:
    def __init__(self, organisation: entities.Organisation):
        self.organisation = organisation

    def to_json(self):
        return {
            "OrganisationID": str(self.organisation.id),
            "OrganisationName": self.organisation.organisation_name,
            "Geography": self.organisation.geography,
        }


class ProgrammeSerializer:
    def __init__(self, programme: entities.Programme):
        self.programme = programme

    def to_json(self):
        return {
            "ProgrammeID": self.programme.programme_id,
            "ProgrammeName": self.programme.programme_name,
            "FundTypeID": self.programme.fund_type_id,
            "OrganisationID": str(self.programme.organisation_id),
        }


class ProgrammeProgressSerializer:
    def __init__(self, programme_progress: entities.ProgrammeProgress):
        self.programme_progress = programme_progress

    def to_json(self):
        return {
            "ID": str(self.programme_progress.id),
            "SubmissionID": self.programme_progress.submission.submission_id,
            "ProgrammeID": self.programme_progress.programme.programme_id,
            "Question": self.programme_progress.question,
            "Answer": self.programme_progress.answer,
        }


class PlaceDetailSerializer:
    def __init__(self, place_detail: entities.PlaceDetail):
        self.place_detail = place_detail

    def to_json(self):
        return {
            "ID": str(self.place_detail.id),
            "SubmissionID": self.place_detail.submission.submission_id,
            "Question": self.place_detail.question,
            "Answer": self.place_detail.answer,
            "ProgrammeID": self.place_detail.programme.programme_id,
            "Indicator": self.place_detail.indicator,
        }


class FundingQuestionSerializer:
    def __init__(self, funding_question: entities.FundingQuestion):
        self.funding_question = funding_question

    def to_json(self):
        return {
            "ID": str(self.funding_question.id),
            "SubmissionID": self.funding_question.submission.submission_id,
            "ProgrammeID": self.funding_question.programme.programme_id,
            "Question": self.funding_question.question,
            "Indicator": self.funding_question.indicator,
            "Response": self.funding_question.response,
            "GuidanceNotes": self.funding_question.guidance_notes,
        }


class ProjectSerializer:
    def __init__(self, project: entities.Project):
        self.project = project

    def to_json(self):
        return {
            "ID": str(self.project.id),
            "SubmissionID": self.project.submission.submission_id,
            "ProjectID": self.project.project_id,
            "ProjectName": self.project.project_name,
            "PrimaryInterventionTheme": self.project.primary_intervention_theme,
            "SingleorMultipleLocations": self.project.location_multiplicity,
            "Locations": self.project.locations,
        }


class ProjectProgressSerializer:
    def __init__(self, project_progress: entities.ProjectProgress):
        self.project_progress = project_progress

    def to_json(self):
        return {
            "ID": str(self.project_progress.id),
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
            "DateofMostImportantUpcomingCommsMilestone(e.g.Dec-22)": self.project_progress.date_of_important_milestone,
        }


class FundingSerializer:
    def __init__(self, funding: entities.Funding):
        self.funding = funding

    def to_json(self):
        return {
            "ID": str(self.funding.id),
            "SubmissionID": self.funding.submission.submission_id,
            "ProjectID": self.funding.project.project_id,
            "FundingSourceName": self.funding.funding_source_name,
            "FundingSourceType": self.funding.funding_source_type,
            "Secured": self.funding.secured,
            "FinancialPeriodStart": str(self.funding.start_date),
            "FinancialPeriodEnd": str(self.funding.end_date),
            "SpendforReportingPeriod": self.funding.spend_for_reporting_period,
            "Actual": self.funding.status,
        }


class FundingCommentSerializer:
    def __init__(self, funding_comment: entities.FundingComment):
        self.funding_comment = funding_comment

    def to_json(self):
        return {
            "ID": str(self.funding_comment.id),
            "SubmissionID": self.funding_comment.submission.submission_id,
            "ProjectID": self.funding_comment.project.project_id,
            "Comment": self.funding_comment.comment,
        }


class PrivateInvestmentSerializer:
    def __init__(self, private_investment: entities.PrivateInvestment):
        self.private_investment = private_investment

    def to_json(self):
        return {
            "ID": str(self.private_investment.id),
            "SubmissionID": self.private_investment.submission.submission_id,
            "ProjectID": self.private_investment.project.project_id,
            "TotalProjectValue": self.private_investment.total_project_value,
            "TownsfundFunding": self.private_investment.townsfund_funding,
            "PrivateSectorFundingRequired": self.private_investment.private_sector_funding_required,
            "PrivateSectorFundingSecured": self.private_investment.private_sector_funding_secured,
            "AdditionalComments": self.private_investment.additional_comments,
        }


class OutputDataSerializer:
    def __init__(self, output_data: entities.OutputData):
        self.output_data = output_data

    def to_json(self):
        return {
            "ID": str(self.output_data.id),
            "SubmissionID": self.output_data.submission.submission_id,
            "ProjectID": self.output_data.project.project_id,
            "FinancialPeriodStart": str(self.output_data.start_date),
            "FinancialPeriodEnd": str(self.output_data.end_date),
            "Output": self.output_data.output_dim.output_name,
            "UnitofMeasurement": self.output_data.unit_of_measurement,
            "Actual": self.output_data.state,
            "Amount": self.output_data.amount,
            "AdditionalInformation": self.output_data.additional_information,
        }


class OutputDimSerializer:
    def __init__(self, output_dim: entities.OutputDim):
        self.output_dim = output_dim

    def to_json(self):
        return {
            "ID": str(self.output_dim.id),
            "OutputName": self.output_dim.output_name,
            "OutputCategory": self.output_dim.output_category,
        }


class OutcomeDataSerializer:
    def __init__(self, outcome_data: entities.OutcomeData):
        self.outcome_data = outcome_data

    def to_json(self):
        return {
            "ID": str(self.outcome_data.id),
            "SubmissionID": self.outcome_data.submission.submission_id,
            "ProjectID": self.outcome_data.project.project_id,
            "FinancialPeriodStart": str(self.outcome_data.start_date),
            "FinancialPeriodEnd": str(self.outcome_data.end_date),
            "Outcome": self.outcome_data.outcome_dim.outcome_name,
            "UnitofMeasurement": self.outcome_data.unit_of_measurement,
            "GeographyIndicator": self.outcome_data.geography_indicator,
            "Amount": self.outcome_data.amount,
            "Actual": self.outcome_data.state,
        }


class OutcomeDimSerializer:
    def __init__(self, outcome_dim: entities.OutcomeDim):
        self.outcome_dim = outcome_dim

    def to_json(self):
        return {
            "ID": str(self.outcome_dim.id),
            "Outcome_Name": self.outcome_dim.outcome_name,
            "Outcome_Category": self.outcome_dim.outcome_category,
        }


class RiskRegisterSerializer:
    def __init__(self, risk_register: entities.RiskRegister):
        self.risk_register = risk_register

    def to_json(self):
        return {
            "ID": str(self.risk_register.id),
            "SubmissionID": self.risk_register.submission.submission_id,
            "ProgrammeID": self.risk_register.programme.programme_id if self.risk_register.programme else None,
            "ProjectID": self.risk_register.project.project_id if self.risk_register.project else None,
            "RiskName": self.risk_register.risk_name,
            "RiskCategory": self.risk_register.risk_category,
            "ShortDescription": self.risk_register.short_desc,
            "FullDescription": self.risk_register.full_desc,
            "Consequences": self.risk_register.consequences,
            "Pre-mitigatedImpact": self.risk_register.pre_mitigated_impact,
            "Pre-mitigatedLikelihood": self.risk_register.pre_mitigated_likelihood,
            "Mitigations": self.risk_register.mitigations,
            "PostMitigatedImpact": self.risk_register.post_mitigated_impact,
            "PostMitigatedLikelihood": self.risk_register.post_mitigated_likelihood,
            "Proximity": self.risk_register.proximity,
            "RiskOwnerRole": self.risk_register.risk_owner_role,
        }
