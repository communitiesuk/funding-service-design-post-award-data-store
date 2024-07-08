from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from core.db import db
from core.db.entities import PendingSubmission

if TYPE_CHECKING:
    from core.dto.programme import ProgrammeDTO


@dataclass
class PendingSubmissionDTO:
    id: str
    programme_id: str
    reporting_round: int
    data_blob: str

    @cached_property
    def programme(self) -> "ProgrammeDTO" | None:
        from core.dto.programme import get_programme_by_id

        if not self.programme_id:
            return None
        return get_programme_by_id(self.programme_id)


def get_pending_submission_by_id(pending_submission_id: str) -> PendingSubmissionDTO:
    pending_submission: PendingSubmission = PendingSubmission.query.get(pending_submission_id)
    return PendingSubmissionDTO(
        id=str(pending_submission.id),
        programme_id=str(pending_submission.programme_id),
        reporting_round=pending_submission.reporting_round,
        data_blob=pending_submission.data_blob,
    )


def get_pending_submissions_by_ids(pending_submission_ids: list[str]) -> list[PendingSubmissionDTO]:
    return [get_pending_submission_by_id(pending_submission_id) for pending_submission_id in pending_submission_ids]


def get_pending_submission(programme_dto: ProgrammeDTO | None, reporting_round: int) -> PendingSubmissionDTO | None:
    if programme_dto:
        for pending_submission_dto in programme_dto.pending_submissions:
            if pending_submission_dto.reporting_round == reporting_round:
                return pending_submission_dto
    return None


def persist_pending_submission(programme_dto: ProgrammeDTO, reporting_round: int, data_blob: dict) -> None:
    dto_for_reporting_round = None
    for pending_submission_dto in programme_dto.pending_submissions:
        if pending_submission_dto.reporting_round == reporting_round:
            dto_for_reporting_round = pending_submission_dto
            break
    if dto_for_reporting_round:
        pending_submission: PendingSubmission = PendingSubmission.query.get(dto_for_reporting_round.id)
        pending_submission.data_blob = data_blob
    else:
        pending_submission = PendingSubmission(
            programme_id=programme_dto.id,
            reporting_round=reporting_round,
            data_blob=data_blob,
        )
        db.session.add(pending_submission)
    db.session.commit()
