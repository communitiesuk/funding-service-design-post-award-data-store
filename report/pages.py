import os

from report import forms
from report.form.form_page import FormPage

_AVAILABLE_PAGES = [
    FormPage(
        page_id="progress_summary",
        form_class=forms.ProgressSummary,
        template="form_pages/progress-summary.html",
    ),
    FormPage(
        page_id="upcoming_communications_initiate",
        form_class=forms.UpcomingCommunicationsInitiate,
        template="form_pages/upcoming-communications-initiate.html",
    ),
    FormPage(
        page_id="upcoming_communication_title",
        form_class=forms.UpcomingCommunicationTitle,
        template="form_pages/upcoming-communication-title.html",
    ),
    FormPage(
        page_id="upcoming_communication_details",
        form_class=forms.UpcomingCommunicationDetails,
        template="form_pages/upcoming-communication-details.html",
    ),
    FormPage(
        page_id="rag_rating_overall",
        form_class=forms.RAGRatingOverall,
        template="form_pages/rag-rating-overall.html",
    ),
    FormPage(
        page_id="rag_rating_schedule",
        form_class=forms.RAGRatingSchedule,
        template="form_pages/rag-rating-schedule.html",
    ),
    FormPage(
        page_id="rag_rating_budget",
        form_class=forms.RAGRatingBudget,
        template="form_pages/rag-rating-budget.html",
    ),
    FormPage(
        page_id="rag_rating_resourcing",
        form_class=forms.RAGRatingResourcing,
        template="form_pages/rag-rating-resourcing.html",
    ),
    FormPage(
        page_id="rag_rating_information",
        form_class=forms.RAGRatingInformation,
        template="form_pages/rag-rating-information.html",
    ),
    FormPage(
        page_id="challenges_initiate",
        form_class=forms.ChallengesInitiate,
        template="form_pages/challenges-initiate.html",
    ),
    FormPage(
        page_id="challenge_title",
        form_class=forms.ChallengeTitle,
        template="form_pages/challenge-title.html",
    ),
    FormPage(
        page_id="challenge_details",
        form_class=forms.ChallengeDetails,
        template="form_pages/challenge-details.html",
    ),
    FormPage(
        page_id="riba_reporting_stage",
        form_class=forms.RIBAReportingStage,
        template="form_pages/riba-reporting-stage.html",
    ),
    FormPage(
        page_id="issues_initiate",
        form_class=forms.IssuesInitiate,
        template="form_pages/issues-initiate.html",
    ),
    FormPage(
        page_id="issue_title",
        form_class=forms.IssueTitle,
        template="form_pages/issue-title.html",
    ),
    FormPage(
        page_id="issue_impact_rating",
        form_class=forms.IssueImpactRating,
        template="form_pages/issue-impact-rating.html",
    ),
    FormPage(
        page_id="issue_details",
        form_class=forms.IssueDetails,
        template="form_pages/issue-details.html",
    ),
    FormPage(
        page_id="expenditure",
        form_class=forms.Expenditure,
        template="form_pages/expenditure.html",
    ),
    FormPage(
        page_id="risks_initiate",
        form_class=forms.RisksInitiate,
        template="form_pages/risks-initiate.html",
    ),
    FormPage(
        page_id="risk_title",
        form_class=forms.RiskTitle,
        template="form_pages/risk-title.html",
    ),
    FormPage(
        page_id="risk_category",
        form_class=forms.RiskCategory,
        template="form_pages/risk-category.html",
    ),
    FormPage(
        page_id="risk_mitigation",
        form_class=forms.RiskMitigation,
        template="form_pages/risk-mitigation.html",
    ),
    FormPage(
        page_id="risk_issue_likelihood",
        form_class=forms.RiskIssueLikelihood,
        template="form_pages/risk-issue-likelihood.html",
    ),
]

TEMPLATE_DIR = os.path.join(os.path.dirname(__file__), "templates")


def parse_available_pages() -> dict[str, FormPage]:
    page_ids_seen = set()
    available_pages_dict = {}

    for page in _AVAILABLE_PAGES:
        # Check if file exists at template path
        if not os.path.exists(os.path.join(TEMPLATE_DIR, page.template)):
            raise ValueError(f"Template file not found: {page.template}")

        # Check for duplicate page IDs
        if page.page_id in page_ids_seen:
            raise ValueError(f"Duplicate page ID found: {page.page_id}")
        page_ids_seen.add(page.page_id)
        available_pages_dict[page.page_id] = page
    return available_pages_dict


AVAILABLE_PAGES_DICT = parse_available_pages()
