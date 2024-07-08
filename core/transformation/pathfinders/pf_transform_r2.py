from datetime import datetime

import pandas as pd

from core.db.entities import PendingSubmission, ProjectRef
from core.transformation.pathfinders.consts import PF_REPORTING_ROUND_TO_DATES
from core.transformation.utils import create_dataframe
from report.persistence.submission_blob import SubmissionBlob


def transform(pending_submission: PendingSubmission) -> None:
    submission_blob = SubmissionBlob.load_from_json(pending_submission.data_blob)
    transformed = {}
    transformed["Submission_Ref"] = _submission_ref(pending_submission)
    transformed["Place Details"] = _place_details(pending_submission, submission_blob)
    # Although we don't load need to load a Programme as we load Programme data in advance, we still need Programme_Ref
    # in the transformed output as it is used in the load_programme_junction function
    transformed["Programme_Ref"] = _programme_ref(pending_submission, submission_blob)
    # No need for Organisation_Ref as Organisation created in advance AND no load function uses it
    transformed["Project Details"] = _project_details(pending_submission, submission_blob)
    transformed["Programme Progress"] = _programme_progress(pending_submission, submission_blob)
    transformed["Project Progress"] = _project_progress(pending_submission, submission_blob)
    transformed["Funding Questions"] = _funding_questions(pending_submission, submission_blob)
    transformed["Funding"] = _funding_data(pending_submission, submission_blob)
    transformed.update(_outputs(pending_submission, submission_blob))
    transformed.update(_outcomes(pending_submission, submission_blob))
    transformed["RiskRegister"] = _risk_register(pending_submission, submission_blob)
    transformed["ProjectFinanceChange"] = _project_finance_changes(pending_submission, submission_blob)
    return transformed


def _submission_ref(pending_submission: PendingSubmission) -> pd.DataFrame:
    reporting_round = pending_submission.reporting_round
    # TODO: Get sign off details from submission_blob
    return create_dataframe(
        {
            "Submission Date": [datetime.now()],
            "Reporting Period Start": [PF_REPORTING_ROUND_TO_DATES[reporting_round]["start"]],
            "Reporting Period End": [PF_REPORTING_ROUND_TO_DATES[reporting_round]["end"]],
            "Sign Off Name": [""],
            "Sign Off Role": [""],
            "Sign Off Date": [""],
        }
    )


def _place_details(pending_submission: PendingSubmission, submission_blob: SubmissionBlob) -> pd.DataFrame:
    programme = pending_submission.programme
    questions = [
        "Financial completion date",
        "Practical completion date",
        "Organisation name",
        "Contact name",
        "Contact email",
        "Contact telephone",
    ]
    # TODO: Get answers from submission_blob
    return create_dataframe(
        {
            "Programme ID": [programme.programme_id] * len(questions),
            "Question": questions,
            "Answer": [""] * len(questions),
        }
    )


def _programme_ref(pending_submission: PendingSubmission, submission_blob: SubmissionBlob) -> pd.DataFrame:
    programme = pending_submission.programme
    fund = programme.fund
    organisation = programme.organisation
    return create_dataframe(
        {
            "Programme ID": [programme.programme_id],
            "FundType_ID": [fund.fund_code],
            "Organisation": [organisation.organisation_name],
        }
    )


def _project_details(pending_submission: PendingSubmission, submission_blob: SubmissionBlob) -> pd.DataFrame:
    programme = pending_submission.programme
    project_ids, project_names, locations, postcodes = [], [], [], []
    for project_id, report_blob in submission_blob.project_reports.items():  # noqa
        project_ids.append(project_id)
        project_ref: ProjectRef = ProjectRef.query.filter_by(project_id=project_id).one()
        project_names.append(project_ref.project_name)
        # TODO: Get locations and postcodes from report_blob
        locations.append("")
        postcodes.append("")
    return create_dataframe(
        {
            "Project ID": project_ids,
            "Programme ID": [programme.programme_id] * len(project_ids),
            "Project Name": project_names,
            "Locations": locations,
            "Postcodes": postcodes,
        }
    )


def _programme_progress(pending_submission: PendingSubmission, submission_blob: SubmissionBlob) -> pd.DataFrame:
    programme = pending_submission.programme
    questions = ["Portfolio progress", "Big issues across portfolio", "Upcoming significant milestones"]
    # TODO: Get answers from submission_blob
    return create_dataframe(
        {
            "Programme ID": [programme.programme_id] * len(questions),
            "Question": questions,
            "Answer": [""] * len(questions),
        }
    )


def _project_progress(pending_submission: PendingSubmission, submission_blob: SubmissionBlob) -> pd.DataFrame:
    project_ids, delivery_rags, spend_rags, commentaries = [], [], [], []
    for project_id, report_blob in submission_blob.project_reports.items():  # noqa
        project_ids.append(project_id)
        # TODO: Get delivery_rags, spend_rags, and commentaries from report_blob
        delivery_rags.append("")
        spend_rags.append("")
        commentaries.append("")
    return create_dataframe(
        {
            "Project ID": project_ids,
            "Delivery (RAG)": delivery_rags,
            "Spend (RAG)": spend_rags,
            "Commentary on Status and RAG Ratings": commentaries,
        }
    )


def _funding_questions(pending_submission: PendingSubmission, submission_blob: SubmissionBlob) -> pd.DataFrame:
    programme = pending_submission.programme
    questions = [
        "Credible plan",
        "Total underspend",
        "Proposed underspend use",
        "Credible plan summary",
        "Current underspend",
        "Uncommitted funding plan",
        "Summary of changes below change request threshold",
    ]
    # TODO: Get answers from submission_blob
    return create_dataframe(
        {
            "Programme ID": [programme.programme_id] * len(questions),
            "Question": questions,
            "Response": [""] * len(questions),
        }
    )


def _funding_data(pending_submission: PendingSubmission, submission_blob: SubmissionBlob) -> pd.DataFrame:
    programme = pending_submission.programme
    # TODO: Get funding data from submission_blob
    funding_source_types = []
    start_dates = []
    end_dates = []
    spends_for_reporting_period = []
    actual_forecasts = []
    return create_dataframe(
        {
            "Programme ID": [programme.programme_id] * len(funding_source_types),
            "Funding Source Type": funding_source_types,
            "Start_Date": start_dates,
            "End_Date": end_dates,
            "Spend for Reporting Period": spends_for_reporting_period,
            "Actual/Forecast": actual_forecasts,
        }
    )


def _outputs(pending_submission: PendingSubmission, submission_blob: SubmissionBlob) -> dict:
    programme = pending_submission.programme
    # TODO: Get outputs from submission_blob
    return {
        "Outputs_Ref": create_dataframe(
            {
                "output_name": [],
                "output_category": [],
            }
        ),
        "Output_Data": create_dataframe(
            {
                "Programme ID": [programme.programme_id] * 0,
                "Output": [],
                "Start_Date": [],
                "End_Date": [],
                "Unit of Measurement": [],
                "Actual/Forecast": [],
                "Amount": [],
            }
        ),
    }


def _outcomes(pending_submission: PendingSubmission, submission_blob: SubmissionBlob) -> dict:
    programme = pending_submission.programme
    # TODO: Get outcomes from submission_blob
    return {
        "Outcome_Ref": create_dataframe(
            {
                "outcome_name": [],
                "outcome_category": [],
            }
        ),
        "Outcome_Data": create_dataframe(
            {
                "Programme ID": [programme.programme_id] * 0,
                "Outcome": [],
                "Start_Date": [],
                "End_Date": [],
                "Unit of Measurement": [],
                "Actual/Forecast": [],
                "Amount": [],
            }
        ),
    }


def _risk_register(pending_submission: PendingSubmission, submission_blob: SubmissionBlob) -> pd.DataFrame:
    programme = pending_submission.programme
    # TODO: Get risks from submission_blob
    return create_dataframe(
        {
            "Programme ID": [programme.programme_id] * 0,
            "RiskName": [],
            "RiskCategory": [],
            "Short Description": [],
            "Pre-mitigatedImpact": [],
            "Pre-mitigatedLikelihood": [],
            "Mitigatons": [],  # NOTE: Typo in mappings.py needs to be fixed
            "PostMitigatedImpact": [],
            "PostMitigatedLikelihood": [],
        }
    )


def _project_finance_changes(pending_submission: PendingSubmission, submission_blob: SubmissionBlob) -> pd.DataFrame:
    programme = pending_submission.programme
    # TODO: Get project finance changes from submission_blob
    return create_dataframe(
        {
            "Programme ID": [programme.programme_id] * 0,
            "Change Number": [],
            "Project Funding Moved From": [],
            "Intervention Theme Moved From": [],
            "Project Funding Moved To": [],
            "Intervention Theme Moved To": [],
            "Amount Moved": [],
            "Change Made": [],
            "Reason for Change": [],
            "Actual or Forecast": [],
            "Reporting Period Change Takes Place": [],
        }
    )
