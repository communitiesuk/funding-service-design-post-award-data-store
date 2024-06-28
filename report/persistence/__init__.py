from core.dto.programme import ProgrammeDTO, persist_pending_submission
from report.persistence.report import Report
from report.persistence.submission import Submission


def get_submission(programme: ProgrammeDTO | None) -> Submission:
    pending_submission = programme.pending_submission
    if not pending_submission:
        return Submission(programme_report=Report(name=programme.programme_name, sections=[]), project_reports=[])
    return Submission.load_from_json(pending_submission.data_blob)


def persist_submission(programme: ProgrammeDTO, submission: Submission):
    persist_pending_submission(programme, submission.serialize())
