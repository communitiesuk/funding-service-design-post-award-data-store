from core.db.propagate_raw_submission import propagate_raw_submission as _propagate_raw_submission
from core.dto.programme import ProgrammeDTO
from core.dto.raw_submission import get_raw_submission as _get_raw_submission
from core.dto.raw_submission import persist_raw_submission as _persist_raw_submission
from core.dto.reporting_round import ReportingRoundDTO
from report.persistence.report_blob import ReportBlob
from report.persistence.submission_blob import SubmissionBlob


def get_raw_submission(programme: ProgrammeDTO | None, reporting_round: ReportingRoundDTO) -> SubmissionBlob:
    raw_submission = _get_raw_submission(programme, reporting_round)
    if not raw_submission:
        return SubmissionBlob(
            programme_report=ReportBlob(
                name=programme.organisation.organisation_name,
                sections=[],
            ),
            project_reports={},
        )
    return SubmissionBlob.load_from_json(raw_submission.data_blob)


def persist_raw_submission(
    programme: ProgrammeDTO, reporting_round: ReportingRoundDTO, raw_submission: SubmissionBlob
) -> None:
    _persist_raw_submission(programme, reporting_round, raw_submission.serialize())


def propagate_raw_submission(programme: ProgrammeDTO, reporting_round: ReportingRoundDTO) -> None:
    _propagate_raw_submission(programme, reporting_round)
