from __future__ import annotations

from dataclasses import dataclass
from functools import cached_property
from typing import TYPE_CHECKING

from core.db.entities import Organisation

if TYPE_CHECKING:
    from core.dto.programme import ProgrammeDTO


@dataclass
class OrganisationDTO:
    id: str
    organisation_name: str
    slug: str
    geography: str
    _programme_ids: list[str]

    @cached_property
    def programmes(self) -> list["ProgrammeDTO"]:
        from core.dto.programme import get_programmes_by_ids

        return get_programmes_by_ids(self._programme_ids)


def get_organisation_by_id(organisation_id: str) -> OrganisationDTO:
    organisation: Organisation = Organisation.query.get(organisation_id)
    programme_ids = [str(programme.id) for programme in organisation.programmes]
    return OrganisationDTO(
        id=str(organisation.id),
        organisation_name=organisation.organisation_name,
        slug=organisation.slug,
        geography=organisation.geography,
        _programme_ids=programme_ids,
    )


def get_organisations_by_ids(organisation_ids: list[str]) -> list[OrganisationDTO]:
    organisations = Organisation.query.filter(Organisation.id.in_(organisation_ids)).all()
    return [get_organisation_by_id(organisation.id) for organisation in organisations]
