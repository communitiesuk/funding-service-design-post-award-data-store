"""This module contains a set of data mappings that define how to import data from Excel workbooks into a SQL database.

Each DataMapping object maps a worksheet to a database table, defining how to convert column names, map foreign keys,
and instantiate database models. The INGEST_MAPPINGS variable defines a sequence of DataMappings in the order they
should be loaded into the database to satisfy foreign key constraints.
"""
from collections import namedtuple
from dataclasses import dataclass, field
from typing import Any

import pandas as pd
import sqlalchemy as sqla

from core.db import db
from core.db import entities as ents

FKMapping = namedtuple(
    "FKMapping",
    [
        "parent_pk",  # pk attribute name in the parent sqla model
        "parent_model",  # parent slqa model class
        "child_fk",  # final attribute name of the FK to the parent (where the value is parent_model.id)
        "child_lookup",  # lookup column name in the child dataframe (this value matches parent_pk)
    ],
)


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
            # convert workbook names to database names and map empty string to None
            db_row = {self.columns[k]: v or (None if v == "" else v) for k, v in row.items()}

            for parent_pk, parent_model, child_fk, child_lookup in self.fk_relations:
                db_row[child_fk] = self.lookup_fk_row(parent_model, parent_pk, db_row[child_lookup])
                if child_fk != child_lookup:  # if they're the same then it's been replaced so don't delete
                    del db_row[child_lookup]

            models.append(self.model(**db_row))

        return models

    @staticmethod
    def lookup_fk_row(model: db.Model, lookup_field: str, lookup_val: Any) -> str | None:
        """Lookup the id of a row in a DB table based on specified field value."""
        stmt = sqla.select(model).where(getattr(model, lookup_field) == lookup_val)
        if fk_ent := db.session.scalars(stmt).first():
            return fk_ent.id  # hacky cast to string as SQLite does not support UUID.
        else:
            return None


# Defines a set of mappings in the order they are loaded into the db (important due to FK constraints).
INGEST_MAPPINGS = (
    DataMapping(
        worksheet_name="Submission_Ref",
        model=ents.Submission,
        columns={
            "Submission ID": "submission_id",
            "Submission Date": "submission_date",
            "Reporting Period Start": "reporting_period_start",
            "Reporting Period End": "reporting_period_end",
            "Reporting Round": "reporting_round",
        },
    ),
    DataMapping(
        worksheet_name="Organisation_Ref",
        model=ents.Organisation,
        columns={
            "Organisation ID": "organisation_id",
            "Organisation": "organisation_name",
            "Geography": "geography",
        },
    ),
    DataMapping(
        worksheet_name="Programme_Ref",
        model=ents.Programme,
        columns={
            "Programme ID": "programme_id",
            "Programme Name": "programme_name",
            "FundType_ID": "fund_type_id",
            "Organisation ID": "organisation_id",
        },
        fk_relations=[("organisation_id", ents.Organisation, "organisation_id", "organisation_id")],
    ),
    DataMapping(
        worksheet_name="Programme Progress",
        model=ents.ProgrammeProgress,
        columns={
            "Submission ID": "submission_id",
            "Programme ID": "programme_id",
            "Question": "question",
            "Answer": "answer",
        },
        fk_relations=[
            ("submission_id", ents.Submission, "submission_id", "submission_id"),
            ("programme_id", ents.Programme, "programme_id", "programme_id"),
        ],
    ),
    DataMapping(
        worksheet_name="Place Details",
        model=ents.PlaceDetail,
        columns={
            "Submission ID": "submission_id",
            "Programme ID": "programme_id",
            "Question": "question",
            "Answer": "answer",
            "Indicator": "indicator",
        },
        fk_relations=[
            ("submission_id", ents.Submission, "submission_id", "submission_id"),
            ("programme_id", ents.Programme, "programme_id", "programme_id"),
        ],
    ),
    DataMapping(
        worksheet_name="Funding Questions",
        model=ents.FundingQuestion,
        columns={
            "Submission ID": "submission_id",
            "Programme ID": "programme_id",
            "Question": "question",
            "Indicator": "indicator",
            "Response": "response",
            "Guidance Notes": "guidance_notes",
        },
        fk_relations=[
            ("submission_id", ents.Submission, "submission_id", "submission_id"),
            ("programme_id", ents.Programme, "programme_id", "programme_id"),
        ],
    ),
    DataMapping(
        worksheet_name="Project Details",
        model=ents.Project,
        columns={
            "Submission ID": "submission_id",
            "Project ID": "project_id",
            "Programme ID": "programme_id",
            "Project Name": "project_name",
            "Primary Intervention Theme": "primary_intervention_theme",
            "Single or Multiple Locations": "location_multiplicity",
            "Locations": "locations",
            "GIS Provided": "gis_provided",
            "Lat/Long": "lat_long",
        },
        fk_relations=[
            ("submission_id", ents.Submission, "submission_id", "submission_id"),
            ("programme_id", ents.Programme, "programme_id", "programme_id"),
        ],
    ),
    DataMapping(
        worksheet_name="Project Progress",
        model=ents.ProjectProgress,
        columns={
            "Submission ID": "submission_id",
            "Project ID": "project_id",
            "Start Date": "start_date",
            "Completion Date": "end_date",
            "Project Adjustment Request Status": "adjustment_request_status",
            "Project Delivery Status": "delivery_status",
            "Delivery (RAG)": "delivery_rag",
            "Spend (RAG)": "spend_rag",
            "Risk (RAG)": "risk_rag",
            "Commentary on Status and RAG Ratings": "commentary",
            "Most Important Upcoming Comms Milestone": "important_milestone",
            "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": "date_of_important_milestone",
        },
        fk_relations=[
            ("submission_id", ents.Submission, "submission_id", "submission_id"),
            ("project_id", ents.Project, "project_id", "project_id"),
        ],
    ),
    DataMapping(
        worksheet_name="Funding",
        model=ents.Funding,
        columns={
            "Submission ID": "submission_id",
            "Project ID": "project_id",
            "Funding Source Name": "funding_source_name",
            "Funding Source Type": "funding_source_type",
            "Secured": "secured",
            "Spend Before Reporting Commenced": "spend_before_reporting_commenced",
            "Reporting Period": "reporting_period",
            "Spend for Reporting Period": "spend_for_reporting_period",
            "Actual / Forecast": "status",
            "Spend Beyond Fund Lifetime": "spend_beyond_fund_lifetime",
        },
        fk_relations=[
            ("submission_id", ents.Submission, "submission_id", "submission_id"),
            ("project_id", ents.Project, "project_id", "project_id"),
        ],
    ),
    DataMapping(
        worksheet_name="Funding Comments",
        model=ents.FundingComment,
        columns={
            "Submission ID": "submission_id",
            "Project ID": "project_id",
            "Comment": "comment",
        },
        fk_relations=[
            ("submission_id", ents.Submission, "submission_id", "submission_id"),
            ("project_id", ents.Project, "project_id", "project_id"),
        ],
    ),
    DataMapping(
        worksheet_name="Private Investments",
        model=ents.PrivateInvestment,
        columns={
            "Submission ID": "submission_id",
            "Project ID": "project_id",
            "Total Project Value": "total_project_value",
            "Townsfund Funding": "townsfund_funding",
            "Private Sector Funding Required": "private_sector_funding_required",
            "Private Sector Funding Secured": "private_sector_funding_secured",
            "Additional Comments": "additional_comments",
        },
        fk_relations=[
            ("submission_id", ents.Submission, "submission_id", "submission_id"),
            ("project_id", ents.Project, "project_id", "project_id"),
        ],
    ),
    DataMapping(
        worksheet_name="Outputs_Ref",
        model=ents.OutputDim,
        columns={
            "Output Name": "output_name",
            "Output Category": "output_category",
        },
    ),
    DataMapping(
        worksheet_name="Output_Data",
        model=ents.OutputData,
        columns={
            "Submission ID": "submission_id",
            "Project ID": "project_id",
            "Start_Date": "start_date",
            "End_Date": "end_date",
            "Output": "output",
            "Unit of Measurement": "unit_of_measurement",
            "Actual/Forecast": "state",
            "Amount": "amount",
            "Additional Information": "additional_information",
        },
        fk_relations=[
            ("submission_id", ents.Submission, "submission_id", "submission_id"),
            ("project_id", ents.Project, "project_id", "project_id"),
            ("output_name", ents.OutputDim, "output_id", "output"),
        ],
    ),
    DataMapping(
        worksheet_name="Outcome_Ref",
        model=ents.OutcomeDim,
        columns={"Outcome_Name": "outcome_name", "Outcome_Category": "outcome_category"},
    ),
    DataMapping(
        worksheet_name="Outcome_Data",
        model=ents.OutcomeData,
        columns={
            "Submission ID": "submission_id",
            "Project ID": "project_id",
            "Programme ID": "programme_id",
            "Outcome": "outcome",
            "Start_Date": "start_date",
            "End_Date": "end_date",
            "UnitofMeasurement": "unit_of_measurement",
            "GeographyIndicator": "geography_indicator",
            "Amount": "amount",
            "Actual/Forecast": "state",
            "Higher Frequency": "higher_frequency",
        },
        fk_relations=[
            ("submission_id", ents.Submission, "submission_id", "submission_id"),
            ("programme_id", ents.Programme, "programme_id", "programme_id"),
            ("project_id", ents.Project, "project_id", "project_id"),
            ("outcome_name", ents.OutcomeDim, "outcome_id", "outcome"),
        ],
    ),
    DataMapping(
        worksheet_name="RiskRegister",
        model=ents.RiskRegister,
        columns={
            "Submission ID": "submission_id",
            "Programme ID": "programme_id",
            "Project ID": "project_id",
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
            ("submission_id", ents.Submission, "submission_id", "submission_id"),
            ("programme_id", ents.Programme, "programme_id", "programme_id"),
            ("project_id", ents.Project, "project_id", "project_id"),
        ],
    ),
)
