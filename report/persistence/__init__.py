from core.dto.pending_submission import get_pending_submission as _get_pending_submission
from core.dto.pending_submission import persist_pending_submission as _persist_pending_submission
from core.dto.programme import ProgrammeDTO
from report.persistence.report import Report
from report.persistence.submission import Submission


def get_pending_submission(programme: ProgrammeDTO | None, reporting_round: int) -> Submission:
    pending_submission = _get_pending_submission(programme, reporting_round)
    if not pending_submission:
        return Submission(
            programme_report=Report(
                name=programme.organisation.organisation_name,
                sections=[],
            ),
            project_reports=[],
        )
    return Submission.load_from_json(pending_submission.data_blob)


def persist_pending_submission(programme: ProgrammeDTO, reporting_round: int, pending_submission: Submission) -> None:
    _persist_pending_submission(programme, reporting_round, pending_submission.serialize())
