import core.const as enums

SCHEMA = {
    "Programme Progress": {
        "columns": {
            "Submission ID": "str",
            "Programme ID": "str",
            "Question": "str",
            "Answer": "str",
        },
        "uniques": ["Submission ID"],
        "foreign_keys": {"Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"}},
    },
    "Programme_Ref": {
        "columns": {
            "Programme ID": "str",
            "Programme Name": "str",
            "FundType_ID": "str",
            "Organisation ID": "str",
        },
        "uniques": ["Programme ID"],  # TODO: Assuming an Organisation can have multiple programmes
        "foreign_keys": {"Organisation ID": {"parent_table": "Organisation_Ref", "parent_pk": "Organisation ID"}},
    },
    "Organisation_Ref": {
        "columns": {
            "Organisation ID": "str",
            "Organisation": "str",
            "Geography": "str",
        },
        "uniques": ["Organisation ID", "Organisation"],  # TODO: Assuming we dont want multiple Orgs with the same name
    },
    "Project Details": {
        "columns": {
            "Submission ID": "str",
            "Project ID": "str",
            "Primary Intervention Theme": "str",
            "Single or Multiple Locations": "str",
            "Locations": "str",
        },
        "uniques": ["Project ID"],
        "enums": {"Single or Multiple Locations": enums.MultiplicityEnum},
    },
    "Place Details": {
        "columns": {
            "Submission ID": "str",
            "Question": "str",
            "Answer": "str",
            "Programme ID": "str",
            "Indicator": "str",
        },
        "foreign_keys": {"Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"}},
    },
    "Project Progress": {
        "columns": {
            "Project ID": "str",
            "Submission ID": "str",
            "Start Date": "datetime",
            "Completion Date": "datetime",
            "Project Adjustment Request Status": "str",  # free text
            "Project Delivery Status": "str",
            "Delivery (RAG)": "str",
            "Spend (RAG)": "str",
            "Risk (RAG)": "str",
            "Commentary on Status and RAG Ratings": "str",
            "Most Important Upcoming Comms Milestone": "str",
            "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": "str",  # free text
        },
        # TODO: Assume that we will only read as many project progress rows as there are projects so this will be unique
        "uniques": ["Project ID"],
        "foreign_keys": {"Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"}},
        "enums": {
            "Project Delivery Status": enums.StatusEnum,
            "Delivery (RAG)": enums.RagEnum,
            "Spend (RAG)": enums.RagEnum,
            "Risk (RAG)": enums.RagEnum,
        },
    },
    "Funding": {
        "columns": {
            "Submission ID": "str",
            "Project ID": "str",
            "Funding Source Name": "str",
            "Funding Source Type": "str",  # TODO: could maybe be an enum but ok for now
            "Secured": "str",  # TODO: Data shows yes/no and empty cells - is this nullable?
            "Spend Before Reporting Commenced": "float",
            "Reporting Period": "str",
            "Spend for Reporting Period": "float",
            "Actual / Forecast": "str",
            "Spend Beyond Fund Lifetime": "float",
        },
        "foreign_keys": {"Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"}},
        "enums": {
            "Secured": enums.YesNoEnum,
            "Actual / Forecast": enums.StateEnum,
        },
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
        "foreign_keys": {"Programme ID": {"parent_table": "Programme_Ref", "parent_pk": "Programme ID"}},
    },
    "Funding Comments": {
        "columns": {
            "Submission ID": "str",
            "Project ID": "str",
            "Comment": "str",
        },
        "foreign_keys": {"Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"}},
    },
    "Private Investments": {
        "columns": {
            "Submission ID": "str",
            "Project ID": "str",
            "Total Project Value": "float",
            "Townsfund Funding": "float",
            "Private Sector Funding Required": "float",
            "Private Sector Funding Secured": "float",
        },
        "foreign_keys": {"Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"}},
        "uniques": ["Project ID"],
    },
    "Outputs_Ref": {
        "columns": {"Output Name": "str", "Output Category": "str"},
        "uniques": ["Output Name"],
    },
    "Output_Data": {
        "columns": {
            "Submission ID": "str",
            "Project ID": "str",
            "Start_Date": "datetime",
            "End_Date": "datetime",
            "Output": "str",
            "Unit of Measurement": "str",
            "Actual/Forecast": "str",
            "Amount": "float",
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
            "Submission ID": "str",
            "Project ID": "str",
            "Start_Date": "datetime",
            "End_Date": "datetime",
            "Outcome": "str",
            "UnitofMeasurement": "str",
            "GeographyIndicator": "str",
            "Amount": "float",
            "Actual/Forecast": "str",
        },
        "foreign_keys": {
            "Project ID": {"parent_table": "Project Details", "parent_pk": "Project ID"},
            "Outcome": {"parent_table": "Outcome_Ref", "parent_pk": "Outcome_Name"},
        },
        "enums": {
            "GeographyIndicator": enums.GeographyIndicatorEnum,
            "Actual/Forecast": enums.StateEnum,
        },
    },
    "RiskRegister": {
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
    },
}
