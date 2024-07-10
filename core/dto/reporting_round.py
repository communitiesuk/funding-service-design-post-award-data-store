from __future__ import annotations

import datetime
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from core.db.entities import ReportingRound

if TYPE_CHECKING:
    from core.dto.fund import FundDTO


@dataclass
class ReportingRoundDTO:
    id: str
    round_number: int
    fund_id: str
    reporting_period_start: datetime.datetime
    reporting_period_end: datetime.datetime
    submission_window_start: datetime.datetime
    submission_window_end: datetime.datetime

    @cached_property
    def fund(self) -> "FundDTO":
        from core.dto.fund import get_fund_by_id

        return get_fund_by_id(self.fund_id)


def get_reporting_round_by_id(reporting_round_id: str) -> ReportingRoundDTO:
    reporting_round: ReportingRound = ReportingRound.query.get(reporting_round_id)
    return ReportingRoundDTO(
        id=str(reporting_round.id),
        round_number=reporting_round.round_number,
        fund_id=str(reporting_round.fund_id),
        reporting_period_start=reporting_round.reporting_period_start,
        reporting_period_end=reporting_round.reporting_period_end,
        submission_window_start=reporting_round.submission_window_start,
        submission_window_end=reporting_round.submission_window_end,
    )


def get_reporting_rounds_by_ids(reporting_round_ids: list[str]) -> list[ReportingRoundDTO]:
    reporting_rounds = ReportingRound.query.filter(ReportingRound.id.in_(reporting_round_ids)).all()
    return [get_reporting_round_by_id(reporting_round.id) for reporting_round in reporting_rounds]
