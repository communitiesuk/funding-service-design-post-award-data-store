from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from core.db.entities import PendingSubmission

if TYPE_CHECKING:
    from core.dto.programme import ProgrammeDTO


@dataclass
class PendingSubmissionDTO:
    id: str
    programme_id: str
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
        data_blob=pending_submission.data_blob,
    )


def get_pending_submissions_by_ids(pending_submission_ids: list[str]) -> list[PendingSubmissionDTO]:
    return [get_pending_submission_by_id(pending_submission_id) for pending_submission_id in pending_submission_ids]
