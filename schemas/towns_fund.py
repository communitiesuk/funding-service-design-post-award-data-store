import core.const as enums

TF_SCHEMA = {
    "StartDate_Dim": {
        "columns": {
            "Date": "datetime",
            "Month": "int",
            "Year": "str",
            "FY": "str",
            "FH": "int",
            "FQ": "int",
        },
        "uniques": ["Date"],
    },
    "EndDate_Dim": {
        "columns": {
            "Date": "datetime",
            "Month": "int",
            "Year": "str",
            "FY": "str",
            "FH": "int",
            "FQ": "int",
        },
        "uniques": ["Date"],
    },
    "Project_Dim": {
        "columns": {
            "Project_ID": "str",
            "Project Name": "str",
            "Package_ID": "str",
            "Address/Postcode": "str",
            "Secondary Organisation": "str",
        },
        "uniques": ["Project_ID"],
        "foreign_keys": {
            "Package_ID": {"parent_table": "Package_Dim", "parent_pk": "Package_ID"}
        },
    },
    "Package_Dim": {
        "columns": {
            "Package_ID": "str",
            "Package_Name": "str",
            "FundType_ID": "str",
            "Organisation": "str",
            "Name Contact Email": "str",
            "Project SRO Email": "str",
            "CFO Email": "str",
            "M&E Email": "str",
        },
        "uniques": ["Package_ID"],
        "foreign_keys": {
            "Organisation": {
                "parent_table": "Organisation_Dim",
                "parent_pk": "Organisation",
            },
            "Name Contact Email": {
                "parent_table": "Contact_Dim",
                "parent_pk": "Email Address",
            },
            "Project SRO Email": {
                "parent_table": "Contact_Dim",
                "parent_pk": "Email Address",
            },
            "CFO Email": {"parent_table": "Contact_Dim", "parent_pk": "Email Address"},
            "M&E Email": {"parent_table": "Contact_Dim", "parent_pk": "Email Address"},
        },
    },
    "Contact_Dim": {
        "columns": {
            "Email Address": "str",
            "Contact Name": "str",
            "Organisation": "str",
            "Telephone": "str",
        },
        "uniques": ["Email Address"],
        "foreign_keys": {
            "Organisation": {
                "parent_table": "Organisation_Dim",
                "parent_pk": "Organisation",
            }
        },
    },
    "Organisation_Dim": {
        "columns": {"Organisation": "str", "Geography": "str"},
        "uniques": ["Organisation"],
    },
    "Project_Delivery_Plan": {
        "columns": {
            "Milestone": "str",
            "Project_ID": "str",
            "Start_Date": "datetime",
            "Finish_Date": "datetime",
            "Status": "str",
            "Comments": "str",
        },
        "foreign_keys": {
            "Project_ID": {"parent_table": "Project_Dim", "parent_pk": "Project_ID"}
        },
        "enums": {"Status": enums.StatusEnum},
    },
    "Procurement": {
        "columns": {
            "Construction_Contract": "str",
            "Project_ID": "str",
            "Start_Date": "datetime",
            "Completion_Date": "datetime",
            "Status": "str",
            "Procurement_Status": "str",
            "Comments": "str",
        },
        "foreign_keys": {
            "Project_ID": {"parent_table": "Project_Dim", "parent_pk": "Project_ID"}
        },
        "enums": {
            "Status": enums.StatusEnum,
            "Procurement_Status": enums.ProcurementStatusEnum,
        },
    },
    "Project_Progress": {
        "columns": {
            "Package_ID": "str",
            "Question_1": "str",
            "Question_2": "str",
            "Question_3": "str",
            "Question_4": "str",
            "Question_5": "str",
            "Question_6": "str",
        },
        "foreign_keys": {
            "Package_ID": {"parent_table": "Package_Dim", "parent_pk": "Package_ID"}
        },
    },
    "DirectFund_Data": {
        "columns": {
            "Project_ID": "str",
            "Start_Date": "datetime",
            "End_Date": "datetime",
            "Actual/Forecast": "str",
            "PRA/Other": "str",
            "Amount": "float",
            "How much of your forecast is contractually committed": "float",
        },
        "foreign_keys": {
            "Project_ID": {"parent_table": "Project_Dim", "parent_pk": "Project_ID"}
        },
        "enums": {
            "Actual/Forecast": enums.StateEnum,
            "PRA/Other": enums.PRAEnum,
        },
    },
    "Capital_Data": {
        "columns": {
            "Project_ID": "str",
            "Start_Date": "datetime",
            "End_Date": "datetime",
            "Actual/Forecast": "str",
            "Amount": "float",
        },
        "foreign_keys": {
            "Project_ID": {"parent_table": "Project_Dim", "parent_pk": "Project_ID"}
        },
        "enums": {"Actual/Forecast": enums.StateEnum},
    },
    "IndirectFundSecured_Data": {
        "columns": {
            "Project_ID": "str",
            "Start_Date": "datetime",
            "End_Date": "datetime",
            "NameOfFundingSource": "str",
            "FundingSourceCategory": "str",
            "Actual/Forecast": "str",
            "Amount": "float",
        },
        "foreign_keys": {
            "Project_ID": {"parent_table": "Project_Dim", "parent_pk": "Project_ID"}
        },
        "enums": {
            "FundingSourceCategory": enums.FundingSourceCategoryEnum,
            "Actual/Forecast": enums.StateEnum,
        },
    },
    "IndirectFundUnsecured_Data": {
        "columns": {
            "Project_ID": "str",
            "Start_Date": "datetime",
            "End_Date": "datetime",
            "NameOfFundingSource": "str",
            "FundingSourceCategory": "str",
            "Actual/Forecast": "str",
            "Amount": "float",
            "CurrentStatus": "str",
            "Commentary": "str",
            "PotentialSecureDate": "datetime",
        },
        "foreign_keys": {
            "Project_ID": {"parent_table": "Project_Dim", "parent_pk": "Project_ID"}
        },
        "enums": {
            "FundingSourceCategory": enums.FundingSourceCategoryEnum,
            "Actual/Forecast": enums.StateEnum,
        },
    },
    "Output_Data": {
        "columns": {
            "Project_ID": "str",
            "Start_Date": "datetime",
            "End_Date": "datetime",
            "Output": "str",
            "Unit of Measurement": "str",
            "Actual/Forecast": "str",
            "Amount": "float",
        },
        "foreign_keys": {
            "Project_ID": {"parent_table": "Project_Dim", "parent_pk": "Project_ID"},
            "Output": {"parent_table": "Outputs_Dim", "parent_pk": "Output Name"},
        },
        "enums": {"Actual/Forecast": enums.StateEnum},
    },
    "Outputs_Dim": {
        "columns": {"Output Name": "str", "Output Category": "str"},
        "uniques": ["Output Name"],
    },
    "Outcome_Data": {
        "columns": {
            "Project": "str",
            "Start_Date": "datetime",
            "End_Date": "datetime",
            "Outcome": "str",
            "UnitofMeasurement": "str",
            "GeographyIndicator": "str",
            "Amount": "int",
            "Actual/Forecast": "str",
        },
        "foreign_keys": {
            "Project": {"parent_table": "Project_Dim", "parent_pk": "Project_ID"},
            "Outcome": {"parent_table": "Outcome_Dim", "parent_pk": "Outcome_Name"},
        },
        "enums": {
            "GeographyIndicator": enums.GeographyIndicatorEnum,
            "Actual/Forecast": enums.StateEnum,
        },
    },
    "Outcome_Dim": {
        "columns": {"Outcome_Name": "str", "Outcome_Category": "str"},
        "uniques": ["Outcome_Name"],
    },
    "Intervention_Dim": {
        "columns": {"Intervention_ID": "str", "Intervention_Name": "str"},
        "uniques": ["Intervention_ID"],
    },
    "RiskRegister": {
        "columns": {
            "Project_ID": "str",
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
            "Project_ID": {"parent_table": "Project_Dim", "parent_pk": "Project_ID"}
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
