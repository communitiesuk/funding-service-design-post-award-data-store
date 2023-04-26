from dataclasses import dataclass, field

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import MetaData

from core.db import models

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

    project: [list[models.Project]] = field(default_factory=list)
    package: [list[models.Package]] = field(default_factory=list)
    contact: [list[models.Contact]] = field(default_factory=list)
    organisation: [list[models.Organisation]] = field(default_factory=list)
    project_delivery_plan: [list[models.ProjectDeliveryPlan]] = field(
        default_factory=list
    )
    procurement: [list[models.Procurement]] = field(default_factory=list)
    project_progress: [list[models.ProjectProgress]] = field(default_factory=list)
    direct_fund: [list[models.DirectFund]] = field(default_factory=list)
    capital: [list[models.Capital]] = field(default_factory=list)
    indirect_fund_secured: [list[models.IndirectFundSecured]] = field(
        default_factory=list
    )
    indirect_fund_unsecured: [list[models.IndirectFundUnsecured]] = field(
        default_factory=list
    )
    output_data: [list[models.OutputData]] = field(default_factory=list)
    outputs_dim: [list[models.OutputsDim]] = field(default_factory=list)
    outcome_data: [list[models.OutcomeData]] = field(default_factory=list)
    outcome_dim: [list[models.OutcomeDim]] = field(default_factory=list)
    risk_register: [list[models.RiskRegister]] = field(default_factory=list)

    DB_MAPPING = {
        # sheet_name: (model_obj, db_attr)
        "Project_Dim": (models.Project, "project"),
        "Package_Dim": (models.Package, "package"),
        "Contact_Dim": (models.Contact, "contact"),
        "Organisation_Dim": (models.Organisation, "organisation"),
        "Project_Delivery_Plan": (models.ProjectDeliveryPlan, "project_delivery_plan"),
        "Procurement": (models.Procurement, "procurement"),
        "Project_Progress": (models.ProjectProgress, "project_progress"),
        "DirectFund_Data": (models.DirectFund, "direct_fund"),
        "Capital_Data": (models.Capital, "capital"),
        "IndirectFundSecured_Data": (
            models.IndirectFundSecured,
            "indirect_fund_secured",
        ),
        "IndirectFundUnsecured_Data": (
            models.IndirectFundUnsecured,
            "indirect_fund_unsecured",
        ),
        "Output_Data": (models.OutputData, "output_data"),
        "Outputs_Dim": (models.OutputsDim, "outputs_dim"),
        "Outcome_Data": (models.OutcomeData, "outcome_data"),
        "Outcome_Dim": (models.OutcomeDim, "outcome_dim"),
        "RiskRegister": (models.RiskRegister, "risk_register"),
    }

    @classmethod
    def from_dataframe(cls, workbook_dfs):
        workbook_dicts = {
            sheet_name: sheet.fillna("").to_dict(orient="records")
            for sheet_name, sheet in workbook_dfs.items()
        }
        db_attributes = {
            db_attr: [
                model_obj.from_dict(row) for row in workbook_dicts.get(sheet_name, [])
            ]
            for sheet_name, (model_obj, db_attr) in cls.DB_MAPPING.items()
        }
        return cls(**db_attributes)
