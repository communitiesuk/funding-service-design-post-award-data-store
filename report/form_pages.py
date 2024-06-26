from govuk_frontend_wtf.wtforms_widgets import GovCharacterCount, GovFileInput, GovRadioInput, GovTextArea, GovTextInput
from wtforms import FileField, RadioField, StringField

from report.flask_form import CustomFlaskForm
from report.form.form_page import FormPage


class ProgressSummaryPage(FormPage):
    page_id = "progress-summary"
    template = "form_pages/progress-summary.html"

    class form_class(CustomFlaskForm):
        progress_summary = StringField(label="", widget=GovCharacterCount())


class UpcomingCommunicationsInitiatePage(FormPage):
    page_id = "upcoming-communications-initiate"
    template = "form_pages/upcoming-communications-initiate.html"

    class form_class(CustomFlaskForm):
        do_you_have_any_upcoming_communications = RadioField(
            label="",
            choices=(("yes", "Yes"), ("no", "No")),
            widget=GovRadioInput(),
        )


class UpcomingCommunicationTitlePage(FormPage):
    page_id = "upcoming-communication-title"
    template = "form_pages/upcoming-communication-title.html"

    class form_class(CustomFlaskForm):
        upcoming_communication_title = StringField(label="", widget=GovTextInput())


class UpcomingCommunicationDetailsPage(FormPage):
    page_id = "upcoming-communication-details"
    template = "form_pages/upcoming-communication-details.html"

    class form_class(CustomFlaskForm):
        upcoming_communication_details = StringField(label="", widget=GovCharacterCount())


class RAGRatingOverallPage(FormPage):
    page_id = "rag-rating-overall"
    template = "form_pages/rag-rating-overall.html"

    class form_class(CustomFlaskForm):
        overall_rag_rating = RadioField(
            label="",
            choices=(
                ("red", "Red - no progress"),
                ("amber", "Amber - partial progress"),
                ("green", "Green - good progress"),
            ),
            widget=GovRadioInput(),
        )


class RAGRatingSchedulePage(FormPage):
    page_id = "rag-rating-schedule"
    template = "form_pages/rag-rating-schedule.html"

    class form_class(CustomFlaskForm):
        schedule_rag_rating = RadioField(
            label="",
            choices=(
                ("red", "Red - no progress"),
                ("amber", "Amber - partial progress"),
                ("green", "Green - good progress"),
            ),
            widget=GovRadioInput(),
        )


class RAGRatingBudgetPage(FormPage):
    page_id = "rag-rating-budget"
    template = "form_pages/rag-rating-budget.html"

    class form_class(CustomFlaskForm):
        budget_rag_rating = RadioField(
            label="",
            choices=(
                ("red", "Red - no progress"),
                ("amber", "Amber - partial progress"),
                ("green", "Green - good progress"),
            ),
            widget=GovRadioInput(),
        )


class RAGRatingResourcingPage(FormPage):
    page_id = "rag-rating-resourcing"
    template = "form_pages/rag-rating-resourcing.html"

    class form_class(CustomFlaskForm):
        resourcing_rag_rating = RadioField(
            label="",
            choices=(
                ("red", "Red - no progress"),
                ("amber", "Amber - partial progress"),
                ("green", "Green - good progress"),
            ),
            widget=GovRadioInput(),
        )


class RAGRatingInformationPage(FormPage):
    page_id = "rag-rating-information"
    template = "form_pages/rag-rating-information.html"

    class form_class(CustomFlaskForm):
        any_additional_information = RadioField(
            label="",
            choices=[("yes", "Yes"), ("no", "No")],
            widget=GovRadioInput(),
        )
        additional_information = StringField(label="", widget=GovTextArea())


class ChallengesInitiatePage(FormPage):
    page_id = "challenges-initiate"
    template = "form_pages/challenges-initiate.html"

    class form_class(CustomFlaskForm):
        do_you_have_any_challenges = RadioField(
            label="",
            choices=(("yes", "Yes"), ("no", "No")),
            widget=GovRadioInput(),
        )


class ChallengeTitlePage(FormPage):
    page_id = "challenge-title"
    template = "form_pages/challenge-title.html"

    class form_class(CustomFlaskForm):
        challenge_title = StringField(label="", widget=GovTextInput())


class ChallengeDetailsPage(FormPage):
    page_id = "challenge-details"
    template = "form_pages/challenge-details.html"

    class form_class(CustomFlaskForm):
        challenge_details = StringField(label="", widget=GovCharacterCount())


class RIBAReportingStagePage(FormPage):
    page_id = "riba-reporting-stage"
    template = "form_pages/riba-reporting-stage.html"

    class form_class(CustomFlaskForm):
        riba_reporting_stage = RadioField(
            label="",
            choices=[
                ("stage-1", "Stage 1 - Preparation and Brief"),
                ("stage-2", "Stage 2 - Concept Design"),
                ("stage-3", "Stage 3 - Spatial Coordination"),
                ("stage-4", "Stage 4 - Technical Design"),
                ("stage-5", "Stage 5 - Manufacturing and Construction"),
            ],
            widget=GovRadioInput(),
        )


class IssuesInitiatePage(FormPage):
    page_id = "issues-initiate"
    template = "form_pages/issues-initiate.html"

    class form_class(CustomFlaskForm):
        do_you_have_any_issues = RadioField(
            label="",
            choices=(("yes", "Yes"), ("no", "No")),
            widget=GovRadioInput(),
        )


class IssueTitlePage(FormPage):
    page_id = "issue-title"
    template = "form_pages/issue-title.html"

    class form_class(CustomFlaskForm):
        issue_title = StringField(label="", widget=GovTextInput())


class IssueImpactRatingPage(FormPage):
    page_id = "issue-impact-rating"
    template = "form_pages/issue-impact-rating.html"

    class form_class(CustomFlaskForm):
        issue_impact_rating = RadioField(
            label="",
            choices=[
                ("insignificant", "Insignificant"),
                ("minor", "Minor"),
                ("significant", "Significant"),
                ("major", "Major"),
                ("severe", "Severe"),
            ],
            widget=GovRadioInput(),
        )


class IssueDetailsPage(FormPage):
    page_id = "issue-details"
    template = "form_pages/issue-details.html"

    class form_class(CustomFlaskForm):
        issue_details = StringField(label="", widget=GovTextArea())


class ExpenditurePage(FormPage):
    page_id = "expenditure"
    template = "form_pages/expenditure.html"

    class form_class(CustomFlaskForm):
        expenditure = FileField(label="", widget=GovFileInput())


class RisksInitiatePage(FormPage):
    page_id = "risks-initiate"
    template = "form_pages/risks-initiate.html"

    class form_class(CustomFlaskForm):
        do_you_have_any_risks = RadioField(
            label="",
            choices=(("yes", "Yes"), ("no", "No")),
            widget=GovRadioInput(),
        )


class RiskTitlePage(FormPage):
    page_id = "risk-title"
    template = "form_pages/risk-title.html"

    class form_class(CustomFlaskForm):
        risk_title = StringField(label="", widget=GovTextInput())


class RiskCategoryPage(FormPage):
    page_id = "risk-category"
    template = "form_pages/risk-category.html"

    class form_class(CustomFlaskForm):
        risk_category = RadioField(
            label="",
            choices=[
                ("1", "Category 1 - Very high"),
                ("2", "Category 2 - High"),
                ("3", "Category 3 - Medium"),
                ("4", "Category 4 - Low"),
                ("5", "Category 5 - Very low"),
            ],
            widget=GovRadioInput(),
        )


class RiskMitigationPage(FormPage):
    page_id = "risk-mitigation"
    template = "form_pages/risk-mitigation.html"

    class form_class(CustomFlaskForm):
        how_will_you_mitigate_the_risk = StringField(label="", widget=GovCharacterCount())


class RiskIssueLikelihoodPage(FormPage):
    page_id = "risk-issue-likelihood"
    template = "form_pages/risk-issue-likelihood.html"

    class form_class(CustomFlaskForm):
        how_likely_is_it_that_the_risk_becomes_an_issue = RadioField(
            label="",
            choices=[
                ("extremely-likely", "Extremely likely"),
                ("likely", "Likely"),
                ("possible", "Possible"),
                ("unlikely", "Unlikely"),
                ("extremely-unlikely", "Extremely unlikely"),
            ],
            widget=GovRadioInput(),
        )


class MilestonesPage(FormPage):
    page_id = "milestones"
    template = "form_pages/milestones.html"

    class form_class(CustomFlaskForm):
        milestone_1 = StringField(
            label="",
            widget=GovCharacterCount(),
        )
        milestone_2 = StringField(
            label="",
            widget=GovCharacterCount(),
        )
        milestone_3 = StringField(
            label="",
            widget=GovCharacterCount(),
        )


def available_form_pages():
    return {cls.page_id: cls() for cls in FormPage.__subclasses__()}


def get_form_page(page_id: str) -> FormPage:
    pages = available_form_pages()
    return pages[page_id]
