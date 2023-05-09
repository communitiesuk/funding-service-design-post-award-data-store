# flake8: noqa
MOCK_PACKAGE_RESPONSE = {
    "cfo_contact": {
        "contact_name": "Jane Doe",
        "email_address": "jane.doe2@example.gov.uk",
        "organisation": {"geography": "", "organisation_name": "Fake Council Name"},
        "telephone": "123456789",
    },
    "m_and_e_contact": {
        "contact_name": "Jane Doe",
        "email_address": "jane.doe2@example.gov.uk",
        "organisation": {"geography": "", "organisation_name": "Fake Council Name"},
        "telephone": "123456789",
    },
    "name_contact": {
        "contact_name": "Jane Doe",
        "email_address": "jane.doe2@example.gov.uk",
        "organisation": {"geography": "", "organisation_name": "Fake Council Name"},
        "telephone": "123456789",
    },
    "organisation": {"geography": "", "organisation_name": "Fake Council Name"},
    "package_name": "Leaky Cauldron regeneration",
    "progress_records": [
        {
            "answer_1": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "answer_2": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "answer_3": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "answer_4": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "answer_5": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
            "answer_6": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
        }
    ],
    "project_sro_contact": {
        "contact_name": "Jane Doe",
        "email_address": "jane.doe2@example.gov.uk",
        "organisation": {"geography": "", "organisation_name": "Fake Council Name"},
        "telephone": "123456789",
    },
    "projects": [
        {
            "address": "SW1A 2AA",
            "capital_records": [
                {
                    "amount": 123.0,
                    "end_date": "2020-09-30T00:00:00Z",
                    "start_date": "2020-04-01T00:00:00Z",
                    "state": "Actual",
                }
            ],
            "direct_funds": [
                {
                    "amount": 0.0,
                    "contractually_committed_amount": 0.0,
                    "end_date": "2021-03-31T00:00:00Z",
                    "pra_or_other": "PRA",
                    "start_date": "2020-10-01T00:00:00Z",
                    "state": "Actual",
                },
                {
                    "amount": 12345678.0,
                    "contractually_committed_amount": 12345678.0,
                    "end_date": "2021-09-30T00:00:00Z",
                    "pra_or_other": "PRA",
                    "start_date": "2021-04-01T00:00:00Z",
                    "state": "Actual",
                },
            ],
            "indirect_funds_secured": [
                {
                    "amount": 1234567.0,
                    "end_date": "2022-03-31T00:00:00Z",
                    "funding_source_category": "Local Authority",
                    "funding_source_name": "Gotham City Council",
                    "start_date": "2021-10-01T00:00:00Z",
                    "state": "Actual",
                },
                {
                    "amount": 1234567.0,
                    "end_date": "2022-09-30T00:00:00Z",
                    "funding_source_category": "Local Authority",
                    "funding_source_name": "Gotham City Council",
                    "start_date": "2022-04-01T00:00:00Z",
                    "state": "Forecast",
                },
            ],
            "indirect_funds_unsecured": [
                {
                    "amount": 0.0,
                    "comments": "",
                    "current_status": "",
                    "end_date": "2021-06-30T00:00:00Z",
                    "funding_source_category": "Private Funding",
                    "funding_source_name": "Private Funding",
                    "potential_secure_date": None,
                    "start_date": "2021-04-01T00:00:00Z",
                    "state": "Actual",
                },
                {
                    "amount": 1234567.0,
                    "comments": "",
                    "current_status": "",
                    "end_date": "2022-06-30T00:00:00Z",
                    "funding_source_category": "Private Funding",
                    "funding_source_name": "Private Funding",
                    "potential_secure_date": None,
                    "start_date": "2022-04-01T00:00:00Z",
                    "state": "Forecast",
                },
            ],
            "outcomes": [
                {
                    "amount": 0.0,
                    "end_date": "2020-04-30T00:00:00Z",
                    "geography_indicator": "Town",
                    "outcome_dim": {
                        "outcome_category": "Place",
                        "outcome_name": "Year on Year % Change in Monthly Footfall",
                    },
                    "start_date": "2020-04-01T00:00:00Z",
                    "state": "Actual",
                    "unit_of_measurement": "Year on Year % Change in Monthly Footfall",
                },
                {
                    "amount": 0.0,
                    "end_date": "2020-05-31T00:00:00Z",
                    "geography_indicator": "Town",
                    "outcome_dim": {
                        "outcome_category": "Place",
                        "outcome_name": "Year on Year % Change in Monthly Footfall",
                    },
                    "start_date": "2020-05-01T00:00:00Z",
                    "state": "Actual",
                    "unit_of_measurement": "Year on Year % Change in Monthly Footfall",
                },
            ],
            "outputs": [
                {
                    "amount": 0.0,
                    "end_date": "2020-09-30T00:00:00Z",
                    "output_dim": {"output_category": "Jobs", "output_name": "#of temporary FT jobs supported"},
                    "start_date": "2020-04-01T00:00:00Z",
                    "state": "Actual",
                    "unit_of_measurement": "Number of jobs",
                },
                {
                    "amount": 0.0,
                    "end_date": "2020-10-30T00:00:00Z",
                    "output_dim": {"output_category": "Jobs", "output_name": " (FTE) permanent jobs created"},
                    "start_date": "2020-04-02T00:00:00Z",
                    "state": "Forecast",
                    "unit_of_measurement": "Number of jobs",
                },
                {
                    "amount": 0.0,
                    "end_date": "2021-03-31T00:00:00Z",
                    "output_dim": {"output_category": "Jobs", "output_name": " (FTE) permanent jobs safe-guarded"},
                    "start_date": "2020-10-01T00:00:00Z",
                    "state": "Actual",
                    "unit_of_measurement": "Number of jobs",
                },
                {
                    "amount": 0.0,
                    "end_date": "2026-03-31T00:00:00Z",
                    "output_dim": {
                        "output_category": "test field - missing data",
                        "output_name": "# of heritage buildings renovated/restored",
                    },
                    "start_date": "2025-10-01T00:00:00Z",
                    "state": "Forecast",
                    "unit_of_measurement": "Number of buildings",
                },
            ],
            "procurement_contracts": [
                {
                    "comments": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "construction_contract": "Contract_1",
                    "end_date": "2022-03-01T00:00:00Z",
                    "procurement_status": "1. Publication of ITT",
                    "start_date": "2022-01-01T00:00:00Z",
                    "status": "3. Ongoing - delayed",
                }
            ],
            "project_delivery_plans": [
                {
                    "comments": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "end_date": "2024-03-31T00:00:00Z",
                    "milestone": "Project start and finish date",
                    "start_date": "2017-10-01T00:00:00Z",
                    "status": "2. Ongoing - on track",
                },
                {
                    "comments": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "end_date": "2024-03-31T00:00:00Z",
                    "milestone": "Key Risk Ratings",
                    "start_date": "2017-10-01T00:00:00Z",
                    "status": "2. Ongoing - on track",
                },
            ],
            "project_name": "Three Broomsticks regeneration",
            "risks": [
                {
                    "consequences": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "full_desc": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. 1",
                    "mitigations": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mitigation 9",
                    "post_mitigated_impact": "3. Medium Impact",
                    "post_mitigated_likelihood": "1. Low",
                    "pre_mitigated_impact": "4. Significant Impact",
                    "pre_mitigated_likelihood": "3. High",
                    "proximity": "3. Approaching: next 6 months",
                    "risk_category": "Rising Costs",
                    "risk_name": "Cost and availability of materials",
                    "risk_owner_role": "Jane Doe, Head of Property Services",
                    "short_desc": "Lorem Ipsum",
                },
                {
                    "consequences": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "full_desc": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. 3",
                    "mitigations": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mitigation 11",
                    "post_mitigated_impact": "2. Low Impact",
                    "post_mitigated_likelihood": "2. Medium",
                    "pre_mitigated_impact": "3. Medium Impact",
                    "pre_mitigated_likelihood": "3. High",
                    "proximity": "2. Distant: next 12 months",
                    "risk_category": "Reputational Risk",
                    "risk_name": "Impact on surrounding area",
                    "risk_owner_role": "Jane Doe- Project Manager",
                    "short_desc": "Lorem Ipsum",
                },
                {
                    "consequences": "Lorem ipsum dolor sit amet, consectetur adipiscing elit.",
                    "full_desc": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. 2",
                    "mitigations": "Lorem ipsum dolor sit amet, consectetur adipiscing elit. Mitigation 10",
                    "post_mitigated_impact": "3. Medium Impact",
                    "post_mitigated_likelihood": "1. Low",
                    "pre_mitigated_impact": "3. Medium Impact",
                    "pre_mitigated_likelihood": "2. Medium",
                    "proximity": "1. Remote",
                    "risk_category": "Premises & Estate Management",
                    "risk_name": "Occupancy levels",
                    "risk_owner_role": "Jane Doe General Manager",
                    "short_desc": "Lorem Ipsum",
                },
            ],
            "secondary_organisation": "",
        }
    ],
}

MOCK_PROJECT_RESPONSE = {
    "address": "SW1A 2AA",
    "capital_records": [
        {"amount": 123.0, "end_date": "2020-09-30T00:00:00Z", "start_date": "2020-04-01T00:00:00Z", "state": "Actual"}
    ],
    "direct_funds": [
        {
            "amount": 0.0,
            "contractually_committed_amount": 0.0,
            "end_date": "2021-03-31T00:00:00Z",
            "pra_or_other": "PRA",
            "start_date": "2020-10-01T00:00:00Z",
            "state": "Actual",
        },
        {
            "amount": 12345678.0,
            "contractually_committed_amount": 12345678.0,
            "end_date": "2021-09-30T00:00:00Z",
            "pra_or_other": "PRA",
            "start_date": "2021-04-01T00:00:00Z",
            "state": "Actual",
        },
    ],
    "indirect_funds_secured": [
        {
            "amount": 1234567.0,
            "end_date": "2022-03-31T00:00:00Z",
            "funding_source_category": "Local Authority",
            "funding_source_name": "Gotham City Council",
            "start_date": "2021-10-01T00:00:00Z",
            "state": "Actual",
        },
        {
            "amount": 1234567.0,
            "end_date": "2022-09-30T00:00:00Z",
            "funding_source_category": "Local Authority",
            "funding_source_name": "Gotham City Council",
            "start_date": "2022-04-01T00:00:00Z",
            "state": "Forecast",
        },
    ],
    "indirect_funds_unsecured": [
        {
            "amount": 0.0,
            "comments": "",
            "current_status": "",
            "end_date": "2021-06-30T00:00:00Z",
            "funding_source_category": "Private Funding",
            "funding_source_name": "Private Funding",
            "potential_secure_date": None,
            "start_date": "2021-04-01T00:00:00Z",
            "state": "Actual",
        },
        {
            "amount": 1234567.0,
            "comments": "",
            "current_status": "",
            "end_date": "2022-06-30T00:00:00Z",
            "funding_source_category": "Private Funding",
            "funding_source_name": "Private Funding",
            "potential_secure_date": None,
            "start_date": "2022-04-01T00:00:00Z",
            "state": "Forecast",
        },
    ],
    "outcomes": [
        {
            "amount": 0.0,
            "end_date": "2020-04-30T00:00:00Z",
            "geography_indicator": "Town",
            "outcome_dim": {
                "outcome_category": "Place",
                "outcome_name": "Year on Year % Change in " "Monthly Footfall",
            },
            "start_date": "2020-04-01T00:00:00Z",
            "state": "Actual",
            "unit_of_measurement": "Year on Year % Change in Monthly " "Footfall",
        },
        {
            "amount": 0.0,
            "end_date": "2020-05-31T00:00:00Z",
            "geography_indicator": "Town",
            "outcome_dim": {
                "outcome_category": "Place",
                "outcome_name": "Year on Year % Change in " "Monthly Footfall",
            },
            "start_date": "2020-05-01T00:00:00Z",
            "state": "Actual",
            "unit_of_measurement": "Year on Year % Change in Monthly " "Footfall",
        },
    ],
    "outputs": [
        {
            "amount": 0.0,
            "end_date": "2020-09-30T00:00:00Z",
            "output_dim": {"output_category": "Jobs", "output_name": "#of temporary FT jobs supported"},
            "start_date": "2020-04-01T00:00:00Z",
            "state": "Actual",
            "unit_of_measurement": "Number of jobs",
        },
        {
            "amount": 0.0,
            "end_date": "2020-10-30T00:00:00Z",
            "output_dim": {"output_category": "Jobs", "output_name": " (FTE) permanent jobs created"},
            "start_date": "2020-04-02T00:00:00Z",
            "state": "Forecast",
            "unit_of_measurement": "Number of jobs",
        },
        {
            "amount": 0.0,
            "end_date": "2021-03-31T00:00:00Z",
            "output_dim": {"output_category": "Jobs", "output_name": " (FTE) permanent jobs " "safe-guarded"},
            "start_date": "2020-10-01T00:00:00Z",
            "state": "Actual",
            "unit_of_measurement": "Number of jobs",
        },
        {
            "amount": 0.0,
            "end_date": "2026-03-31T00:00:00Z",
            "output_dim": {
                "output_category": "test field - missing data",
                "output_name": "# of heritage buildings " "renovated/restored",
            },
            "start_date": "2025-10-01T00:00:00Z",
            "state": "Forecast",
            "unit_of_measurement": "Number of buildings",
        },
    ],
    "procurement_contracts": [
        {
            "comments": "Lorem ipsum dolor sit amet, " "consectetur adipiscing elit.",
            "construction_contract": "Contract_1",
            "end_date": "2022-03-01T00:00:00Z",
            "procurement_status": "1. Publication of ITT",
            "start_date": "2022-01-01T00:00:00Z",
            "status": "3. Ongoing - delayed",
        }
    ],
    "project_delivery_plans": [
        {
            "comments": "Lorem ipsum dolor sit amet, " "consectetur adipiscing elit.",
            "end_date": "2024-03-31T00:00:00Z",
            "milestone": "Project start and finish date",
            "start_date": "2017-10-01T00:00:00Z",
            "status": "2. Ongoing - on track",
        },
        {
            "comments": "Lorem ipsum dolor sit amet, " "consectetur adipiscing elit.",
            "end_date": "2024-03-31T00:00:00Z",
            "milestone": "Key Risk Ratings",
            "start_date": "2017-10-01T00:00:00Z",
            "status": "2. Ongoing - on track",
        },
    ],
    "project_name": "Three Broomsticks regeneration",
    "risks": [
        {
            "consequences": "Lorem ipsum dolor sit amet, consectetur " "adipiscing elit.",
            "full_desc": "Lorem ipsum dolor sit amet, consectetur adipiscing " "elit. 1",
            "mitigations": "Lorem ipsum dolor sit amet, consectetur adipiscing " "elit. Mitigation 9",
            "post_mitigated_impact": "3. Medium Impact",
            "post_mitigated_likelihood": "1. Low",
            "pre_mitigated_impact": "4. Significant Impact",
            "pre_mitigated_likelihood": "3. High",
            "proximity": "3. Approaching: next 6 months",
            "risk_category": "Rising Costs",
            "risk_name": "Cost and availability of materials",
            "risk_owner_role": "Jane Doe, Head of Property Services",
            "short_desc": "Lorem Ipsum",
        },
        {
            "consequences": "Lorem ipsum dolor sit amet, consectetur " "adipiscing elit.",
            "full_desc": "Lorem ipsum dolor sit amet, consectetur adipiscing " "elit. 3",
            "mitigations": "Lorem ipsum dolor sit amet, consectetur adipiscing " "elit. Mitigation 11",
            "post_mitigated_impact": "2. Low Impact",
            "post_mitigated_likelihood": "2. Medium",
            "pre_mitigated_impact": "3. Medium Impact",
            "pre_mitigated_likelihood": "3. High",
            "proximity": "2. Distant: next 12 months",
            "risk_category": "Reputational Risk",
            "risk_name": "Impact on surrounding area",
            "risk_owner_role": "Jane Doe- Project Manager",
            "short_desc": "Lorem Ipsum",
        },
        {
            "consequences": "Lorem ipsum dolor sit amet, consectetur " "adipiscing elit.",
            "full_desc": "Lorem ipsum dolor sit amet, consectetur adipiscing " "elit. 2",
            "mitigations": "Lorem ipsum dolor sit amet, consectetur adipiscing " "elit. Mitigation 10",
            "post_mitigated_impact": "3. Medium Impact",
            "post_mitigated_likelihood": "1. Low",
            "pre_mitigated_impact": "3. Medium Impact",
            "pre_mitigated_likelihood": "2. Medium",
            "proximity": "1. Remote",
            "risk_category": "Premises & Estate Management",
            "risk_name": "Occupancy levels",
            "risk_owner_role": "Jane Doe General Manager",
            "short_desc": "Lorem Ipsum",
        },
    ],
    "secondary_organisation": "",
}
