import core.const as enums

SCHEMA = {
    "Submission_Ref": {
        "columns": {
            "Submission Date": "datetime",
            "Reporting Period Start": "datetime",
            "Reporting Period End": "datetime",
            "Reporting Round": "int",
        },
    },
    "Organisation_Ref": {
        "columns": {
            "Organisation": "str",
            "Geography": "str",
        },
        "uniques": ["Organisation"],
    },
    "Programme_Ref": {
        "columns": {
            "Programme ID": "str",
            "Programme Name": "str",
            "FundType_ID": "str",
            "Organisation": "str",
        },
        "uniques": ["Programme ID"],  # TODO: Assuming an Organisation can have multiple programmes
        "foreign_keys": {"Organisation": {"parent_table": "Organisation_Ref", "parent_pk": "Organisation"}},
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
        "enums": {"Single or Multiple Locations": enums.MultiplicityEnum},
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
        # TODO: Assume that we will only read as many project progress rows as there are projects so this will be unique
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
            "Actual / Forecast": "str",
        },
        "foreign_keys": {
            "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
        },
        "enums": {
            "Secured": enums.YesNoEnum,
            "Actual / Forecast": enums.StateEnum,
        },
    },
    "Funding Comments": {
        "columns": {
            "Project ID": "str",
            "Comment": "str",
        },
        "foreign_keys": {
            "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
        },
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
    },
    "Outputs_Ref": {
        "columns": {"Output Name": "str", "Output Category": "str"},
        "uniques": ["Output Name"],
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
    },
    "Outcome_Ref": {
        "columns": {"Outcome_Name": "str", "Outcome_Category": "str"},
        "uniques": ["Outcome_Name"],
    },
    "Outcome_Data": {
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
    },
    "RiskRegister": {
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
    },
}
