from dataclasses import dataclass, field

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from core.db import fake_models

convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)

db = SQLAlchemy(metadata=metadata)


@dataclass
class FakeDB:
    """
    A mock database made from lists of dataclasses.
    """

    project: [list[fake_models.Project]] = field(default_factory=list)
    package: [list[fake_models.Package]] = field(default_factory=list)
    contact: [list[fake_models.Contact]] = field(default_factory=list)
    organisation: [list[fake_models.Organisation]] = field(default_factory=list)
    project_delivery_plan: [list[fake_models.ProjectDeliveryPlan]] = field(default_factory=list)
    procurement: [list[fake_models.Procurement]] = field(default_factory=list)
    project_progress: [list[fake_models.ProjectProgress]] = field(default_factory=list)
    direct_fund: [list[fake_models.DirectFund]] = field(default_factory=list)
    capital: [list[fake_models.Capital]] = field(default_factory=list)
    indirect_fund_secured: [list[fake_models.IndirectFundSecured]] = field(default_factory=list)
    indirect_fund_unsecured: [list[fake_models.IndirectFundUnsecured]] = field(default_factory=list)
    output_data: [list[fake_models.OutputData]] = field(default_factory=list)
    outputs_dim: [list[fake_models.OutputsDim]] = field(default_factory=list)
    outcome_data: [list[fake_models.OutcomeData]] = field(default_factory=list)
    outcome_dim: [list[fake_models.OutcomeDim]] = field(default_factory=list)
    risk_register: [list[fake_models.RiskRegister]] = field(default_factory=list)

    DB_MAPPING = {
        # sheet_name: (model_obj, db_attr)
        "Project_Dim": (fake_models.Project, "project"),
        "Package_Dim": (fake_models.Package, "package"),
        "Contact_Dim": (fake_models.Contact, "contact"),
        "Organisation_Dim": (fake_models.Organisation, "organisation"),
        "Project_Delivery_Plan": (
            fake_models.ProjectDeliveryPlan,
            "project_delivery_plan",
        ),
        "Procurement": (fake_models.Procurement, "procurement"),
        "Project_Progress": (fake_models.ProjectProgress, "project_progress"),
        "DirectFund_Data": (fake_models.DirectFund, "direct_fund"),
        "Capital_Data": (fake_models.Capital, "capital"),
        "IndirectFundSecured_Data": (
            fake_models.IndirectFundSecured,
            "indirect_fund_secured",
        ),
        "IndirectFundUnsecured_Data": (
            fake_models.IndirectFundUnsecured,
            "indirect_fund_unsecured",
        ),
        "Output_Data": (fake_models.OutputData, "output_data"),
        "Outputs_Dim": (fake_models.OutputsDim, "outputs_dim"),
        "Outcome_Data": (fake_models.OutcomeData, "outcome_data"),
        "Outcome_Dim": (fake_models.OutcomeDim, "outcome_dim"),
        "RiskRegister": (fake_models.RiskRegister, "risk_register"),
    }

    @classmethod
    def from_dataframe(cls, workbook_dfs):
        workbook_dicts = {
            sheet_name: sheet.fillna("").to_dict(orient="records") for sheet_name, sheet in workbook_dfs.items()
        }
        db_attributes = {
            db_attr: [model_obj.from_dict(row) for row in workbook_dicts.get(sheet_name, [])]
            for sheet_name, (model_obj, db_attr) in cls.DB_MAPPING.items()
        }
        return cls(**db_attributes)
