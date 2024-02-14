"""This module contains a set of data mappings that define how to import data from Excel workbooks into a SQL database.

Each DataMapping object maps a pandas DataFrame of data to a database table, defining how to convert column names,
map foreign keys, and instantiate database models. The INGEST_MAPPINGS variable defines a sequence of DataMappings in
the order they should be loaded into the database to satisfy foreign key constraints.
"""
from collections import namedtuple
from dataclasses import dataclass, field
from typing import Any, Type

import pandas as pd

from core.db import db
from core.db import entities as ents
from core.db.entities import BaseModel
from core.db.queries import generic_select_where_query

FKMapping = namedtuple(
    "FKMapping",
    [
        "parent_lookup",  # lookup attribute name in the parent sqla model
        "parent_model",  # parent slqa model class
        "child_fk",  # final attribute name of the FK to the parent (where the value is parent_model.id)
        "child_lookup",  # lookup column name in the child dataframe (this value matches parent_pk)
    ],
)


@dataclass
class DataMapping:
    """A class that maps a table of extracted data to a database table.

    :param table: The name of the table to map.
    :param model: The database model to map the data to.
    :param column_mapping: A mapping of table column names to database column names.
    :param fk_relations: A list of foreign key mappings to use when mapping the data to the database.
    """

    table: str
    model: Type[BaseModel]
    column_mapping: dict[str, str]
    cols_to_jsonb: list[str] = field(default_factory=list)
    fk_relations: list[FKMapping] = field(default_factory=list)

    def map_data_to_models(self, data: pd.DataFrame) -> list[db.Model]:
        """Maps the given data to a list of database models.

        :param data: The data to map.
        :return: A list of database models.
        """
        data.rename(columns=self.column_mapping, inplace=True)

        if self.cols_to_jsonb:
            data = self.move_event_data_to_json_blob(data, self.cols_to_jsonb)
        data_rows = data.to_dict("records")

        models = []
        for row in data_rows:
            # create foreign key relations
            for parent_lookup, parent_model, child_fk, child_lookup_column in self.fk_relations:
                # find parent entity via this lookup
                lookups = {parent_lookup: row[child_lookup_column]}

                # if creating a project id FK then also match on submission id to ensure it relates to the correct round
                if child_fk == "project_id":
                    lookups["submission_id"] = row["submission_id"]

                # set the child FK to match the parent PK
                row[child_fk] = self.get_row_id(parent_model, lookups)

                # delete the now defunct lookup column, unless the child FK and lookup columns are one and the same
                if child_fk != child_lookup_column:
                    del row[child_lookup_column]

            models.append(self.model(**row))

        return models

    @staticmethod
    def get_row_id(model: Type[BaseModel], lookups: dict[str, Any]) -> str | None:
        """Select a row from the database by matching on some WHERE conditions and return its UUID.

        :param model: SQLAlchemy Model to select
        :param lookups: mapping of model attribute names to values to query on
        :return: the ID of the matched Model, otherwise None if the query returns no results
        """
        where_conditions = (getattr(model, attribute) == value for attribute, value in lookups.items())
        query = generic_select_where_query(model, where_conditions)
        row = db.session.scalar(query)
        return row.id if row else None

    @staticmethod
    def move_event_data_to_json_blob(
        data: pd.DataFrame,
        cols_to_jsonb: list[str],
    ) -> pd.DataFrame:
        """Move specified columns into a json_blob field.

        :param data: data for a given table
        :param cols_to_jsonb: columns to be moved into a json blob
        :return: a DataFrame with specified columns moved into a json blob
        """
        df_with_cols_to_move = data[cols_to_jsonb]
        json_blob_col = []

        for row in df_with_cols_to_move.iterrows():
            json_blob_row = {}
            # row[0] is the index for the row in the DataFrame, which can be discarded
            for col_name, col_values in row[1].iteritems():
                json_blob_row[col_name] = col_values
            json_blob_col.append(json_blob_row)

        data.drop(cols_to_jsonb, axis=1, inplace=True)
        data["json_blob"] = json_blob_col

        return data


# Defines a set of mappings in the order they are loaded into the db (important due to FK constraints).
INGEST_MAPPINGS = (
    DataMapping(
        table="Submission_Ref",
        model=ents.Submission,
        column_mapping={
            "Submission ID": "submission_id",
            "Submission Date": "submission_date",
            "Reporting Period Start": "reporting_period_start",
            "Reporting Period End": "reporting_period_end",
            "Reporting Round": "reporting_round",
        },
    ),
    DataMapping(
        table="Organisation_Ref",
        model=ents.Organisation,
        column_mapping={
            "Organisation": "organisation_name",
            "Geography": "geography",
        },
    ),
    DataMapping(
        table="Programme_Ref",
        model=ents.Programme,
        column_mapping={
            "Programme ID": "programme_id",
            "Programme Name": "programme_name",
            "FundType_ID": "fund_type_id",
            "Organisation": "organisation",
        },
        fk_relations=[("organisation_name", ents.Organisation, "organisation_id", "organisation")],
    ),
    DataMapping(
        table="Programme Progress",
        model=ents.ProgrammeProgress,
        column_mapping={
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
        table="Place Details",
        model=ents.PlaceDetail,
        column_mapping={
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
        table="Funding Questions",
        model=ents.FundingQuestion,
        column_mapping={
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
        table="Project Details",
        model=ents.Project,
        column_mapping={
            "Submission ID": "submission_id",
            "Project ID": "project_id",
            "Programme ID": "programme_id",
            "Project Name": "project_name",
            "Primary Intervention Theme": "primary_intervention_theme",
            "Single or Multiple Locations": "location_multiplicity",
            "Locations": "locations",
            "Postcodes": "postcodes",
            "GIS Provided": "gis_provided",
            "Lat/Long": "lat_long",
        },
        fk_relations=[
            ("submission_id", ents.Submission, "submission_id", "submission_id"),
            ("programme_id", ents.Programme, "programme_id", "programme_id"),
        ],
    ),
    DataMapping(
        table="Project Progress",
        model=ents.ProjectProgress,
        column_mapping={
            "Submission ID": "submission_id",
            "Project ID": "project_id",
            "Start Date": "start_date",
            "Completion Date": "end_date",
            "Current Project Delivery Stage": "delivery_stage",
            "Leading Factor of Delay": "leading_factor_of_delay",
            "Project Adjustment Request Status": "adjustment_request_status",
            "Project Delivery Status": "delivery_status",
            "Delivery (RAG)": "delivery_rag",
            "Spend (RAG)": "spend_rag",
            "Risk (RAG)": "risk_rag",
            "Commentary on Status and RAG Ratings": "commentary",
            "Most Important Upcoming Comms Milestone": "important_milestone",
            "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": "date_of_important_milestone",
        },
        cols_to_jsonb=[
            "delivery_stage",
            "leading_factor_of_delay",
            "adjustment_request_status",
            "delivery_status",
            "delivery_rag",
            "spend_rag",
            "risk_rag",
            "commentary",
            "important_milestone",
            "date_of_important_milestone",
        ],
        fk_relations=[
            ("submission_id", ents.Submission, "submission_id", "submission_id"),
            ("project_id", ents.Project, "project_id", "project_id"),
        ],
    ),
    DataMapping(
        table="Funding",
        model=ents.Funding,
        column_mapping={
            "Submission ID": "submission_id",
            "Project ID": "project_id",
            "Funding Source Name": "funding_source_name",
            "Funding Source Type": "funding_source_type",
            "Secured": "secured",
            "Start_Date": "start_date",
            "End_Date": "end_date",
            "Spend for Reporting Period": "spend_for_reporting_period",
            "Actual/Forecast": "status",
        },
        fk_relations=[
            ("submission_id", ents.Submission, "submission_id", "submission_id"),
            ("project_id", ents.Project, "project_id", "project_id"),
        ],
    ),
    DataMapping(
        table="Funding Comments",
        model=ents.FundingComment,
        column_mapping={
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
        table="Private Investments",
        model=ents.PrivateInvestment,
        column_mapping={
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
        table="Outputs_Ref",
        model=ents.OutputDim,
        column_mapping={
            "Output Name": "output_name",
            "Output Category": "output_category",
        },
    ),
    DataMapping(
        table="Output_Data",
        model=ents.OutputData,
        column_mapping={
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
        table="Outcome_Ref",
        model=ents.OutcomeDim,
        column_mapping={"Outcome_Name": "outcome_name", "Outcome_Category": "outcome_category"},
    ),
    DataMapping(
        table="Outcome_Data",
        model=ents.OutcomeData,
        column_mapping={
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
        table="RiskRegister",
        model=ents.RiskRegister,
        column_mapping={
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
