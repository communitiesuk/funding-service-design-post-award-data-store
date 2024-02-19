from datetime import datetime

import core.const as enums
from core.validation.schema_validation.schema import parse_schema

TF_ROUND_4_VAL_SCHEMA = parse_schema(
    {
        "Submission_Ref": {
            "columns": {
                "Submission Date": datetime,
                "Reporting Period Start": datetime,
                "Reporting Period End": datetime,
                "Reporting Round": int,
            },
            "non-nullable": ["Reporting Period Start", "Reporting Period End", "Reporting Round"],
        },
        "Organisation_Ref": {
            "columns": {
                "Organisation": str,
                "Geography": str,
            },
            "uniques": ["Organisation"],
            "non-nullable": ["Organisation"],
        },
        "Programme_Ref": {
            "columns": {
                "Programme ID": str,
                "Programme Name": str,
                "FundType_ID": str,
                "Organisation": str,
            },
            "uniques": ["Programme ID"],
            "foreign_keys": {"Organisation": {"parent_table": "Organisation_Ref", "parent_pk": "Organisation"}},
            "enums": {"FundType_ID": enums.FundTypeIdEnum},
            "non-nullable": ["Programme ID", "Programme Name", "FundType_ID", "Organisation"],
        },
        "Programme Progress": {
            "columns": {
                "Programme ID": str,
                "Question": str,
                "Answer": str,
            },
            "foreign_keys": {
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
            },
            "non-nullable": ["Programme ID", "Question", "Answer"],
        },
        "Place Details": {
            "columns": {
                "Programme ID": str,
                "Question": str,
                "Answer": str,
                "Indicator": str,
            },
            "foreign_keys": {
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
            },
            "composite_key": (
                "Programme ID",
                "Question",
                "Indicator",
            ),
            "non-nullable": ["Programme ID", "Question", "Indicator", "Answer"],
        },
        "Funding Questions": {
            "table_nullable": True,
            "columns": {
                "Programme ID": str,
                "Question": str,
                "Indicator": str,
                "Response": str,
                "Guidance Notes": str,
            },
            "foreign_keys": {
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
            },
            "composite_key": (
                "Programme ID",
                "Question",
                "Indicator",
            ),
            "non-nullable": ["Programme ID", "Question"],
        },
        "Project Details": {
            "columns": {
                "Project ID": str,
                "Programme ID": str,
                "Project Name": str,
                "Primary Intervention Theme": str,
                "Single or Multiple Locations": str,
                "Locations": str,
                "Postcodes": list,
                "GIS Provided": str,
                "Lat/Long": str,
            },
            "uniques": ["Project ID"],
            "foreign_keys": {
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
            },
            "enums": {
                "Single or Multiple Locations": enums.MultiplicityEnum,
                "Primary Intervention Theme": enums.PrimaryInterventionThemeEnum,
            },
            "non-nullable": [
                "Project ID",
                "Programme ID",
                "Project Name",
                "Primary Intervention Theme",
                "Single or Multiple Locations",
                # Locations, Lat/Long and GIS Provided all validated after schema validation due to specific rules
            ],
        },
        "Project Progress": {
            "columns": {
                "Project ID": str,
                "Start Date": datetime,
                "Completion Date": datetime,
                "Current Project Delivery Stage": str,
                "Project Delivery Status": str,
                "Leading Factor of Delay": str,
                "Project Adjustment Request Status": str,
                "Delivery (RAG)": str,
                "Spend (RAG)": str,
                "Risk (RAG)": str,
                "Commentary on Status and RAG Ratings": str,
                "Most Important Upcoming Comms Milestone": str,
                "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": datetime,
            },
            "uniques": ["Project ID"],
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
            },
            "enums": {
                "Project Adjustment Request Status": enums.ProjectAdjustmentRequestStatus,
                "Current Project Delivery Stage": enums.ProjectDeliveryStageEnum,
                "Project Delivery Status": enums.StatusEnum,
                "Leading Factor of Delay": enums.DelayEnum,
                "Delivery (RAG)": enums.RagEnum,
                "Spend (RAG)": enums.RagEnum,
                "Risk (RAG)": enums.RagEnum,
            },
            "non-nullable": [
                "Project ID",
                "Start Date",
                "Completion Date",
                # Current Project Delivery Status is sometimes nullable so has its own specific validation
                "Project Delivery Status",
                # Leading Factor of Delay is sometimes nullable so has its own specific validation
                "Project Adjustment Request Status",
                "Delivery (RAG)",
                "Spend (RAG)",
                "Risk (RAG)",
                "Commentary on Status and RAG Ratings",
                # Most Important Upcoming Comms Milestone is sometimes nullable so has its own specific validation
                # This also applies to Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)
            ],
        },
        "Funding": {
            "columns": {
                "Project ID": str,
                "Funding Source Name": str,
                "Funding Source Type": str,
                "Secured": str,
                "Start_Date": datetime,
                "End_Date": datetime,
                "Spend for Reporting Period": float,
                "Actual/Forecast": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
            },
            "composite_key": (
                "Project ID",
                "Funding Source Name",
                "Funding Source Type",
                "Secured",
                "Start_Date",
                "End_Date",
            ),
            "enums": {
                "Secured": enums.YesNoEnum,
                "Actual/Forecast": enums.StateEnum,
            },
            "non-nullable": ["Project ID", "Funding Source Name", "Funding Source Type", "Spend for Reporting Period"],
        },
        "Funding Comments": {
            "columns": {
                "Project ID": str,
                "Comment": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
            },
            "non-nullable": ["Project ID"],
        },
        "Private Investments": {
            "columns": {
                "Project ID": str,
                "Total Project Value": float,
                "Townsfund Funding": float,
                "Private Sector Funding Required": float,
                "Private Sector Funding Secured": float,
                "Additional Comments": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
            },
            "uniques": ["Project ID"],
            "non-nullable": ["Project ID", "Total Project Value", "Townsfund Funding"],
        },
        "Outputs_Ref": {
            "columns": {"Output Name": str, "Output Category": str},
            "uniques": ["Output Name"],
            "non-nullable": ["Output Name", "Output Category"],
        },
        "Output_Data": {
            "columns": {
                "Project ID": str,
                "Start_Date": datetime,
                "End_Date": datetime,
                "Output": str,
                "Unit of Measurement": str,
                "Actual/Forecast": str,
                "Amount": float,
                "Additional Information": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
                "Output": {"parent_table": "Outputs_Ref", "parent_pk": "Output Name"},
            },
            "composite_key": (
                "Project ID",
                "Output",
                "Start_Date",
                "End_Date",
                "Unit of Measurement",
                "Actual/Forecast",
            ),
            "enums": {"Actual/Forecast": enums.StateEnum},
            "non-nullable": ["Project ID", "Start_Date", "Output", "Unit of Measurement", "Amount"],
        },
        "Outcome_Ref": {
            "table_nullable": True,
            "columns": {"Outcome_Name": str, "Outcome_Category": str},
            "uniques": ["Outcome_Name"],
            "non-nullable": ["Outcome_Name", "Outcome_Category"],
        },
        "Outcome_Data": {
            "table_nullable": True,
            "columns": {
                "Project ID": str,
                "Programme ID": str,
                "Start_Date": datetime,
                "End_Date": datetime,
                "Outcome": str,
                "UnitofMeasurement": str,
                "GeographyIndicator": str,
                "Amount": float,
                "Actual/Forecast": str,
                "Higher Frequency": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID", "nullable": True},
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID", "nullable": True},
                "Outcome": {"parent_table": "Outcome_Ref", "parent_pk": "Outcome_Name"},
            },
            "composite_key": (
                "Project ID",
                "Outcome",
                "Start_Date",
                "End_Date",
                "GeographyIndicator",
            ),
            "enums": {
                "GeographyIndicator": enums.GeographyIndicatorEnum,
                "Actual/Forecast": enums.StateEnum,
            },
            "non-nullable": [
                "Start_Date",
                "End_Date",
                "Outcome",
                "UnitofMeasurement",
                "Actual/Forecast",
                "Amount",
                "GeographyIndicator",
            ],
        },
        "RiskRegister": {
            "table_nullable": True,
            "columns": {
                "Programme ID": str,
                "Project ID": str,
                "RiskName": str,
                "RiskCategory": str,
                "Short Description": str,
                "Full Description": str,
                "Consequences": str,
                "Pre-mitigatedImpact": str,
                "Pre-mitigatedLikelihood": str,
                "Mitigatons": str,
                "PostMitigatedImpact": str,
                "PostMitigatedLikelihood": str,
                "Proximity": str,
                "RiskOwnerRole": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID", "nullable": True},
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID", "nullable": True},
            },
            "composite_key": (
                "Programme ID",
                "Project ID",
                "RiskName",
            ),
            "enums": {
                "RiskCategory": enums.RiskCategoryEnum,
                "Pre-mitigatedImpact": enums.ImpactEnum,
                "Pre-mitigatedLikelihood": enums.LikelihoodEnum,
                "PostMitigatedImpact": enums.ImpactEnum,
                "PostMitigatedLikelihood": enums.LikelihoodEnum,
                "Proximity": enums.ProximityEnum,
            },
            "non-nullable": [
                "RiskName",
                "RiskCategory",
                "Short Description",
                "Full Description",
                "Consequences",
                "Pre-mitigatedImpact",
                "Pre-mitigatedLikelihood",
                "Mitigatons",
                "PostMitigatedImpact",
                "PostMitigatedLikelihood",
                "Proximity",
                "RiskOwnerRole",
            ],
        },
        "Programme Management": {
            "columns": {
                "Programme ID": str,
                "Payment Type": str,
                "Reporting Period": str,
                "Spend for Reporting Period": str,
            },
            "table_nullable": True,
        },
    }
)

TF_ROUND_3_VAL_SCHEMA = parse_schema(
    {
        "Submission_Ref": {
            "columns": {
                "Submission Date": datetime,
                "Reporting Period Start": datetime,
                "Reporting Period End": datetime,
                "Reporting Round": int,
            },
            "non-nullable": ["Reporting Period Start", "Reporting Period End", "Reporting Round"],
        },
        "Organisation_Ref": {
            "columns": {
                "Organisation": str,
                "Geography": str,
            },
            "uniques": ["Organisation"],
            "non-nullable": ["Organisation"],
        },
        "Programme_Ref": {
            "columns": {
                "Programme ID": str,
                "Programme Name": str,
                "FundType_ID": str,
                "Organisation": str,
            },
            "uniques": ["Programme ID"],
            "foreign_keys": {"Organisation": {"parent_table": "Organisation_Ref", "parent_pk": "Organisation"}},
            "enums": {"FundType_ID": enums.FundTypeIdEnum},
            "non-nullable": ["Programme ID", "Programme Name", "FundType_ID", "Organisation"],
        },
        "Programme Progress": {
            "columns": {
                "Programme ID": str,
                "Question": str,
                "Answer": str,
            },
            "foreign_keys": {
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
            },
            "non-nullable": ["Programme ID", "Question"],
        },
        "Place Details": {
            "columns": {
                "Programme ID": str,
                "Question": str,
                "Answer": str,
                "Indicator": str,
            },
            "foreign_keys": {
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
            },
            "non-nullable": ["Programme ID", "Question", "Indicator"],
        },
        "Funding Questions": {
            "columns": {
                "Programme ID": str,
                "Question": str,
                "Indicator": str,
                "Response": str,
                "Guidance Notes": str,
            },
            "foreign_keys": {
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
            },
            "non-nullable": ["Programme ID", "Question"],
            "table_nullable": True,
        },
        "Project Details": {
            "columns": {
                "Project ID": str,
                "Programme ID": str,
                "Project Name": str,
                "Primary Intervention Theme": str,
                "Single or Multiple Locations": str,
                "Locations": str,
                "Postcodes": list,
                "GIS Provided": str,
                "Lat/Long": str,
            },
            "uniques": ["Project ID"],
            "foreign_keys": {
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
            },
            "enums": {"Single or Multiple Locations": enums.MultiplicityEnum, "GIS Provided": enums.YesNoEnum},
            "non-nullable": [
                "Project ID",
                "Programme ID",
                "Project Name",
                "Primary Intervention Theme",
                "Single or Multiple Locations",
                "Locations",
            ],
        },
        "Project Progress": {
            "columns": {
                "Project ID": str,
                "Start Date": datetime,
                "Completion Date": datetime,
                "Project Adjustment Request Status": str,  # free text
                "Project Delivery Status": str,
                "Delivery (RAG)": str,
                "Spend (RAG)": str,
                "Risk (RAG)": str,
                "Commentary on Status and RAG Ratings": str,
                "Most Important Upcoming Comms Milestone": str,
                "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": datetime,
            },
            "uniques": ["Project ID"],
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
            },
            "enums": {
                "Project Delivery Status": enums.StatusEnum,
                "Delivery (RAG)": enums.RagEnum,
                "Spend (RAG)": enums.RagEnum,
                "Risk (RAG)": enums.RagEnum,
            },
            "non-nullable": [
                "Project ID",
            ],
        },
        "Funding": {
            "columns": {
                "Project ID": str,
                "Funding Source Name": str,
                "Funding Source Type": str,
                "Secured": str,
                "Start_Date": datetime,
                "End_Date": datetime,
                "Spend for Reporting Period": float,
                "Actual/Forecast": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
            },
            "enums": {
                "Secured": enums.YesNoEnum,
                "Actual/Forecast": enums.StateEnum,
            },
            "non-nullable": [
                "Project ID",
                "Funding Source Name",
                "Funding Source Type",
            ],
        },
        "Funding Comments": {
            "columns": {
                "Project ID": str,
                "Comment": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
            },
            "non-nullable": ["Project ID"],
        },
        "Private Investments": {
            "columns": {
                "Project ID": str,
                "Total Project Value": float,
                "Townsfund Funding": float,
                "Private Sector Funding Required": float,
                "Private Sector Funding Secured": float,
                "Additional Comments": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
            },
            "uniques": ["Project ID"],
            "non-nullable": ["Project ID", "Total Project Value", "Townsfund Funding"],
        },
        "Outputs_Ref": {
            "columns": {"Output Name": str, "Output Category": str},
            "uniques": ["Output Name"],
            "non-nullable": ["Output Name", "Output Category"],
        },
        "Output_Data": {
            "columns": {
                "Project ID": str,
                "Start_Date": datetime,
                "End_Date": datetime,
                "Output": str,
                "Unit of Measurement": str,
                "Actual/Forecast": str,
                "Amount": float,
                "Additional Information": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
                "Output": {"parent_table": "Outputs_Ref", "parent_pk": "Output Name"},
            },
            "enums": {"Actual/Forecast": enums.StateEnum},
            "non-nullable": ["Project ID", "Start_Date", "Output", "Unit of Measurement"],
        },
        "Outcome_Ref": {
            "table_nullable": True,
            "columns": {"Outcome_Name": str, "Outcome_Category": str},
            "uniques": ["Outcome_Name"],
            "non-nullable": ["Outcome_Name", "Outcome_Category"],
        },
        "Outcome_Data": {
            "table_nullable": True,
            "columns": {
                "Project ID": str,
                "Programme ID": str,
                "Start_Date": datetime,
                "End_Date": datetime,
                "Outcome": str,
                "UnitofMeasurement": str,
                "GeographyIndicator": str,
                "Amount": float,
                "Actual/Forecast": str,
                "Higher Frequency": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID", "nullable": True},
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID", "nullable": True},
                "Outcome": {"parent_table": "Outcome_Ref", "parent_pk": "Outcome_Name"},
            },
            "enums": {
                "GeographyIndicator": enums.GeographyIndicatorEnum,
                "Actual/Forecast": enums.StateEnum,
            },
            "non-nullable": [
                "Start_Date",
                "End_Date",
                "Outcome",
                "UnitofMeasurement",
                "Actual/Forecast",
            ],
        },
        "RiskRegister": {
            "table_nullable": True,
            "columns": {
                "Programme ID": str,
                "Project ID": str,
                "RiskName": str,
                "RiskCategory": str,
                "Short Description": str,
                "Full Description": str,
                "Consequences": str,
                "Pre-mitigatedImpact": str,
                "Pre-mitigatedLikelihood": str,
                "Mitigatons": str,
                "PostMitigatedImpact": str,
                "PostMitigatedLikelihood": str,
                "Proximity": str,
                "RiskOwnerRole": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID", "nullable": True},
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID", "nullable": True},
            },
            "enums": {
                "Pre-mitigatedImpact": enums.ImpactEnum,
                "Pre-mitigatedLikelihood": enums.LikelihoodEnum,
                "PostMitigatedImpact": enums.ImpactEnum,
                "PostMitigatedLikelihood": enums.LikelihoodEnum,
                "Proximity": enums.ProximityEnum,
            },
            "non-nullable": [
                "RiskName",
            ],
        },
        "Programme Management": {
            "columns": {
                "Programme ID": str,
                "Payment Type": str,
                "Reporting Period": str,
                "Spend for Reporting Period": str,
            },
            "table_nullable": True,
        },
    }
)

TF_ROUND_2_VAL_SCHEMA = parse_schema(
    {
        "Submission_Ref": {
            "columns": {
                "Submission ID": str,
                "Submission Date": datetime,
                "Reporting Period Start": datetime,
                "Reporting Period End": datetime,
                "Reporting Round": int,
            },
            "non-nullable": ["Reporting Period Start", "Reporting Period End", "Reporting Round"],
        },
        "Organisation_Ref": {
            "columns": {
                "Organisation": str,
                "Geography": str,
            },
            "uniques": ["Organisation"],
            "non-nullable": ["Organisation"],
        },
        "Programme_Ref": {
            "columns": {
                "Programme ID": str,
                "Programme Name": str,
                "FundType_ID": str,
                "Organisation": str,
            },
            "uniques": ["Programme ID"],
            "foreign_keys": {"Organisation": {"parent_table": "Organisation_Ref", "parent_pk": "Organisation"}},
            "enums": {"FundType_ID": enums.FundTypeIdEnum},
            "non-nullable": ["Programme ID", "Programme Name", "FundType_ID", "Organisation"],
        },
        "Programme Junction": {
            "columns": {
                "Programme ID": str,
                "Submission ID": str,
            },
            "non-nullable": ["Programme ID", "Submission ID"],
        },
        "Programme Progress": {
            "columns": {
                "Submission ID": str,
                "Programme ID": str,
                "Question": str,
                "Answer": str,
            },
            "foreign_keys": {
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
            },
            "non-nullable": ["Programme ID", "Question"],
        },
        "Place Details": {
            "columns": {
                "Submission ID": str,
                "Programme ID": str,
                "Question": str,
                "Answer": str,
                "Indicator": str,
            },
            "foreign_keys": {
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
            },
            "non-nullable": ["Programme ID", "Question", "Indicator"],
        },
        "Funding Questions": {
            "columns": {
                "Submission ID": str,
                "Programme ID": str,
                "Question": str,
                "Indicator": str,
                "Response": str,
                "Guidance Notes": str,
            },
            "foreign_keys": {
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
            },
            "non-nullable": ["Programme ID", "Question"],
        },
        "Project Details": {
            "columns": {
                "Submission ID": str,
                "Project ID": str,
                "Programme ID": str,
                "Project Name": str,
                "Primary Intervention Theme": str,
                "Single or Multiple Locations": str,
                "Locations": str,
                "Postcodes": list,
                "GIS Provided": str,
                "Lat/Long": str,
            },
            "uniques": ["Project ID"],
            "foreign_keys": {
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
            },
            "enums": {"Single or Multiple Locations": enums.MultiplicityEnum, "GIS Provided": enums.YesNoEnum},
            "non-nullable": [
                "Project ID",
                "Programme ID",
                "Project Name",
                "Primary Intervention Theme",
                "Locations",
            ],
        },
        "Project Progress": {
            "columns": {
                "Project ID": str,
                "Start Date": datetime,
                "Completion Date": datetime,
                "Project Adjustment Request Status": str,  # free text
                "Project Delivery Status": str,
                "Delivery (RAG)": str,
                "Spend (RAG)": str,
                "Risk (RAG)": str,
                "Commentary on Status and RAG Ratings": str,
                "Most Important Upcoming Comms Milestone": str,
                "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": datetime,
            },
            "uniques": ["Project ID"],
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
            },
            "enums": {
                "Project Delivery Status": enums.StatusEnum,
                "Delivery (RAG)": enums.RagEnum,
                "Spend (RAG)": enums.RagEnum,
                "Risk (RAG)": enums.RagEnum,
            },
            "non-nullable": [
                "Project ID",
            ],
        },
        "Funding": {
            "columns": {
                "Project ID": str,
                "Funding Source Name": str,
                "Funding Source Type": str,
                "Secured": str,
                "Start_Date": datetime,
                "End_Date": datetime,
                "Spend for Reporting Period": float,
                "Actual/Forecast": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
            },
            "enums": {
                "Secured": enums.YesNoEnum,
                "Actual/Forecast": enums.StateEnum,
            },
            "non-nullable": [
                "Project ID",
                "Funding Source Name",
                "Funding Source Type",
            ],
        },
        "Outputs_Ref": {
            "columns": {"Output Name": str, "Output Category": str},
            "uniques": ["Output Name"],
            "non-nullable": ["Output Name", "Output Category"],
        },
        "Output_Data": {
            "columns": {
                "Project ID": str,
                "Start_Date": datetime,
                "End_Date": datetime,
                "Output": str,
                "Unit of Measurement": str,
                "Actual/Forecast": str,
                "Amount": float,
                "Additional Information": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
                "Output": {"parent_table": "Outputs_Ref", "parent_pk": "Output Name"},
            },
            "enums": {"Actual/Forecast": enums.StateEnum},
            "non-nullable": ["Project ID", "Start_Date", "Output", "Unit of Measurement"],
        },
        "Outcome_Ref": {
            "table_nullable": True,
            "columns": {"Outcome_Name": str, "Outcome_Category": str},
            "uniques": ["Outcome_Name"],
            "non-nullable": ["Outcome_Name", "Outcome_Category"],
        },
        "Outcome_Data": {
            "table_nullable": True,
            "columns": {
                "Submission ID": str,
                "Project ID": str,
                "Programme ID": str,
                "Start_Date": datetime,
                "End_Date": datetime,
                "Outcome": str,
                "UnitofMeasurement": str,
                "GeographyIndicator": str,
                "Amount": float,
                "Actual/Forecast": str,
                "Higher Frequency": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID", "nullable": True},
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID", "nullable": True},
                "Outcome": {"parent_table": "Outcome_Ref", "parent_pk": "Outcome_Name"},
            },
            "enums": {
                "GeographyIndicator": enums.GeographyIndicatorEnum,
                "Actual/Forecast": enums.StateEnum,
            },
            "non-nullable": [
                "Start_Date",
                "End_Date",
                "Outcome",
                "UnitofMeasurement",
            ],
        },
        "RiskRegister": {
            "table_nullable": True,
            "columns": {
                "Submission ID": str,
                "Programme ID": str,
                "Project ID": str,
                "RiskName": str,
                "RiskCategory": str,
                "Short Description": str,
                "Full Description": str,
                "Consequences": str,
                "Pre-mitigatedImpact": str,
                "Pre-mitigatedLikelihood": str,
                "Mitigatons": str,
                "PostMitigatedImpact": str,
                "PostMitigatedLikelihood": str,
                "Proximity": str,
                "RiskOwnerRole": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID", "nullable": True},
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID", "nullable": True},
            },
            "enums": {
                "Pre-mitigatedImpact": enums.ImpactEnum,
                "Pre-mitigatedLikelihood": enums.LikelihoodEnum,
                "PostMitigatedImpact": enums.ImpactEnum,
                "PostMitigatedLikelihood": enums.LikelihoodEnum,
                "Proximity": enums.ProximityEnum,
            },
            "non-nullable": [
                "RiskName",
            ],
        },
    }
)

TF_ROUND_1_VAL_SCHEMA = parse_schema(
    {
        "Submission_Ref": {
            "columns": {
                "Submission ID": str,
                "Submission Date": datetime,
                "Reporting Period Start": datetime,
                "Reporting Period End": datetime,
                "Reporting Round": int,
            },
            "non-nullable": ["Reporting Period Start", "Reporting Period End", "Reporting Round"],
        },
        "Organisation_Ref": {
            "columns": {
                "Organisation": str,
                "Geography": str,
            },
            "uniques": ["Organisation"],
            "non-nullable": ["Organisation"],
        },
        "Programme_Ref": {
            "columns": {
                "Programme ID": str,
                "Programme Name": str,
                "FundType_ID": str,
                "Organisation": str,
            },
            "uniques": ["Programme ID"],
            "foreign_keys": {"Organisation": {"parent_table": "Organisation_Ref", "parent_pk": "Organisation"}},
            "enums": {"FundType_ID": enums.FundTypeIdEnum},
            "non-nullable": ["Programme ID", "Programme Name", "FundType_ID", "Organisation"],
        },
        "Programme Junction": {
            "columns": {
                "Programme ID": str,
                "Submission ID": str,
            },
            "non-nullable": ["Programme ID", "Submission ID"],
        },
        "Programme Progress": {
            "columns": {
                "Submission ID": str,
                "Programme ID": str,
                "Question": str,
                "Answer": str,
            },
            "foreign_keys": {
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
            },
            "non-nullable": ["Programme ID", "Question"],
        },
        "Place Details": {
            "columns": {
                "Submission ID": str,
                "Programme ID": str,
                "Question": str,
                "Answer": str,
                "Indicator": str,
            },
            "foreign_keys": {
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
            },
            "non-nullable": ["Programme ID", "Question", "Indicator"],
        },
        "Funding Questions": {
            "columns": {
                "Submission ID": str,
                "Programme ID": str,
                "Question": str,
                "Indicator": str,
                "Response": str,
                "Guidance Notes": str,
            },
            "foreign_keys": {
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
            },
            "non-nullable": ["Programme ID", "Question"],
        },
        "Project Details": {
            "columns": {
                "Submission ID": str,
                "Project ID": str,
                "Programme ID": str,
                "Project Name": str,
                "Primary Intervention Theme": str,
                "Single or Multiple Locations": str,
                "Locations": str,
                "Postcodes": list,
                "GIS Provided": str,
                "Lat/Long": str,
            },
            "uniques": ["Project ID"],
            "foreign_keys": {
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
            },
            "enums": {"Single or Multiple Locations": enums.MultiplicityEnum, "GIS Provided": enums.YesNoEnum},
            "non-nullable": [
                "Project ID",
                "Programme ID",
                "Project Name",
                "Primary Intervention Theme",
                "Locations",
            ],
        },
        "Project Progress": {
            "columns": {
                "Project ID": str,
                "Start Date": datetime,
                "Completion Date": datetime,
                "Project Adjustment Request Status": str,  # free text
                "Project Delivery Status": str,
                "Delivery (RAG)": str,
                "Spend (RAG)": str,
                "Risk (RAG)": str,
                "Commentary on Status and RAG Ratings": str,
                "Most Important Upcoming Comms Milestone": str,
                "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": datetime,
            },
            "uniques": ["Project ID"],
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
            },
            "enums": {
                "Project Delivery Status": enums.StatusEnum,
                "Delivery (RAG)": enums.RagEnum,
                "Spend (RAG)": enums.RagEnum,
                "Risk (RAG)": enums.RagEnum,
            },
            "non-nullable": [
                "Project ID",
            ],
        },
        "Funding": {
            "columns": {
                "Project ID": str,
                "Funding Source Name": str,
                "Funding Source Type": str,
                "Secured": str,
                "Start_Date": datetime,
                "End_Date": datetime,
                "Spend for Reporting Period": float,
                "Actual/Forecast": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
            },
            "enums": {
                "Secured": enums.YesNoEnum,
                "Actual/Forecast": enums.StateEnum,
            },
            "non-nullable": [
                "Project ID",
                "Funding Source Name",
                "Funding Source Type",
            ],
        },
        "Funding Comments": {
            "columns": {
                "Project ID": str,
                "Comment": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
            },
            "non-nullable": ["Project ID"],
        },
        "Outcome_Ref": {
            "table_nullable": True,
            "columns": {"Outcome_Name": str, "Outcome_Category": str},
            "uniques": ["Outcome_Name"],
            "non-nullable": ["Outcome_Name", "Outcome_Category"],
        },
        "Outcome_Data": {
            "table_nullable": True,
            "columns": {
                "Submission ID": str,
                "Project ID": str,
                "Programme ID": str,
                "Start_Date": datetime,
                "End_Date": datetime,
                "Outcome": str,
                "UnitofMeasurement": str,
                "GeographyIndicator": str,
                "Amount": float,
                "Actual/Forecast": str,
                "Higher Frequency": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID", "nullable": True},
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID", "nullable": True},
                "Outcome": {"parent_table": "Outcome_Ref", "parent_pk": "Outcome_Name"},
            },
            "enums": {
                "GeographyIndicator": enums.GeographyIndicatorEnum,
                "Actual/Forecast": enums.StateEnum,
            },
            "non-nullable": [
                "Start_Date",
                "End_Date",
                "Outcome",
                "UnitofMeasurement",
            ],
        },
        "RiskRegister": {
            "table_nullable": True,
            "columns": {
                "Submission ID": str,
                "Programme ID": str,
                "Project ID": str,
                "RiskName": str,
                "RiskCategory": str,
                "Short Description": str,
                "Full Description": str,
                "Consequences": str,
                "Pre-mitigatedImpact": str,
                "Pre-mitigatedLikelihood": str,
                "Mitigatons": str,
                "PostMitigatedImpact": str,
                "PostMitigatedLikelihood": str,
                "Proximity": str,
                "RiskOwnerRole": str,
            },
            "foreign_keys": {
                "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID", "nullable": True},
                "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID", "nullable": True},
            },
            "enums": {
                "Pre-mitigatedImpact": enums.ImpactEnum,
                "Pre-mitigatedLikelihood": enums.LikelihoodEnum,
                "PostMitigatedImpact": enums.ImpactEnum,
                "PostMitigatedLikelihood": enums.LikelihoodEnum,
                "Proximity": enums.ProximityEnum,
            },
            "non-nullable": [
                "RiskName",
            ],
        },
    }
)
