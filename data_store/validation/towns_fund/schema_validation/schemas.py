from datetime import datetime

import data_store.const as enums
from data_store.validation.towns_fund.schema_validation.schema import parse_schema

TF_ROUND_4_VAL_SCHEMA = parse_schema(
    {
        "Submission_Ref": {
            "columns": {
                "submission_date": datetime,
            },
        },
        "Organisation_Ref": {
            "columns": {
                "organisation_name": str,
                "geography": str,
            },
            "uniques": ["organisation_name"],
            "non-nullable": ["organisation_name"],
        },
        "Programme_Ref": {
            "columns": {
                "programme_id": str,
                "programme_name": str,
                "fund_type_id": str,
                "organisation": str,
            },
            "uniques": ["programme_id"],
            "foreign_keys": {"organisation": {"parent_table": "Organisation_Ref", "parent_pk": "organisation_name"}},
            "enums": {"fund_type_id": enums.FundTypeIdEnum},
            "non-nullable": ["programme_id", "programme_name", "fund_type_id", "organisation"],
        },
        "Programme Progress": {
            "columns": {
                "programme_id": str,
                "question": str,
                "answer": str,
            },
            "foreign_keys": {
                "programme_id": {"parent_table": "Programme_Ref", "parent_pk": "programme_id"},
            },
            "non-nullable": ["programme_id", "question", "answer"],
        },
        "Place Details": {
            "columns": {
                "programme_id": str,
                "question": str,
                "answer": str,
                "indicator": str,
            },
            "foreign_keys": {
                "programme_id": {"parent_table": "Programme_Ref", "parent_pk": "programme_id"},
            },
            "composite_key": (
                "programme_id",
                "question",
                "indicator",
            ),
            "non-nullable": ["programme_id", "question", "indicator", "answer"],
        },
        "Funding Questions": {
            "table_nullable": True,
            "columns": {
                "programme_id": str,
                "question": str,
                "indicator": str,
                "response": str,
                "guidance_notes": str,
            },
            "foreign_keys": {
                "programme_id": {"parent_table": "Programme_Ref", "parent_pk": "programme_id"},
            },
            "composite_key": (
                "programme_id",
                "question",
                "indicator",
            ),
            "non-nullable": ["programme_id", "question"],
        },
        "Project Details": {
            "columns": {
                "project_id": str,
                "programme_id": str,
                "project_name": str,
                "primary_intervention_theme": str,
                "location_multiplicity": str,
                "locations": str,
                "postcodes": list,
                "gis_provided": str,
                "lat_long": str,
            },
            "uniques": ["project_id"],
            "foreign_keys": {
                "programme_id": {"parent_table": "Programme_Ref", "parent_pk": "programme_id"},
            },
            "enums": {
                "location_multiplicity": enums.MultiplicityEnum,
                "primary_intervention_theme": enums.PrimaryInterventionThemeEnum,
            },
            "non-nullable": [
                "project_id",
                "programme_id",
                "project_name",
                "primary_intervention_theme",
                "location_multiplicity",
                # Locations, lat_long and gis_provided all validated after schema validation due to specific rules
            ],
        },
        "Project Progress": {
            "columns": {
                "project_id": str,
                "start_date": datetime,
                "end_date": datetime,
                "delivery_stage": str,
                "delivery_status": str,
                "leading_factor_of_delay": str,
                "adjustment_request_status": str,
                "delivery_rag": str,
                "spend_rag": str,
                "risk_rag": str,
                "commentary": str,
                "important_milestone": str,
                "date_of_important_milestone": datetime,
            },
            "uniques": ["project_id"],
            "foreign_keys": {
                "project_id": {"parent_table": "Project Details", "parent_pk": "project_id"},
            },
            "enums": {
                "adjustment_request_status": enums.ProjectAdjustmentRequestStatus,
                "delivery_stage": enums.ProjectDeliveryStageEnum,
                "delivery_status": enums.StatusEnum,
                "leading_factor_of_delay": enums.DelayEnum,
                "delivery_rag": enums.RagEnum,
                "spend_rag": enums.RagEnum,
                "risk_rag": enums.RagEnum,
            },
            "non-nullable": [
                "project_id",
                "start_date",
                "end_date",
                # delivery_stage is sometimes nullable so has its own specific validation
                "delivery_status",
                # leading_factor_of_delay is sometimes nullable so has its own specific validation
                "adjustment_request_status",
                "delivery_rag",
                "spend_rag",
                "risk_rag",
                "commentary",
                # important_milestone is sometimes nullable so has its own specific validation
                # This also applies to date_of_important_milestone
            ],
            "project_date_validation": ["start_date", "end_date"],
        },
        "Funding": {
            "columns": {
                "project_id": str,
                "funding_source": str,
                "spend_type": str,
                "secured": str,
                "start_date": datetime,
                "end_date": datetime,
                "spend_for_reporting_period": float,
                "state": str,
            },
            "foreign_keys": {
                "project_id": {"parent_table": "Project Details", "parent_pk": "project_id"},
            },
            "composite_key": (
                "project_id",
                "funding_source",
                "spend_type",
                "secured",
                "start_date",
                "end_date",
            ),
            "enums": {
                "secured": enums.YesNoEnum,
                "state": enums.StateEnum,
            },
            "non-nullable": ["project_id", "funding_source", "spend_type", "spend_for_reporting_period"],
        },
        "Funding Comments": {
            "columns": {
                "project_id": str,
                "comment": str,
            },
            "foreign_keys": {
                "project_id": {"parent_table": "Project Details", "parent_pk": "project_id"},
            },
            "non-nullable": ["project_id"],
        },
        "Private Investments": {
            "columns": {
                "project_id": str,
                "total_project_value": float,
                "townsfund_funding": float,
                "private_sector_funding_required": float,
                "private_sector_funding_secured": float,
                "additional_comments": str,
            },
            "foreign_keys": {
                "project_id": {"parent_table": "Project Details", "parent_pk": "project_id"},
            },
            "uniques": ["project_id"],
            "non-nullable": ["project_id", "total_project_value", "townsfund_funding"],
        },
        "Outputs_Ref": {
            "columns": {"output_name": str, "output_category": str},
            "uniques": ["output_name"],
            "non-nullable": ["output_name", "output_category"],
        },
        "Output_Data": {
            "columns": {
                "project_id": str,
                "start_date": datetime,
                "end_date": datetime,
                "output": str,
                "unit_of_measurement": str,
                "state": str,
                "amount": float,
                "additional_information": str,
            },
            "foreign_keys": {
                "project_id": {"parent_table": "Project Details", "parent_pk": "project_id"},
                "output": {"parent_table": "Outputs_Ref", "parent_pk": "output_name"},
            },
            "composite_key": (
                "project_id",
                "output",
                "start_date",
                "end_date",
                "unit_of_measurement",
                "state",
            ),
            "enums": {"state": enums.StateEnum},
            "non-nullable": ["project_id", "start_date", "output", "unit_of_measurement", "amount"],
        },
        "Outcome_Ref": {
            "table_nullable": True,
            "columns": {"outcome_name": str, "outcome_category": str},
            "uniques": ["outcome_name"],
            "non-nullable": ["outcome_name", "outcome_category"],
        },
        "Outcome_Data": {
            "table_nullable": True,
            "columns": {
                "project_id": str,
                "programme_id": str,
                "start_date": datetime,
                "end_date": datetime,
                "outcome": str,
                "unit_of_measurement": str,
                "geography_indicator": str,
                "amount": float,
                "state": str,
                "higher_frequency": str,
            },
            "foreign_keys": {
                "project_id": {"parent_table": "Project Details", "parent_pk": "project_id", "nullable": True},
                "programme_id": {"parent_table": "Programme_Ref", "parent_pk": "programme_id", "nullable": True},
                "outcome": {"parent_table": "Outcome_Ref", "parent_pk": "outcome_name"},
            },
            "composite_key": (
                "project_id",
                "outcome",
                "start_date",
                "end_date",
                "geography_indicator",
            ),
            "enums": {
                "geography_indicator": enums.GeographyIndicatorEnum,
                "state": enums.StateEnum,
            },
            "non-nullable": [
                "start_date",
                "end_date",
                "outcome",
                "unit_of_measurement",
                "state",
                "amount",
                "geography_indicator",
            ],
        },
        "RiskRegister": {
            "table_nullable": True,
            "columns": {
                "programme_id": str,
                "project_id": str,
                "risk_name": str,
                "risk_category": str,
                "short_desc": str,
                "full_desc": str,
                "consequences": str,
                "pre_mitigated_impact": str,
                "pre_mitigated_likelihood": str,
                "mitigations": str,
                "post_mitigated_impact": str,
                "post_mitigated_likelihood": str,
                "proximity": str,
                "risk_owner_role": str,
            },
            "foreign_keys": {
                "project_id": {"parent_table": "Project Details", "parent_pk": "project_id", "nullable": True},
                "programme_id": {"parent_table": "Programme_Ref", "parent_pk": "programme_id", "nullable": True},
            },
            "composite_key": (
                "programme_id",
                "project_id",
                "risk_name",
            ),
            "enums": {
                "risk_category": enums.RiskCategoryEnum,
                "pre_mitigated_impact": enums.ImpactEnum,
                "pre_mitigated_likelihood": enums.LikelihoodEnum,
                "post_mitigated_impact": enums.ImpactEnum,
                "post_mitigated_likelihood": enums.LikelihoodEnum,
                "proximity": enums.ProximityEnum,
            },
            "non-nullable": [
                "risk_name",
                "risk_category",
                "short_desc",
                "full_desc",
                "consequences",
                "pre_mitigated_impact",
                "pre_mitigated_likelihood",
                "mitigations",
                "post_mitigated_impact",
                "post_mitigated_likelihood",
                "proximity",
                "risk_owner_role",
            ],
        },
        "Programme Management": {
            "columns": {
                "programme_id": str,
                "payment_type": str,
                "spend_for_reporting_period": float,
                "start_date": datetime,
                "end_date": datetime,
                "state": str,
            },
            "table_nullable": True,
        },
    }
)

TF_ROUND_3_VAL_SCHEMA = parse_schema(
    {
        "Submission_Ref": {
            "columns": {
                "submission_date": datetime,
            },
        },
        "Organisation_Ref": {
            "columns": {
                "organisation_name": str,
                "geography": str,
            },
            "uniques": ["organisation_name"],
            "non-nullable": ["organisation_name"],
        },
        "Programme_Ref": {
            "columns": {
                "programme_id": str,
                "programme_name": str,
                "fund_type_id": str,
                "organisation": str,
            },
            "uniques": ["programme_id"],
            "foreign_keys": {"organisation": {"parent_table": "Organisation_Ref", "parent_pk": "organisation_name"}},
            "enums": {"fund_type_id": enums.FundTypeIdEnum},
            "non-nullable": ["programme_id", "programme_name", "fund_type_id", "organisation"],
        },
        "Programme Progress": {
            "columns": {
                "programme_id": str,
                "question": str,
                "answer": str,
            },
            "foreign_keys": {
                "programme_id": {"parent_table": "Programme_Ref", "parent_pk": "programme_id"},
            },
            "non-nullable": ["programme_id", "question"],
        },
        "Place Details": {
            "columns": {
                "programme_id": str,
                "question": str,
                "answer": str,
                "indicator": str,
            },
            "foreign_keys": {
                "programme_id": {"parent_table": "Programme_Ref", "parent_pk": "programme_id"},
            },
            "non-nullable": ["programme_id", "question", "indicator"],
        },
        "Funding Questions": {
            "columns": {
                "programme_id": str,
                "question": str,
                "indicator": str,
                "response": str,
                "guidance_notes": str,
            },
            "foreign_keys": {
                "programme_id": {"parent_table": "Programme_Ref", "parent_pk": "programme_id"},
            },
            "non-nullable": ["programme_id", "question"],
            "table_nullable": True,
        },
        "Project Details": {
            "columns": {
                "project_id": str,
                "programme_id": str,
                "project_name": str,
                "primary_intervention_theme": str,
                "location_multiplicity": str,
                "locations": str,
                "postcodes": list,
                "gis_provided": str,
                "lat_long": str,
            },
            "uniques": ["project_id"],
            "foreign_keys": {
                "programme_id": {"parent_table": "Programme_Ref", "parent_pk": "programme_id"},
            },
            "enums": {"location_multiplicity": enums.MultiplicityEnum, "gis_provided": enums.YesNoEnum},
            "non-nullable": [
                "project_id",
                "programme_id",
                "project_name",
                "primary_intervention_theme",
                "location_multiplicity",
                "locations",
            ],
        },
        "Project Progress": {
            "columns": {
                "project_id": str,
                "start_date": datetime,
                "end_date": datetime,
                "adjustment_request_status": str,  # free text
                "delivery_status": str,
                "delivery_rag": str,
                "spend_rag": str,
                "risk_rag": str,
                "commentary": str,
                "important_milestone": str,
                "date_of_important_milestone": datetime,
            },
            "uniques": ["project_id"],
            "foreign_keys": {
                "project_id": {"parent_table": "Project Details", "parent_pk": "project_id"},
            },
            "enums": {
                "delivery_status": enums.StatusEnum,
                "delivery_rag": enums.RagEnum,
                "spend_rag": enums.RagEnum,
                "risk_rag": enums.RagEnum,
            },
            "non-nullable": [
                "project_id",
            ],
            "project_date_validation": ["start_date", "end_date"],
        },
        "Funding": {
            "columns": {
                "project_id": str,
                "funding_source": str,
                "spend_type": str,
                "secured": str,
                "start_date": datetime,
                "end_date": datetime,
                "spend_for_reporting_period": float,
                "state": str,
            },
            "foreign_keys": {
                "project_id": {"parent_table": "Project Details", "parent_pk": "project_id"},
            },
            "enums": {
                "secured": enums.YesNoEnum,
                "state": enums.StateEnum,
            },
            "non-nullable": [
                "project_id",
                "funding_source",
                "spend_type",
            ],
        },
        "Funding Comments": {
            "columns": {
                "project_id": str,
                "comment": str,
            },
            "foreign_keys": {
                "project_id": {"parent_table": "Project Details", "parent_pk": "project_id"},
            },
            "non-nullable": ["project_id"],
        },
        "Private Investments": {
            "columns": {
                "project_id": str,
                "total_project_value": float,
                "townsfund_funding": float,
                "private_sector_funding_required": float,
                "private_sector_funding_secured": float,
                "additional_comments": str,
            },
            "foreign_keys": {
                "project_id": {"parent_table": "Project Details", "parent_pk": "project_id"},
            },
            "uniques": ["project_id"],
            "non-nullable": ["project_id", "total_project_value", "townsfund_funding"],
        },
        "Outputs_Ref": {
            "columns": {"output_name": str, "output_category": str},
            "uniques": ["output_name"],
            "non-nullable": ["output_name", "output_category"],
        },
        "Output_Data": {
            "columns": {
                "project_id": str,
                "start_date": datetime,
                "end_date": datetime,
                "output": str,
                "unit_of_measurement": str,
                "state": str,
                "amount": float,
                "additional_information": str,
            },
            "foreign_keys": {
                "project_id": {"parent_table": "Project Details", "parent_pk": "project_id"},
                "output": {"parent_table": "Outputs_Ref", "parent_pk": "output_name"},
            },
            "enums": {"state": enums.StateEnum},
            "non-nullable": ["project_id", "start_date", "output", "unit_of_measurement"],
        },
        "Outcome_Ref": {
            "table_nullable": True,
            "columns": {"outcome_name": str, "outcome_category": str},
            "uniques": ["outcome_name"],
            "non-nullable": ["outcome_name", "outcome_category"],
        },
        "Outcome_Data": {
            "table_nullable": True,
            "columns": {
                "project_id": str,
                "programme_id": str,
                "start_date": datetime,
                "end_date": datetime,
                "outcome": str,
                "unit_of_measurement": str,
                "geography_indicator": str,
                "amount": float,
                "state": str,
                "higher_frequency": str,
            },
            "foreign_keys": {
                "project_id": {"parent_table": "Project Details", "parent_pk": "project_id", "nullable": True},
                "programme_id": {"parent_table": "Programme_Ref", "parent_pk": "programme_id", "nullable": True},
                "outcome": {"parent_table": "Outcome_Ref", "parent_pk": "outcome_name"},
            },
            "enums": {
                "geography_indicator": enums.GeographyIndicatorEnum,
                "state": enums.StateEnum,
            },
            "non-nullable": [
                "start_date",
                "end_date",
                "outcome",
                "unit_of_measurement",
                "state",
            ],
        },
        "RiskRegister": {
            "table_nullable": True,
            "columns": {
                "programme_id": str,
                "project_id": str,
                "risk_name": str,
                "risk_category": str,
                "short_desc": str,
                "full_desc": str,
                "consequences": str,
                "pre_mitigated_impact": str,
                "pre_mitigated_likelihood": str,
                "mitigations": str,
                "post_mitigated_impact": str,
                "post_mitigated_likelihood": str,
                "proximity": str,
                "risk_owner_role": str,
            },
            "foreign_keys": {
                "project_id": {"parent_table": "Project Details", "parent_pk": "project_id", "nullable": True},
                "programme_id": {"parent_table": "Programme_Ref", "parent_pk": "programme_id", "nullable": True},
            },
            "enums": {
                "pre_mitigated_impact": enums.ImpactEnum,
                "pre_mitigated_likelihood": enums.LikelihoodEnum,
                "post_mitigated_impact": enums.ImpactEnum,
                "post_mitigated_likelihood": enums.LikelihoodEnum,
                "proximity": enums.ProximityEnum,
            },
            "non-nullable": [
                "risk_name",
            ],
        },
        "Programme Management": {
            "columns": {
                "programme_id": str,
                "payment_type": str,
                "spend_for_reporting_period": float,
                "start_date": datetime,
                "end_date": datetime,
                "state": str,
            },
            "table_nullable": True,
        },
    }
)
