from __future__ import annotations

import datetime
from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from core.db.entities import Fund, ReportingRound

if TYPE_CHECKING:
    from core.dto.fund import FundDTO


@dataclass
class ReportingRoundDTO:
    id: str
    round_number: int
    fund_id: str
    observation_period_start: datetime.datetime
    observation_period_end: datetime.datetime
    submission_window_start: datetime.datetime
    submission_window_end: datetime.datetime

    @cached_property
    def fund(self) -> "FundDTO":
        from core.dto.fund import get_fund_by_id

        return get_fund_by_id(self.fund_id)


def _entity_to_dto(reporting_round: ReportingRound) -> ReportingRoundDTO:
    return ReportingRoundDTO(
        id=str(reporting_round.id),
        round_number=reporting_round.round_number,
        fund_id=str(reporting_round.fund_id),
        observation_period_start=reporting_round.observation_period_start,
        observation_period_end=reporting_round.observation_period_end,
        submission_window_start=reporting_round.submission_window_start,
        submission_window_end=reporting_round.submission_window_end,
    )


def get_reporting_round_by_id(reporting_round_id: str) -> ReportingRoundDTO:
    reporting_round: ReportingRound = ReportingRound.query.get(reporting_round_id)
    return _entity_to_dto(reporting_round)


def get_reporting_rounds_by_ids(reporting_round_ids: list[str]) -> list[ReportingRoundDTO]:
    reporting_rounds = ReportingRound.query.filter(ReportingRound.id.in_(reporting_round_ids)).all()
    return [get_reporting_round_by_id(reporting_round.id) for reporting_round in reporting_rounds]


def get_reporting_round_by_fund_slug_and_round_number(fund_slug: str, round_number: int) -> ReportingRoundDTO:
    reporting_round: ReportingRound = (
        ReportingRound.query.join(ReportingRound.fund)
        .filter(ReportingRound.round_number == round_number, Fund.slug == fund_slug)
        .one()
    )
    return _entity_to_dto(reporting_round)
