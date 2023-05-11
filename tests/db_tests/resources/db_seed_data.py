import datetime
import uuid

import core.const as enums

uid = {f"uuid{i}": uuid.uuid4() for i in range(1, 50)}

ORGANISATION_DATA = {
    "id": [uid["uuid1"], uid["uuid2"], uid["uuid3"]],
    "organisation_name": ["Test Organisation", "Test Organisation 2", "Test Organisation 3"],
    "geography": ["Earth", "Mars", "Venus"],
}


CONTACT_DATA = {
    "id": [uid["uuid4"], uid["uuid5"], uid["uuid6"]],
    "email_address": ["jane@example.com", "john@example.com", "joe@example.com"],
    "contact_name": ["Jane Doe", "John Doe", "Joe Bloggs"],
    "telephone": ["123", "789", "334"],
    "organisation_id": [uid["uuid1"], uid["uuid1"], uid["uuid3"]],
}

PACKAGE_DATA = {
    "id": [uid["uuid7"], uid["uuid8"], uid["uuid9"]],
    "package_name": ["Regeneration Project", "North Eastern Scheme", "Southern Access Project"],
    "package_id": ["ABC00123", "GHSG001", "ABC05678"],
    "fund_type_id": ["HIJ", "LMN", "OPQR"],
    "organisation_id": [uid["uuid1"], uid["uuid2"], uid["uuid3"]],
    "name_contact_id": [uid["uuid4"], uid["uuid5"], uid["uuid6"]],
    "project_sro_contact_id": [uid["uuid4"], uid["uuid5"], uid["uuid6"]],
    "cfo_contact_id": [uid["uuid4"], uid["uuid5"], uid["uuid6"]],
    "m_and_e_contact_id": [uid["uuid4"], uid["uuid5"], uid["uuid6"]],
}

PROJECT_DATA = {
    "id": [uid["uuid10"], uid["uuid11"], uid["uuid12"]],
    "project_id": ["LUF01891", "LUF01892", "LUF01893"],
    "project_name": ["Project 1", "Project 2", "Project 3"],
    "package_id": [uid["uuid7"], uid["uuid8"], uid["uuid9"]],
    "address": ["SW1A 2AA", "SW1A 2AB", "SW1A 2AC"],
    "secondary_organisation": ["Org 1", "Org 2", "Org 3"],
}

PROJECT_DELIVERY_PLAN_DATA = {
    "id": [uid["uuid13"], uid["uuid14"], uid["uuid15"]],
    "milestone": ["Project start and finish date", "Project start and finish date", "Key Risk Ratings"],
    "project_id": [uid["uuid10"], uid["uuid11"], uid["uuid12"]],
    "start_date": [datetime.date(2021, 4, 1), datetime.date(2022, 11, 3), datetime.date(2023, 1, 14)],
    "end_date": [datetime.date(2022, 3, 20), datetime.date(2023, 3, 10), datetime.date(2024, 1, 13)],
    "status": [enums.StatusEnum.NOT_YET_STARTED, enums.StatusEnum.ONGOING_DELAYED, enums.StatusEnum.OTHER],
    "comments": [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua",
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    ],
}

PROCUREMENT_DATA = {
    "id": [uid["uuid16"], uid["uuid17"], uid["uuid18"]],
    "construction_contract": ["Contract_1", "Contract_2", "Contract_3"],
    "project_id": [uid["uuid10"], uid["uuid11"], uid["uuid12"]],
    "start_date": [datetime.date(2021, 4, 1), datetime.date(2022, 11, 3), datetime.date(2023, 1, 14)],
    "end_date": [datetime.date(2022, 3, 20), datetime.date(2023, 3, 10), datetime.date(2024, 1, 13)],
    "status": [enums.StatusEnum.COMPLETED, enums.StatusEnum.NOT_YET_STARTED, enums.StatusEnum.ONGOING_DELAYED],
    "procurement_status": [
        enums.ProcurementStatusEnum.AWARDING_OF_CONSTRUCTION_CONTRACT,
        enums.ProcurementStatusEnum.EVALUATION_OF_TENDERS,
        enums.ProcurementStatusEnum.PUBLICATION_OF_ITT,
    ],
    "comments": [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua",
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    ],
}

PROJECT_PROGRESS_DATA = {
    "id": [uid["uuid19"], uid["uuid20"], uid["uuid21"]],
    "package_id": [uid["uuid7"], uid["uuid8"], uid["uuid9"]],
    "answer_1": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "answer_2": "sed do eiusmod tempor incididunt ut labore et dolore magna",
    "answer_3": "Ut enim ad minim veniam, quis nostrud exercitation ullamco.",
    "answer_4": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
    "answer_5": "sed do eiusmod tempor incididunt ut labore et dolore magna",
    "answer_6": "Ut enim ad minim veniam, quis nostrud exercitation ullamco.",
}

DIRECT_FUND_DATA = {
    "id": [uid["uuid22"], uid["uuid23"], uid["uuid24"]],
    "project_id": [uid["uuid10"], uid["uuid11"], uid["uuid12"]],
    "start_date": [datetime.date(2021, 4, 1), datetime.date(2022, 11, 3), datetime.date(2023, 1, 14)],
    "end_date": [datetime.date(2022, 3, 20), datetime.date(2023, 3, 10), datetime.date(2024, 1, 13)],
    "state": [enums.StateEnum.ACTUAL, enums.StateEnum.FORECAST, enums.StateEnum.FORECAST],
    "amount": [1000000.00, 12345678.00, 0.00],
    "pra_or_other": [enums.PRAEnum.OTHER, enums.PRAEnum.PRA, enums.PRAEnum.OTHER],
    "contractually_committed_amount": [1000000.00, 12345678.00, 0.00],
}

CAPITAL_DATA = {
    "id": [uid["uuid25"], uid["uuid26"], uid["uuid27"]],
    "project_id": [uid["uuid10"], uid["uuid11"], uid["uuid12"]],
    "start_date": [datetime.date(2021, 4, 1), datetime.date(2022, 11, 3), datetime.date(2023, 1, 14)],
    "end_date": [datetime.date(2022, 3, 20), datetime.date(2023, 3, 10), datetime.date(2024, 1, 13)],
    "state": [enums.StateEnum.ACTUAL, enums.StateEnum.FORECAST, enums.StateEnum.FORECAST],
    "amount": [2, 000, 000.00, 0.00, 10, 345, 000.00],
}

INDIRECT_FUND_SECURED_DATA = {
    "id": [uid["uuid28"], uid["uuid29"], uid["uuid30"]],
    "project_id": [uid["uuid10"], uid["uuid11"], uid["uuid12"]],
    "start_date": [datetime.date(2021, 4, 1), datetime.date(2022, 11, 3), datetime.date(2023, 1, 14)],
    "end_date": [datetime.date(2022, 3, 20), datetime.date(2023, 3, 10), datetime.date(2024, 1, 13)],
    "funding_source_name": ["Local Authority", "Private Funding", "Local Authority"],
    "funding_source_category": [
        enums.FundingSourceCategoryEnum.LOCAL_AUTHORITY,
        enums.FundingSourceCategoryEnum.OTHER_PUBLIC_FUNDING,
        enums.FundingSourceCategoryEnum.THIRD_SECTOR_FUNDING,
    ],
    "state": [enums.StateEnum.ACTUAL, enums.StateEnum.FORECAST, enums.StateEnum.FORECAST],
    "amount": ["£0.00", "£1,000,000", "£12,345,678.00"],
}

INDIRECT_FUND_UNSECURED_DATA = {
    "id": [uid["uuid31"], uid["uuid32"], uid["uuid33"]],
    "project_id": [uid["uuid10"], uid["uuid11"], uid["uuid12"]],
    "start_date": [datetime.date(2021, 4, 1), datetime.date(2022, 11, 3), datetime.date(2023, 1, 14)],
    "end_date": [datetime.date(2022, 3, 20), datetime.date(2023, 3, 10), datetime.date(2024, 1, 13)],
    "funding_source_name": ["Private Funding", "Local Authority", "Private Funding"],
    "funding_source_category": [
        enums.FundingSourceCategoryEnum.THIRD_SECTOR_FUNDING,
        enums.FundingSourceCategoryEnum.OTHER_PUBLIC_FUNDING,
        enums.FundingSourceCategoryEnum.THIRD_SECTOR_FUNDING,
    ],
    "state": [enums.StateEnum.ACTUAL, enums.StateEnum.FORECAST, enums.StateEnum.FORECAST],
    "amount": ["£1,000,000", "£12,345,678.00", "£0.00"],
    "current_status": ["1. Not yet started", "2. Ongoing - on track", "3. Ongoing - at risk"],
    "comments": [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua",
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    ],
    "potential_secure_date": ["01/04/2021", "11/03/2022", "14/01/2023"],
}

OUTPUT_DATA = {
    "id": [uid["uuid34"], uid["uuid35"], uid["uuid36"]],
    "project_id": [uid["uuid10"], uid["uuid11"], uid["uuid12"]],
    "start_date": [datetime.date(2021, 4, 1), datetime.date(2022, 11, 3), datetime.date(2023, 1, 14)],
    "end_date": [datetime.date(2022, 3, 20), datetime.date(2023, 3, 10), datetime.date(2024, 1, 13)],
    "output_dim_id": [uid["uuid37"], uid["uuid38"], uid["uuid39"]],
    "unit_of_measurement": ["Number of jobs", "Number of jobs", "Number of jobs"],
    "state": [enums.StateEnum.ACTUAL, enums.StateEnum.FORECAST, enums.StateEnum.FORECAST],
    "amount": ["£1,000,000", "£12,345,678.00", "£0.00"],
}

OUTPUT_DIM = {
    "id": [uid["uuid37"], uid["uuid38"], uid["uuid39"]],
    "output_name": [
        "Total length of improved cycle ways",
        "(FTE) permanent jobs safe-guarded",
        "Number of new residential units",
    ],
    "output_category": ["Transport", "Jobs", "Regeneration - Housing"],
}

OUTCOME_DATA = {
    "id": [uid["uuid40"], uid["uuid41"], uid["uuid42"]],
    "project_id": [uid["uuid10"], uid["uuid11"], uid["uuid12"]],
    "start_date": [datetime.date(2021, 4, 1), datetime.date(2022, 11, 3), datetime.date(2023, 1, 14)],
    "end_date": [datetime.date(2022, 3, 20), datetime.date(2023, 3, 10), datetime.date(2024, 1, 13)],
    "outcome_dim_id": [uid["uuid43"], uid["uuid44"], uid["uuid45"]],
    "unit_of_measurement": [
        "Year on Year % Change in Monthly Footfall",
        "Year on Year % Change in Monthly Footfall",
        "Year on Year % Change in Monthly Footfall",
    ],
    "geography_indicator": [
        enums.GeographyIndicatorEnum.LOCAL_AUTHORITY,
        enums.GeographyIndicatorEnum.LARGER_THAN_TOWN_OR_LA,
        enums.GeographyIndicatorEnum.LOCATIONS_PROVIDED_ELSEWHERE,
    ],
    "amount": ["-64%", "-39%", "17%"],
    "state": [enums.StateEnum.ACTUAL, enums.StateEnum.FORECAST, enums.StateEnum.FORECAST],
}

OUTCOME_DIM = {
    "id": [uid["uuid43"], uid["uuid44"], uid["uuid45"]],
    "outcome_name": [
        "Air quality - NO2 concentrations",
        "Auidence numbers for cultural events",
        "Average (mean) anxiety ratings",
    ],
    "outcome_category": ["Transport", "Culture", "Health"],
}

RISK_REGISTER_DATA = {
    "id": [uid["uuid46"], uid["uuid47"], uid["uuid48"]],
    "project_id": [uid["uuid10"], uid["uuid11"], uid["uuid12"]],
    "risk_name": ["Capital Cost", "Demand Risk", "Cost and availability of materials"],
    "risk_category": ["Rising Costs", "Ineffective Culture", "Geopolitical, Environmental or Economic Shock"],
    "short_desc": ["Lorem ipsum dolor sit amet.", "sed do eiusmod tempor incididunt", "Ut enim ad minim veniam."],
    "full_desc": [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit, sed do eiusmod tempor incididunt.",
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo.",
        "Duis aute irure dolor in reprehenderit in voluptate velit esse cillum dolore eu fugiat nulla.",
    ],
    "consequences": [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua",
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    ],
    "pre_mitigated_impact": [enums.ImpactEnum.MARGINAL, enums.ImpactEnum.LOW, enums.ImpactEnum.SIGNIFICANT],
    "pre_mitigated_likelihood": [enums.LikelihoodEnum.LOW, enums.LikelihoodEnum.MEDIUM, enums.LikelihoodEnum.HIGH],
    "mitigations": [
        "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        "sed do eiusmod tempor incididunt ut labore et dolore magna aliqua",
        "Ut enim ad minim veniam, quis nostrud exercitation ullamco laboris nisi ut aliquip ex ea commodo consequat.",
    ],
    "post_mitigated_impact": [enums.ImpactEnum.CRITICAL, enums.ImpactEnum.MAJOR, enums.ImpactEnum.LOW],
    "post_mitigated_likelihood": [enums.LikelihoodEnum.LOW, enums.LikelihoodEnum.MEDIUM, enums.LikelihoodEnum.HIGH],
    "proximity": [enums.ProximityEnum.REMOTE, enums.ProximityEnum.DISTANT, enums.ProximityEnum.CLOSE],
    "risk_owner_role": ["Jane Doe - SRO", "Jane Doe, Head of Property Services", "Jane Doe General Manager"],
}
