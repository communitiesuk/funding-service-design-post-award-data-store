from dataclasses import dataclass

import pandas as pd

from core.db import models


@dataclass
class FakeDB:
    """
    A mock database made from lists of dataclasses.

    Example usage:
    >>> db = FakeDB.from_file("db/DLUCH_Data_Model_V3.4_clean.xlsx")
    >>> [model.as_dict() for model in
    ... filter(lambda x: x.project_id == "LUF0052", db.project)]  # doctest: +ELLIPSIS
    [{'project_id': 'LUF0052', 'project_name': 'Thriving Gainsborough', ...}]
    """

    project: list[models.Project]
    package: list[models.Package]
    contact: list[models.Contact]
    organisation: list[models.Organisation]
    project_delivery_plan: list[models.ProjectDeliveryPlan]
    procurement: list[models.Procurement]
    project_progress: list[models.ProjectProgress]
    direct_fund: list[models.DirectFund]
    capital: list[models.Capital]
    indirect_fund_secured: list[models.IndirectFundSecured]
    indirect_fund_unsecured: list[models.IndirectFundUnsecured]
    output_data: list[models.OutputData]
    outputs_dim: list[models.OutputsDim]
    outcome_data: list[models.OutcomeData]
    outcome_dim: list[models.OutcomeDim]
    risk_register: list[models.RiskRegister]

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
    def from_file(cls, path: str):
        workbook_dfs = pd.read_excel(path, sheet_name=list(cls.DB_MAPPING.keys()))
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


MOCK_DB = FakeDB.from_file(
    "core/db/DLUCH_Data_Model_V3.4_EXAMPLE.xlsx"
)  # simple version of the spreadsheet. Correct structure with minimal fake data
