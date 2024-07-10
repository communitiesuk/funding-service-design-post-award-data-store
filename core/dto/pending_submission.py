from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from core.db import db
from core.db.entities import PendingSubmission

if TYPE_CHECKING:
    from core.dto.programme import ProgrammeDTO
    from core.dto.reporting_round import ReportingRoundDTO


@dataclass
class PendingSubmissionDTO:
    id: str
    programme_id: str
    reporting_round_id: int
    data_blob: str

    @cached_property
    def programme(self) -> "ProgrammeDTO":
        from core.dto.programme import get_programme_by_id

        return get_programme_by_id(self.programme_id)

    @cached_property
    def reporting_round(self) -> "ReportingRoundDTO":
        from core.dto.reporting_round import get_reporting_round_by_id

        return get_reporting_round_by_id(self.reporting_round_id)


def _entity_to_dto(pending_submission: PendingSubmission) -> PendingSubmissionDTO:
    return PendingSubmissionDTO(
        id=str(pending_submission.id),
        programme_id=str(pending_submission.programme_id),
        reporting_round_id=pending_submission.reporting_round_id,
        data_blob=pending_submission.data_blob,
    )


def get_pending_submission_by_id(pending_submission_id: str) -> PendingSubmissionDTO:
    pending_submission: PendingSubmission = PendingSubmission.query.get(pending_submission_id)
    return _entity_to_dto(pending_submission)


def get_pending_submissions_by_ids(pending_submission_ids: list[str]) -> list[PendingSubmissionDTO]:
    return [get_pending_submission_by_id(pending_submission_id) for pending_submission_id in pending_submission_ids]


def get_pending_submission(
    programme_dto: ProgrammeDTO | None, reporting_round_dto: ReportingRoundDTO
) -> PendingSubmissionDTO | None:
    pending_submission = PendingSubmission.query.filter_by(
        programme_id=programme_dto.id, reporting_round_id=reporting_round_dto.id
    ).first()
    if pending_submission:
        return _entity_to_dto(pending_submission)
    return None


def persist_pending_submission(
    programme_dto: ProgrammeDTO, reporting_round_dto: ReportingRoundDTO, data_blob: dict
) -> None:
    pending_submission_dto = get_pending_submission(programme_dto, reporting_round_dto)
    if pending_submission_dto:
        pending_submission: PendingSubmission = PendingSubmission.query.get(pending_submission_dto.id)
        pending_submission.data_blob = data_blob
    else:
        pending_submission = PendingSubmission(
            programme_id=programme_dto.id,
            reporting_round_id=reporting_round_dto.id,
            data_blob=data_blob,
        )
        db.session.add(pending_submission)
    db.session.commit()
