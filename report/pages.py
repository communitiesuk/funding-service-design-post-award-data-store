from report import forms
from report.report_form_components.report_form_page import ReportFormPage

_AVAILABLE_PAGES = [
    ReportFormPage(
        page_id="progress_summary",
        form_class=forms.ProgressSummary,
        template="form_pages/progress-summary.html",
    ),
    ReportFormPage(
        page_id="upcoming_communications_initiate",
        form_class=forms.UpcomingCommunicationsInitiate,
        template="form_pages/upcoming-communications-initiate.html",
    ),
    ReportFormPage(
        page_id="upcoming_communication_title",
        form_class=forms.UpcomingCommunicationTitle,
        template="form_pages/upcoming-communication-title.html",
    ),
    ReportFormPage(
        page_id="upcoming_communication_details",
        form_class=forms.UpcomingCommunicationDetails,
        template="form_pages/upcoming-communication-details.html",
    ),
    ReportFormPage(
        page_id="rag_rating_overall",
        form_class=forms.RAGRatingOverall,
        template="form_pages/rag-rating-overall.html",
    ),
    ReportFormPage(
        page_id="rag_rating_schedule",
        form_class=forms.RAGRatingSchedule,
        template="form_pages/rag-rating-schedule.html",
    ),
    ReportFormPage(
        page_id="rag_rating_budget",
        form_class=forms.RAGRatingBudget,
        template="form_pages/rag-rating-budget.html",
    ),
    ReportFormPage(
        page_id="rag_rating_resourcing",
        form_class=forms.RAGRatingResourcing,
        template="form_pages/rag-rating-resourcing.html",
    ),
    ReportFormPage(
        page_id="rag_rating_information",
        form_class=forms.RAGRatingInformation,
        template="form_pages/rag-rating-information.html",
    ),
    ReportFormPage(
        page_id="challenges_initiate",
        form_class=forms.ChallengesInitiate,
        template="form_pages/challenges-initiate.html",
    ),
    ReportFormPage(
        page_id="challenge_title",
        form_class=forms.ChallengeTitle,
        template="form_pages/challenge-title.html",
    ),
    ReportFormPage(
        page_id="challenge_details",
        form_class=forms.ChallengeDetails,
        template="form_pages/challenge-details.html",
    ),
    ReportFormPage(
        page_id="riba_reporting_stage",
        form_class=forms.RIBAReportingStage,
        template="form_pages/riba-reporting-stage.html",
    ),
    ReportFormPage(
        page_id="issues_initiate",
        form_class=forms.IssuesInitiate,
        template="form_pages/issues-initiate.html",
    ),
    ReportFormPage(
        page_id="issue_title",
        form_class=forms.IssueTitle,
        template="form_pages/issue-title.html",
    ),
    ReportFormPage(
        page_id="issue_impact_rating",
        form_class=forms.IssueImpactRating,
        template="form_pages/issue-impact-rating.html",
    ),
    ReportFormPage(
        page_id="issue_details",
        form_class=forms.IssueDetails,
        template="form_pages/issue-details.html",
    ),
]


def parse_available_pages() -> dict[str, ReportFormPage]:
    available_pages_dict = {page.page_id: page for page in _AVAILABLE_PAGES}
    if len(available_pages_dict) != len(_AVAILABLE_PAGES):
        raise ValueError("Duplicate page IDs found in available pages")
    return available_pages_dict


AVAILABLE_PAGES_DICT = parse_available_pages()
