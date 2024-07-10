from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from core.db import db
from core.db.entities import RawSubmission

if TYPE_CHECKING:
    from core.dto.programme import ProgrammeDTO
    from core.dto.reporting_round import ReportingRoundDTO


@dataclass
class RawSubmissionDTO:
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


def _entity_to_dto(raw_submission: RawSubmission) -> RawSubmissionDTO:
    return RawSubmissionDTO(
        id=str(raw_submission.id),
        programme_id=str(raw_submission.programme_id),
        reporting_round_id=raw_submission.reporting_round_id,
        data_blob=raw_submission.data_blob,
    )


def get_raw_submission_by_id(raw_submission_id: str) -> RawSubmissionDTO:
    raw_submission: RawSubmission = RawSubmission.query.get(raw_submission_id)
    return _entity_to_dto(raw_submission)


def get_raw_submissions_by_ids(raw_submission_ids: list[str]) -> list[RawSubmissionDTO]:
    return [get_raw_submission_by_id(raw_submission_id) for raw_submission_id in raw_submission_ids]


def get_raw_submission(
    programme_dto: ProgrammeDTO | None, reporting_round_dto: ReportingRoundDTO
) -> RawSubmissionDTO | None:
    raw_submission = RawSubmission.query.filter_by(
        programme_id=programme_dto.id, reporting_round_id=reporting_round_dto.id
    ).first()
    if raw_submission:
        return _entity_to_dto(raw_submission)
    return None


def persist_raw_submission(
    programme_dto: ProgrammeDTO, reporting_round_dto: ReportingRoundDTO, data_blob: dict
) -> None:
    raw_submission_dto = get_raw_submission(programme_dto, reporting_round_dto)
    if raw_submission_dto:
        raw_submission: RawSubmission = RawSubmission.query.get(raw_submission_dto.id)
        raw_submission.data_blob = data_blob
    else:
        raw_submission = RawSubmission(
            programme_id=programme_dto.id,
            reporting_round_id=reporting_round_dto.id,
            data_blob=data_blob,
        )
        db.session.add(raw_submission)
    db.session.commit()
