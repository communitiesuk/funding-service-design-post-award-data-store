"""
Fake DB model for prototyping use.

Fake model consisting of dataclasses that replicate individual DB tables. For
storing prototype data only, there are no referential constraints enforced at
model/fake DB level.
"""
import inspect
from dataclasses import dataclass
from datetime import datetime


class BaseModel:
    def __new__(cls, *args, **kwargs):
        if cls is BaseModel:
            raise TypeError(f"only children of '{cls.__name__}' may be instantiated")
        return super().__new__(cls)

    @classmethod
    def from_dict(cls, d: dict):
        try:
            lookup = getattr(cls, "DB_MAPPING")
            d = {lookup[k]: v for k, v in d.items()}
        except AttributeError:
            pass

        # Filter unknown fields from JSON dictionary
        return cls(
            **{k: v for k, v in d.items() if k in inspect.signature(cls).parameters}
        )

    def as_dict(self):
        return vars(self)


@dataclass
class Project(BaseModel):
    project_id: str
    project_name: str
    package_id: str
    address: str
    secondary_organisation: str

    DB_MAPPING = {
        "Address/Postcode": "address",
        "Package_ID": "package_id",
        "Project Name": "project_name",
        "Project_ID": "project_id",
        "Secondary Organisation": "secondary_organisation",
    }


@dataclass
class Package(BaseModel):
    package_id: str
    package_name: str
    fund_type_id: str
    organisation: str
    contact_email: str
    project_sro_email: str
    cfo_email: str
    m_and_e_email: str

    DB_MAPPING = {
        "CFO Email": "cfo_email",
        "FundType_ID": "fund_type_id",
        "M&E Email": "m_and_e_email",
        "Name Contact Email": "contact_email",
        "Organisation": "organisation",
        "Package_ID": "package_id",
        "Package_Name": "package_name",
        "Project SRO Email": "project_sro_email",
    }


@dataclass
class Contact(BaseModel):
    email_address: str
    contact_name: str
    organisation: str
    telephone: str

    DB_MAPPING = {
        "Contact Name": "contact_name",
        "Email Address": "email_address",
        "Organisation": "organisation",
        "Telephone": "telephone",
    }


@dataclass
class Organisation(BaseModel):
    organisation: str
    geography: str

    DB_MAPPING = {"Geography": "geography", "Organisation": "organisation"}


@dataclass
class ProjectDeliveryPlan(BaseModel):
    milestone: str
    project_id: str
    start_date: datetime
    finish_date: datetime
    status: str
    comments: str

    DB_MAPPING = {
        "Milestone": "milestone",
        "Project_ID": "project_id",
        "Start_Date": "start_date",
        "Finish_Date": "finish_date",
        "Status": "status",
        "Comments": "comments",
    }


@dataclass
class Procurement(BaseModel):
    construction_contract: str
    project_id: str
    start_date: datetime
    completion_date: datetime
    status: str
    procurement_status: str
    comments: str

    DB_MAPPING = {
        "Construction_Contract": "construction_contract",
        "Project_ID": "project_id",
        "Start_Date": "start_date",
        "Completion_Date": "completion_date",
        "Status": "status",
        "Procurement_Status": "procurement_status",
        "Comments": "comments",
    }


@dataclass
class ProjectProgress(BaseModel):
    # TODO: Where are the questions?
    #  Do we need a new model to be able to configure for multiple funds?

    package_id: str
    answer_1: str
    answer_2: str
    answer_3: str
    answer_4: str
    answer_5: str
    answer_6: str

    DB_MAPPING = {
        "Package_ID": "package_id",
        "Question_1": "answer_1",
        "Question_2": "answer_2",
        "Question_3": "answer_3",
        "Question_4": "answer_4",
        "Question_5": "answer_5",
        "Question_6": "answer_6",
    }


@dataclass
class DirectFund(BaseModel):
    project_id: str  # primary key
    start_date: datetime
    end_date: datetime
    state: str  # enum / choice field "Actual" or "Forecast"
    pra_or_other: str  # better name? enum or is other free text?
    amount: float
    contractually_committed_amount: float

    DB_MAPPING = {
        "Project_ID": "project_id",
        "Start_Date": "start_date",
        "End_Date": "end_date",
        "Actual/Forecast": "state",
        "PRA/Other": "pra_or_other",
        "Amount": "amount",
        "How much of your forecast "
        "is contractually committed": "contractually_committed_amount",
    }


@dataclass
class Capital(BaseModel):
    project_id: str  # primary key
    start_date: datetime
    end_date: datetime
    state: str  # enum / choice field "Actual" or "Forecast"
    amount: float

    DB_MAPPING = {
        "Project_ID": "project_id",
        "Start_Date": "start_date",
        "End_Date": "end_date",
        "Actual/Forecast": "state",
        "Amount": "amount",
    }


@dataclass
class IndirectFundSecured(BaseModel):
    project_id: str  # primary key
    start_date: datetime
    end_date: datetime
    funding_source_name: str  # will these link to entities in organisation model?
    funding_source_category: str  # enum field?
    state: str  # enum / choice field "Actual" or "Forecast"
    amount: float  # TODO: do we need to round this to 2dp on (or after) ingest?

    DB_MAPPING = {
        "Project_ID": "project_id",
        "Start_Date": "start_date",
        "End_Date": "end_date",
        "NameOfFundingSource": "funding_source_name",
        "FundingSourceCategory": "funding_source_category",
        "Actual/Forecast": "state",
        "Amount": "amount",
    }


@dataclass
class IndirectFundUnsecured(BaseModel):
    project_id: str  # primary key
    start_date: datetime
    end_date: datetime
    funding_source_name: str  # will these link to entities in organisation model?
    funding_source_category: str
    state: str
    amount: float  # TODO: do we need to round this to 2dp on (or after) ingest?
    current_status: str  # assumed, no example data
    comments: str  # assumed, no example data
    potential_secure_date: datetime

    DB_MAPPING = {
        "Project_ID": "project_id",
        "Start_Date": "start_date",
        "End_Date": "end_date",
        "NameOfFundingSource": "funding_source_name",
        "FundingSourceCategory": "funding_source_category",
        "Actual/Forecast": "state",
        "Amount": "amount",
        "CurrentStatus": "current_status",
        "Commentary": "comments",
        "PotentialSecureDate": "potential_secure_date",
    }


@dataclass
class OutputData(BaseModel):
    project_id: str
    start_date: datetime
    end_date: datetime
    output: str  # FK to OutputsDim
    unit_of_measurement: str  # also an enum? could it be as part of OutputDim instead?
    state: str  # enum / flag
    amount: float

    DB_MAPPING = {
        "Project_ID": "project_id",
        "Start_Date": "start_date",
        "End_Date": "end_date",
        "Output": "output",
        "Unit of Measurement": "unit_of_measurement",
        "Actual/Forecast": "state",
        "Amount": "amount",
    }


@dataclass
class OutputsDim(BaseModel):
    # Inconsistency between naming of plural 'OutputsDim' and singular 'OutcomeDim'.
    # Inconsistency between naming of columns too e.g. Output Name vs Output_Name
    output_name: str
    output_category: str

    DB_MAPPING = {
        "Output Name": "output_name",
        "Output Category": "output_category",
    }


@dataclass
class OutcomeData(BaseModel):
    project_id: str
    start_date: datetime
    end_date: datetime
    outcome: str  # FK to OutcomeDim
    unit_of_measurement: str  # also an enum? could it be as part of OutputDim instead?
    geography_indicator: str  # will it be an enum? data just includes `Town` as a value
    state: str  # enum / flag
    amount: float

    DB_MAPPING = {
        "Project": "project_id",
        "Start_Date": "start_date",
        "End_Date": "end_date",
        "Outcome": "outcome",
        "UnitofMeasurement": "unit_of_measurement",
        "GeographyIndicator": "geography_indicator",
        "Amount": "amount",
        "Actual/Forecast": "state",
    }


@dataclass
class OutcomeDim(BaseModel):
    outcome_name: str
    outcome_category: str

    DB_MAPPING = {
        "Outcome_Name": "outcome_name",
        "Outcome_Category": "outcome_category",
    }


@dataclass
class RiskRegister(BaseModel):
    project_id: str  # primary key
    risk_name: str
    risk_category: str  # looks like this should be an enum?
    short_desc: str
    full_desc: str
    consequences: str
    pre_mitigated_impact: str  # enum
    pre_mitigated_likelihood: str  # enum
    mitigations: str
    post_mitigated_impact: str  # enum
    post_mitigated_likelihood: str  # enum
    proximity: str  # enum
    risk_owner_role: str

    DB_MAPPING = {
        "Project_ID": "project_id",
        "RiskName": "risk_name",
        "RiskCategory": "risk_category",
        "Short Description": "short_desc",
        "Full Description": "full_desc",
        "Consequences": "consequences",
        "Pre-mitigatedImpact": "pre_mitigated_impact",
        "Pre-mitigatedLikelihood": "pre_mitigated_likelihood",
        "Mitigatons": "mitigations",  # typo in data model spreadsheet
        "PostMitigatedImpact": "post_mitigated_impact",
        "PostMitigatedLikelihood": "post_mitigated_likelihood",
        "Proximity": "proximity",
        "RiskOwnerRole": "risk_owner_role",
    }
