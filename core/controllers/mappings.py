"""This module contains a set of data mappings that define how to import data from Excel workbooks into a SQL database.

Each DataMapping object maps a worksheet to a database table, defining how to convert column names, map foreign keys,
and instantiate database models. The TOWNS_FUND_MAPPINGS variable defines a sequence of DataMappings in the order they
should be loaded into the database to satisfy foreign key constraints.
"""
from collections import namedtuple
from dataclasses import dataclass, field
from typing import Any

import pandas as pd
import sqlalchemy as sqla

from core.db import db
from core.db import entities as ents

FKMapping = namedtuple("FKMapping", ["parent_pk", "parent_model", "child_fk", "child_lookup"])


@dataclass
class DataMapping:
    """A class that maps a worksheet to a database table.

    :param worksheet_name: The name of the worksheet to map.
    :param model: The database model to map the worksheet to.
    :param columns: A mapping of worksheet column names to database column names.
    :param fk_relations: A list of foreign key mappings to use when mapping the worksheet to the database.
    """

    worksheet_name: str
    model: db.Model
    columns: dict[str, str]
    fk_relations: list[FKMapping] = field(default_factory=list)

    def map_worksheet_to_models(self, worksheet: pd.DataFrame) -> list[db.Model]:
        """Maps the given worksheet to a list of database models.

        :param worksheet: The worksheet to map.
        :return: A list of database models.
        """
        ws_rows = worksheet.to_dict("records")

        models = []
        for row in ws_rows:
            db_row = {self.columns[k]: v for k, v in row.items()}  # convert workbook names to database names

            for parent_pk, parent_model, child_fk, child_lookup in self.fk_relations:
                db_row[child_fk] = lookup_fk_row(parent_model, parent_pk, db_row[child_lookup])
                if child_fk != child_lookup:  # if they're the same then it's been replaced so don't delete
                    del db_row[child_lookup]

            models.append(self.model(**db_row))

        return models


# Defines a set of mappings in the order they are loaded into the db (important due to FK constraints).
TOWNS_FUND_MAPPINGS = (
    DataMapping(
        worksheet_name="Organisation_Dim",
        model=ents.Organisation,
        columns={
            "Organisation": "organisation_name",
            "Geography": "geography",
        },
    ),
    DataMapping(
        worksheet_name="Contact_Dim",
        model=ents.Contact,
        columns={
            "Email Address": "email_address",
            "Contact Name": "contact_name",
            "Organisation": "organisation",
            "Telephone": "telephone",
        },
        fk_relations=[("organisation_name", ents.Organisation, "organisation_id", "organisation")],
    ),
    DataMapping(
        worksheet_name="Package_Dim",
        model=ents.Package,
        columns={
            "Package_ID": "package_id",
            "Package_Name": "package_name",
            "FundType_ID": "fund_type_id",
            "Organisation": "organisation",
            "Name Contact Email": "name_contact",
            "Project SRO Email": "project_sro_contact",
            "CFO Email": "cfo_contact",
            "M&E Email": "m_and_e_contact",
        },
        fk_relations=[
            ("organisation_name", ents.Organisation, "organisation_id", "organisation"),
            ("email_address", ents.Contact, "name_contact_id", "name_contact"),
            ("email_address", ents.Contact, "project_sro_contact_id", "project_sro_contact"),
            ("email_address", ents.Contact, "cfo_contact_id", "cfo_contact"),
            ("email_address", ents.Contact, "m_and_e_contact_id", "m_and_e_contact"),
        ],
    ),
    DataMapping(
        worksheet_name="Project_Dim",
        model=ents.Project,
        columns={
            "Project_ID": "project_id",
            "Project Name": "project_name",
            "Package_ID": "package_id",
            "Address/Postcode": "address",
            "Secondary Organisation": "secondary_organisation",
        },
        fk_relations=[("package_id", ents.Package, "package_id", "package_id")],
    ),
    DataMapping(
        worksheet_name="Project_Delivery_Plan",
        model=ents.ProjectDeliveryPlan,
        columns={
            "Milestone": "milestone",
            "Project_ID": "project_id",
            "Start_Date": "start_date",
            "Finish_Date": "end_date",
            "Status": "status",
            "Comments": "comments",
        },
        fk_relations=[("project_id", ents.Project, "project_id", "project_id")],
    ),
    DataMapping(
        worksheet_name="Procurement",
        model=ents.Procurement,
        columns={
            "Construction_Contract": "construction_contract",
            "Project_ID": "project_id",
            "Start_Date": "start_date",
            "Completion_Date": "end_date",
            "Status": "status",
            "Procurement_Status": "procurement_status",
            "Comments": "comments",
        },
        fk_relations=[("project_id", ents.Project, "project_id", "project_id")],
    ),
    DataMapping(
        worksheet_name="Project_Progress",
        model=ents.ProjectProgress,
        columns={
            "Package_ID": "package_id",
            "Question_1": "answer_1",
            "Question_2": "answer_2",
            "Question_3": "answer_3",
            "Question_4": "answer_4",
            "Question_5": "answer_5",
            "Question_6": "answer_6",
        },
        fk_relations=[("package_id", ents.Package, "package_id", "package_id")],
    ),
    DataMapping(
        worksheet_name="DirectFund_Data",
        model=ents.DirectFund,
        columns={
            "Project_ID": "project_id",
            "Start_Date": "start_date",
            "End_Date": "end_date",
            "Actual/Forecast": "state",
            "PRA/Other": "pra_or_other",
            "Amount": "amount",
            "How much of your forecast is contractually committed": "contractually_committed_amount",
        },
        fk_relations=[("project_id", ents.Project, "project_id", "project_id")],
    ),
    DataMapping(
        worksheet_name="Capital_Data",
        model=ents.Capital,
        columns={
            "Project_ID": "project_id",
            "Start_Date": "start_date",
            "End_Date": "end_date",
            "Actual/Forecast": "state",
            "Amount": "amount",
        },
        fk_relations=[("project_id", ents.Project, "project_id", "project_id")],
    ),
    DataMapping(
        worksheet_name="IndirectFundSecured_Data",
        model=ents.IndirectFundSecured,
        columns={
            "Project_ID": "project_id",
            "Start_Date": "start_date",
            "End_Date": "end_date",
            "NameOfFundingSource": "funding_source_name",
            "FundingSourceCategory": "funding_source_category",
            "Actual/Forecast": "state",
            "Amount": "amount",
        },
        fk_relations=[("project_id", ents.Project, "project_id", "project_id")],
    ),
    DataMapping(
        worksheet_name="IndirectFundUnsecured_Data",
        model=ents.IndirectFundUnsecured,
        columns={
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
        },
        fk_relations=[("project_id", ents.Project, "project_id", "project_id")],
    ),
    DataMapping(
        worksheet_name="Outputs_Dim",
        model=ents.OutputDim,
        columns={"Output Name": "output_name", "Output Category": "output_category"},
    ),
    DataMapping(
        worksheet_name="Output_Data",
        model=ents.OutputData,
        columns={
            "Project_ID": "project_id",
            "Start_Date": "start_date",
            "End_Date": "end_date",
            "Output": "output",
            "Unit of Measurement": "unit_of_measurement",
            "Actual/Forecast": "state",
            "Amount": "amount",
        },
        fk_relations=[
            ("project_id", ents.Project, "project_id", "project_id"),
            ("output_name", ents.OutputDim, "output_dim_id", "output"),
        ],
    ),
    DataMapping(
        worksheet_name="Outcome_Dim",
        model=ents.OutcomeDim,
        columns={"Outcome_Name": "outcome_name", "Outcome_Category": "outcome_category"},
    ),
    DataMapping(
        worksheet_name="Outcome_Data",
        model=ents.OutcomeData,
        columns={
            "Project": "project_id",
            "Start_Date": "start_date",
            "End_Date": "end_date",
            "Outcome": "outcome",
            "UnitofMeasurement": "unit_of_measurement",
            "GeographyIndicator": "geography_indicator",
            "Amount": "amount",
            "Actual/Forecast": "state",
        },
        fk_relations=[
            ("project_id", ents.Project, "project_id", "project_id"),
            ("outcome_name", ents.OutcomeDim, "outcome_dim_id", "outcome"),
        ],
    ),
    DataMapping(
        worksheet_name="RiskRegister",
        model=ents.RiskRegister,
        columns={
            "Project_ID": "project_id",
            "RiskName": "risk_name",
            "RiskCategory": "risk_category",
            "Short Description": "short_desc",
            "Full Description": "full_desc",
            "Consequences": "consequences",
            "Pre-mitigatedImpact": "pre_mitigated_impact",
            "Pre-mitigatedLikelihood": "pre_mitigated_likelihood",
            "Mitigatons": "mitigations",
            "PostMitigatedImpact": "post_mitigated_impact",
            "PostMitigatedLikelihood": "post_mitigated_likelihood",
            "Proximity": "proximity",
            "RiskOwnerRole": "risk_owner_role",
        },
        fk_relations=[
            ("project_id", ents.Project, "project_id", "project_id"),
        ],
    ),
)


def lookup_fk_row(model: db.Model, lookup_field: str, lookup_val: Any) -> str:
    """Lookup the id of a row in a DB table based on specified field value."""
    stmt = sqla.select(model).where(getattr(model, lookup_field) == lookup_val)
    return str(db.session.scalars(stmt).first().id)  # hacky cast to string as SQLite does not support UUID.
