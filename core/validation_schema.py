import core.const as enums

SCHEMA = {
    "Submission_Ref": {
        "columns": {
            "Submission Date": "datetime",
            "Reporting Period Start": "datetime",
            "Reporting Period End": "datetime",
            "Reporting Round": "int",
        },
        "non-nullable": ["Reporting Period Start", "Reporting Period End", "Reporting Round"],
    },
    "Organisation_Ref": {
        "columns": {
            "Organisation": "str",
            "Geography": "str",
        },
        "uniques": ["Organisation"],
        "non-nullable": ["Organisation"],
    },
    "Programme_Ref": {
        "columns": {
            "Programme ID": "str",
            "Programme Name": "str",
            "FundType_ID": "str",
            "Organisation": "str",
        },
        "uniques": ["Programme ID"],
        "foreign_keys": {"Organisation": {"parent_table": "Organisation_Ref", "parent_pk": "Organisation"}},
        "enums": {"FundType_ID": enums.FundTypeIdEnum},
        "non-nullable": ["Programme ID", "Programme Name", "FundType_ID", "Organisation"],
    },
    "Programme Progress": {
        "columns": {
            "Programme ID": "str",
            "Question": "str",
            "Answer": "str",
        },
        "foreign_keys": {
            "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
        },
        "non-nullable": ["Programme ID", "Question"],
    },
    "Place Details": {
        "columns": {
            "Programme ID": "str",
            "Question": "str",
            "Answer": "str",
            "Indicator": "str",
        },
        "foreign_keys": {
            "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
        },
        "non-nullable": ["Programme ID", "Question", "Indicator"],
    },
    "Funding Questions": {
        "columns": {
            "Programme ID": "str",
            "Question": "str",
            "Indicator": "str",
            "Response": "str",
            "Guidance Notes": "str",
        },
        "foreign_keys": {
            "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
        },
        "non-nullable": ["Programme ID", "Question"],
    },
    "Project Details": {
        "columns": {
            "Project ID": "str",
            "Programme ID": "str",
            "Project Name": "str",
            "Primary Intervention Theme": "str",
            "Single or Multiple Locations": "str",
            "Locations": "str",
            "Postcodes": "str",
            "GIS Provided": "str",
            "Lat/Long": "str",
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
            "Project ID": "str",
            "Start Date": "datetime",
            "Completion Date": "datetime",
            "Project Adjustment Request Status": "str",  # free text
            "Project Delivery Status": "str",
            "Delivery (RAG)": "str",
            "Spend (RAG)": "str",
            "Risk (RAG)": "str",
            "Commentary on Status and RAG Ratings": "str",
            "Most Important Upcoming Comms Milestone": "str",
            "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": "datetime",
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
            "Project ID": "str",
            "Funding Source Name": "str",
            "Funding Source Type": "str",  # TODO: could maybe be an enum but ok for now
            "Secured": "str",
            "Start_Date": "datetime",
            "End_Date": "datetime",
            "Spend for Reporting Period": "float",
            "Actual/Forecast": "str",
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
            "Project ID": "str",
            "Comment": "str",
        },
        "foreign_keys": {
            "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
        },
        "non-nullable": ["Project ID"],
    },
    "Private Investments": {
        "columns": {
            "Project ID": "str",
            "Total Project Value": "float",
            "Townsfund Funding": "float",
            "Private Sector Funding Required": "float",
            "Private Sector Funding Secured": "float",
            "Additional Comments": "str",
        },
        "foreign_keys": {
            "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
        },
        "uniques": ["Project ID"],
        "non-nullable": ["Project ID", "Total Project Value", "Townsfund Funding"],
    },
    "Outputs_Ref": {
        "columns": {"Output Name": "str", "Output Category": "str"},
        "uniques": ["Output Name"],
        "non-nullable": ["Output Name", "Output Category"],
    },
    "Output_Data": {
        "columns": {
            "Project ID": "str",
            "Start_Date": "datetime",
            "End_Date": "datetime",
            "Output": "str",
            "Unit of Measurement": "str",
            "Actual/Forecast": "str",
            "Amount": "float",
            "Additional Information": "str",
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
        "columns": {"Outcome_Name": "str", "Outcome_Category": "str"},
        "uniques": ["Outcome_Name"],
        "non-nullable": ["Outcome_Name", "Outcome_Category"],
    },
    "Outcome_Data": {
        "table_nullable": True,
        "columns": {
            "Project ID": "str",
            "Programme ID": "str",
            "Start_Date": "datetime",
            "End_Date": "datetime",
            "Outcome": "str",
            "UnitofMeasurement": "str",
            "GeographyIndicator": "str",
            "Amount": "float",
            "Actual/Forecast": "str",
            "Higher Frequency": "str",
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
            "Programme ID": "str",
            "Project ID": "str",
            "RiskName": "str",
            "RiskCategory": "str",
            "Short Description": "str",
            "Full Description": "str",
            "Consequences": "str",
            "Pre-mitigatedImpact": "str",
            "Pre-mitigatedLikelihood": "str",
            "Mitigatons": "str",
            "PostMitigatedImpact": "str",
            "PostMitigatedLikelihood": "str",
            "Proximity": "str",
            "RiskOwnerRole": "str",
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


ROUND_ONE_TF_SCHEMA = {
    "Submission_Ref": {
        "columns": {
            "Submission ID": "str",
            "Submission Date": "datetime",
            "Reporting Period Start": "datetime",
            "Reporting Period End": "datetime",
            "Reporting Round": "int",
        },
        "non-nullable": ["Reporting Period Start", "Reporting Period End", "Reporting Round"],
    },
    "Organisation_Ref": {
        "columns": {
            "Organisation": "str",
            "Geography": "str",
        },
        "uniques": ["Organisation"],
        "non-nullable": ["Organisation"],
    },
    "Programme_Ref": {
        "columns": {
            "Programme ID": "str",
            "Programme Name": "str",
            "FundType_ID": "str",
            "Organisation": "str",
        },
        "uniques": ["Programme ID"],
        "foreign_keys": {"Organisation": {"parent_table": "Organisation_Ref", "parent_pk": "Organisation"}},
        "enums": {"FundType_ID": enums.FundTypeIdEnum},
        "non-nullable": ["Programme ID", "Programme Name", "FundType_ID", "Organisation"],
    },
    "Programme Progress": {
        "columns": {
            "Submission ID": "str",
            "Programme ID": "str",
            "Question": "str",
            "Answer": "str",
        },
        "foreign_keys": {
            "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
        },
        "non-nullable": ["Programme ID", "Question"],
    },
    "Place Details": {
        "columns": {
            "Submission ID": "str",
            "Programme ID": "str",
            "Question": "str",
            "Answer": "str",
            "Indicator": "str",
        },
        "foreign_keys": {
            "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
        },
        "non-nullable": ["Programme ID", "Question", "Indicator"],
    },
    "Funding Questions": {
        "columns": {
            "Submission ID": "str",
            "Programme ID": "str",
            "Question": "str",
            "Indicator": "str",
            "Response": "str",
            "Guidance Notes": "str",
        },
        "foreign_keys": {
            "Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"},
        },
        "non-nullable": ["Programme ID", "Question"],
    },
    "Project Details": {
        "columns": {
            "Submission ID": "str",
            "Project ID": "str",
            "Programme ID": "str",
            "Project Name": "str",
            "Primary Intervention Theme": "str",
            "Single or Multiple Locations": "str",
            "Locations": "str",
            "Postcodes": "str",
            "GIS Provided": "str",
            "Lat/Long": "str",
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
            "Submission ID": "str",
            "Project ID": "str",
            "Start Date": "datetime",
            "Completion Date": "datetime",
            "Project Adjustment Request Status": "str",  # free text
            "Project Delivery Status": "str",
            "Delivery (RAG)": "str",
            "Spend (RAG)": "str",
            "Risk (RAG)": "str",
            "Commentary on Status and RAG Ratings": "str",
            "Most Important Upcoming Comms Milestone": "str",
            "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": "datetime",
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
            "Submission ID": "str",
            "Project ID": "str",
            "Funding Source Name": "str",
            "Funding Source Type": "str",  # TODO: could maybe be an enum but ok for now
            "Secured": "str",
            "Start_Date": "datetime",
            "End_Date": "datetime",
            "Spend for Reporting Period": "float",
            "Actual/Forecast": "str",
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
            "Submission ID": "str",
            "Project ID": "str",
            "Comment": "str",
        },
        "foreign_keys": {
            "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
        },
        "non-nullable": ["Project ID"],
    },
    "Outcome_Ref": {
        "table_nullable": True,
        "columns": {"Outcome_Name": "str", "Outcome_Category": "str"},
        "uniques": ["Outcome_Name"],
        "non-nullable": ["Outcome_Name", "Outcome_Category"],
    },
    "Outcome_Data": {
        "table_nullable": True,
        "columns": {
            "Submission ID": "str",
            "Project ID": "str",
            "Programme ID": "str",
            "Start_Date": "datetime",
            "End_Date": "datetime",
            "Outcome": "str",
            "UnitofMeasurement": "str",
            "GeographyIndicator": "str",
            "Amount": "float",
            "Actual/Forecast": "str",
            "Higher Frequency": "str",
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
            "Submission ID": "str",
            "Programme ID": "str",
            "Project ID": "str",
            "RiskName": "str",
            "RiskCategory": "str",
            "Short Description": "str",
            "Full Description": "str",
            "Consequences": "str",
            "Pre-mitigatedImpact": "str",
            "Pre-mitigatedLikelihood": "str",
            "Mitigatons": "str",
            "PostMitigatedImpact": "str",
            "PostMitigatedLikelihood": "str",
            "Proximity": "str",
            "RiskOwnerRole": "str",
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
