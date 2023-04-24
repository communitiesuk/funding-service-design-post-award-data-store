"""Module of constants."""
from collections import namedtuple
from enum import StrEnum

LookupArgs = namedtuple("fk_lookup_args", ["fk_primary", "related_table", "pk_related"])


class StatusEnum(StrEnum):
    NOT_YET_STARTED = "1. Not yet started"
    ONGOING_ON_TRACK = "2. Ongoing - on track"
    ONGOING_DELAYED = "3. Ongoing - delayed"
    COMPLETED = "4. Completed"
    OTHER = "5. Other"


class ProcurementStatusEnum(StrEnum):
    PUBLICATION_OF_ITT = "1. Publication of ITT"
    EVALUATION_OF_TENDERS = "2. Evaluation of Tenders"
    AWARDING_OF_CONSTRUCTION_CONTRACT = "3. Awarding of Construction Contract"
    SIGNING_OF_CONSTRUCTION_CONTRACT = "4. Signing of Construction Contract"


class StateEnum(StrEnum):
    ACTUAL = "Actual"
    FORECAST = "Forecast"


class PRAEnum(StrEnum):
    PRA = "PRA"
    OTHER = "Other"


class FundingSourceCategoryEnum(StrEnum):
    LOCAL_AUTHORITY = "Local Authority"
    THIRD_SECTOR_FUNDING = "Third Sector Funding"
    OTHER_PUBLIC_FUNDING = "Other Public Funding"
    PRIVATE_FUNDING = "Private Funding"


class GeographyIndicatorEnum(StrEnum):
    TRAVEL_CORRIDOR = "Travel corridor"
    LOCATIONS_PROVIDED_ELSEWHERE = "Locations provided in 'Project Admin' tab"
    OUTPUT_AREA = "Output area"
    LOWER_LAYER_SUPER_OUTPUT_AREA = "Lower layer super output area"
    MIDDLE_LAYER_SUPER_OUTPUT_AREA = "Middle layer super output area"
    TOWN = "Town"
    LOCAL_AUTHORITY = "Local Authority"
    LARGER_THAN_TOWN_OR_LA = "Larger than Town or Local Authority"
    OTHER = "Other / Custom Geography"


class ImpactEnum(StrEnum):
    MARGINAL = "1. Marginal Impact"
    LOW = "2. Low Impact"
    MEDIUM = "3. Medium Impact"
    SIGNIFICANT = "4. Significant Impact"
    MAJOR = "5. Major Impact"
    CRITICAL = "6. Critical Impact"


class LikelihoodEnum(StrEnum):
    LOW = "1. Low"
    MEDIUM = "2. Medium"
    HIGH = "3. High"


class ProximityEnum(StrEnum):
    REMOTE = "1. Remote"
    DISTANT = "2. Distant: next 12 months"
    APPROACHING = "3. Approaching: next 6 months"
    CLOSE = "4. Close: next 3 months"
    IMMINENT = "5. Imminent: next month"
