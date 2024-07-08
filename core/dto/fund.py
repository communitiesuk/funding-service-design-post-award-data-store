from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from core.db.entities import Fund

if TYPE_CHECKING:
    from core.dto.programme import ProgrammeDTO


@dataclass
class FundDTO:
    id: str
    fund_code: str
    fund_name: str
    slug: str
    _programme_ids: list[str]

    @cached_property
    def programmes(self) -> list["ProgrammeDTO"]:
        from core.dto.programme import get_programmes_by_ids

        if not self._programme_ids:
            return []
        return get_programmes_by_ids(self._programme_ids)


def get_fund_by_id(fund_id: str) -> FundDTO:
    fund: Fund = Fund.query.get(fund_id)
    programme_ids = [str(programme.id) for programme in fund.programmes]
    return FundDTO(
        id=str(fund.id),
        fund_code=fund.fund_code,
        fund_name=fund.fund_name,
        slug=fund.slug,
        _programme_ids=programme_ids,
    )


def get_funds_by_ids(fund_ids: list[str]) -> list[FundDTO]:
    funds = Fund.query.filter(Fund.id.in_(fund_ids)).all()
    return [get_fund_by_id(fund.id) for fund in funds]
