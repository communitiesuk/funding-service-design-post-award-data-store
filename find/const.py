from enum import StrEnum


class MIMETYPE(StrEnum):
    XLSX = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    JSON = "application/json"


class InternalDomain(StrEnum):
    COMMUNITIES = "@communities.gov.uk"
    TEST_COMMUNITIES = "@test.communities.gov.uk"
