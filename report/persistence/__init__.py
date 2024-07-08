from core.db.propagate_pending_submission import propagate_pending_submission as _propagate_pending_submission
from core.dto.pending_submission import get_pending_submission as _get_pending_submission
from core.dto.pending_submission import persist_pending_submission as _persist_pending_submission
from core.dto.programme import ProgrammeDTO
from report.persistence.report_blob import ReportBlob
from report.persistence.submission_blob import SubmissionBlob


def get_pending_submission(programme: ProgrammeDTO | None, reporting_round: int) -> SubmissionBlob:
    pending_submission = _get_pending_submission(programme, reporting_round)
    if not pending_submission:
        return SubmissionBlob(
            programme_report=ReportBlob(
                name=programme.organisation.organisation_name,
                sections=[],
            ),
            project_reports={},
        )
    return SubmissionBlob.load_from_json(pending_submission.data_blob)


def persist_pending_submission(
    programme: ProgrammeDTO, reporting_round: int, pending_submission: SubmissionBlob
) -> None:
    _persist_pending_submission(programme, reporting_round, pending_submission.serialize())


def propagate_pending_submission(programme: ProgrammeDTO, reporting_round: int) -> None:
    _propagate_pending_submission(programme, reporting_round)
