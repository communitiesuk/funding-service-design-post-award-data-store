"""This module contains a set of data mappings that define how to import data from Excel workbooks into a SQL database.

Each DataMapping object maps a pandas DataFrame of data to a database table, defining how to convert column names,
map foreign keys, and instantiate database models. The INGEST_MAPPINGS variable defines a sequence of DataMappings in
the order they should be loaded into the database to satisfy foreign key constraints.
"""

from dataclasses import dataclass, field
from typing import Any, Type

import pandas as pd

from data_store.db import db
from data_store.db import entities as ents
from data_store.db.entities import BaseModel
from data_store.db.queries import generic_select_where_query, get_project_id_fk
from data_store.util import move_data_to_jsonb_blob


@dataclass
class FKMapping:
    parent_lookups: list[str]  # Lookup attribute(s) in the parent model
    parent_model: Type[BaseModel]  # Parent model class
    child_fk: str  # Attribute name of the FK in the child model
    child_lookups: list[str]  # Column name(s) in the child data frame


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

        - Renames columns such that they match those in the data model.
        - Replaces the human-readable values in selected FKs to match the UUIDs for the rows in the parent
        tables corresponding to those values.
        - Moves all specified columns into a JSONB blob where needed.

        In the case of "Programme Junction", two values are needed to perform the FK look-up.
        This requires first looking-up the UUIDs for the corresponding rows in both the Programme_Ref and Submission_Ref
        tables, and then using these values to get the UUID for the row corresponding to both in the ProgrammeJunction
        table.

        FK look-ups for project_id require the context of the submission id for the current ingestion,
        which we can derive from the ProgrammeJunction table once the appropriate FK look-ups have been done.
        This is because we must join Project to ProgrammeJunction on submission_id for the project_id FK look-up, but as
        this is the UUID for submission_id, e.g. the FK, as it appears in the ProgrammeJunction table, we must first
        generate and then look-up the UUID for this current submission.
        This is saved as a global variable to retain the information for whenever this function is called, where it may
        depend on knowledge only accessible to previous calls of this function.

        :param data: The data to map, arranged into DataFrames corresponding to tables in the db.
        :return: A list of database models.
        """
        global CURRENT_SUBMISSION_ID

        renamed_data = data.rename(columns=self.column_mapping).replace("", None)

        if self.cols_to_jsonb:
            renamed_data = move_data_to_jsonb_blob(renamed_data, self.cols_to_jsonb)

        data_rows = renamed_data.to_dict("records")

        models = []
        for row in data_rows:
            # create foreign key relations
            for fk_mapping in self.fk_relations:
                parent_lookups = fk_mapping.parent_lookups
                parent_model = fk_mapping.parent_model
                child_fk = fk_mapping.child_fk
                child_lookups = fk_mapping.child_lookups

                # 'programme_junction_id' requires two look-ups
                if child_fk == "programme_junction_id":
                    programme_parent_lookup, submission_parent_lookup = parent_lookups
                    programme_child_lookup, submission_child_lookup = child_lookups
                    lookups = {
                        programme_parent_lookup: self.get_row_id(
                            ents.Programme, {programme_parent_lookup: row.get(programme_child_lookup)}
                        ),
                        submission_parent_lookup: self.get_row_id(
                            ents.Submission, {submission_parent_lookup: row.get(submission_child_lookup)}
                        ),
                    }
                    if programme_child_lookup in row:
                        del row[programme_child_lookup]
                    if submission_child_lookup in row:
                        del row[submission_child_lookup]
                else:
                    # different funds will lack certain look-ups
                    if not row.get(child_lookups[0]):
                        continue

                    # find parent entity via this lookup
                    lookups = {parent_lookups[0]: row[child_lookups[0]]}

                    if child_fk != child_lookups[0]:
                        del row[child_lookups[0]]

                # set the child FK to match the parent PK
                # project id needs to be looked up via the project's programme junction
                if child_fk == "project_id":
                    row[child_fk] = get_project_id_fk(row[child_fk], CURRENT_SUBMISSION_ID)
                else:
                    row[child_fk] = self.get_row_id(parent_model, lookups)

            models.append(self.model(**row))  # type: ignore

        if self.table == "Programme Junction":
            CURRENT_SUBMISSION_ID = models[0].submission_id

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


# Defines a set of mappings in the order they are loaded into the db (important due to FK constraints).
INGEST_MAPPINGS = (
    DataMapping(
        table="Submission_Ref",
        model=ents.Submission,
        column_mapping={
            "Submission ID": "submission_id",
            "Submission Date": "submission_date",
            "Sign Off Name": "sign_off_name",
            "Sign Off Role": "sign_off_role",
            "Sign Off Date": "sign_off_date",
            "Reporting Round ID": "reporting_round_id",
        },
        cols_to_jsonb=[
            "sign_off_name",
            "sign_off_role",
            "sign_off_date",
        ],
    ),
    DataMapping(
        table="Organisation_Ref",
        model=ents.Organisation,
        column_mapping={
            "Organisation": "organisation_name",
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
        fk_relations=[
            FKMapping(
                parent_lookups=["organisation_name"],
                parent_model=ents.Organisation,
                child_fk="organisation_id",
                child_lookups=["organisation"],
            ),
            FKMapping(
                parent_lookups=["fund_code"],
                parent_model=ents.Fund,
                child_fk="fund_type_id",
                child_lookups=["fund_type_id"],
            ),
        ],
    ),
    DataMapping(
        table="Programme Junction",
        model=ents.ProgrammeJunction,
        column_mapping={
            "Submission ID": "submission_id",
            "Programme ID": "programme_id",
            "Reporting Round ID": "reporting_round_id",
        },
        fk_relations=[
            FKMapping(
                parent_lookups=["submission_id"],
                parent_model=ents.Submission,
                child_fk="submission_id",
                child_lookups=["submission_id"],
            ),
            FKMapping(
                parent_lookups=["programme_id"],
                parent_model=ents.Programme,
                child_fk="programme_id",
                child_lookups=["programme_id"],
            ),
        ],
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
        cols_to_jsonb=[
            "question",
            "answer",
        ],
        fk_relations=[
            FKMapping(
                parent_lookups=["programme_id", "submission_id"],
                parent_model=ents.ProgrammeJunction,
                child_fk="programme_junction_id",
                child_lookups=["programme_id", "submission_id"],
            ),
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
        cols_to_jsonb=[
            "question",
            "indicator",
            "answer",
        ],
        fk_relations=[
            FKMapping(
                parent_lookups=["programme_id", "submission_id"],
                parent_model=ents.ProgrammeJunction,
                child_fk="programme_junction_id",
                child_lookups=["programme_id", "submission_id"],
            ),
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
        cols_to_jsonb=[
            "question",
            "indicator",
            "response",
            "guidance_notes",
        ],
        fk_relations=[
            FKMapping(
                parent_lookups=["programme_id", "submission_id"],
                parent_model=ents.ProgrammeJunction,
                child_fk="programme_junction_id",
                child_lookups=["programme_id", "submission_id"],
            ),
        ],
    ),
    DataMapping(
        table="Project Details",
        model=ents.Project,
        column_mapping={
            "Project ID": "project_id",
            "Submission ID": "submission_id",
            "Programme ID": "programme_id",
            "Project Name": "project_name",
            "Primary Intervention Theme": "primary_intervention_theme",
            "Single or Multiple Locations": "location_multiplicity",
            "Locations": "locations",
            "Postcodes": "postcodes",
            "GIS Provided": "gis_provided",
            "Lat/Long": "lat_long",
        },
        cols_to_jsonb=[
            "primary_intervention_theme",
            "location_multiplicity",
            "locations",
            "gis_provided",
            "lat_long",
        ],
        fk_relations=[
            FKMapping(
                parent_lookups=["programme_id", "submission_id"],
                parent_model=ents.ProgrammeJunction,
                child_fk="programme_junction_id",
                child_lookups=["programme_id", "submission_id"],
            ),
        ],
    ),
    DataMapping(
        table="Project Progress",
        model=ents.ProjectProgress,
        column_mapping={
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
            "Project Status": "project_status",
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
            "project_status",
        ],
        fk_relations=[
            FKMapping(
                parent_lookups=["project_id"],
                parent_model=ents.Project,
                child_fk="project_id",
                child_lookups=["project_id"],
            ),
        ],
    ),
    DataMapping(
        table="Funding",
        model=ents.Funding,
        column_mapping={
            "Submission ID": "submission_id",
            "Project ID": "project_id",
            "Programme ID": "programme_id",
            "Funding Source Name": "funding_source",
            "Funding Category": "funding_category",
            "Funding Source Type": "spend_type",
            "Secured": "secured",
            "Start_Date": "start_date",
            "End_Date": "end_date",
            "Spend for Reporting Period": "spend_for_reporting_period",
            "Actual/Forecast": "state",
        },
        cols_to_jsonb=[
            "funding_source",
            "funding_category",
            "spend_type",
            "secured",
            "spend_for_reporting_period",
            "state",
        ],
        fk_relations=[
            FKMapping(
                parent_lookups=["project_id"],
                parent_model=ents.Project,
                child_fk="project_id",
                child_lookups=["project_id"],
            ),
            FKMapping(
                parent_lookups=["programme_id", "submission_id"],
                parent_model=ents.ProgrammeJunction,
                child_fk="programme_junction_id",
                child_lookups=["programme_id", "submission_id"],
            ),
        ],
    ),
    DataMapping(
        table="Funding Comments",
        model=ents.FundingComment,
        column_mapping={
            "Project ID": "project_id",
            "Comment": "comment",
        },
        cols_to_jsonb=["comment"],
        fk_relations=[
            FKMapping(
                parent_lookups=["project_id"],
                parent_model=ents.Project,
                child_fk="project_id",
                child_lookups=["project_id"],
            ),
        ],
    ),
    DataMapping(
        table="Private Investments",
        model=ents.PrivateInvestment,
        column_mapping={
            "Project ID": "project_id",
            "Total Project Value": "total_project_value",
            "Townsfund Funding": "townsfund_funding",
            "Private Sector Funding Required": "private_sector_funding_required",
            "Private Sector Funding Secured": "private_sector_funding_secured",
            "Additional Comments": "additional_comments",
        },
        cols_to_jsonb=[
            "total_project_value",
            "townsfund_funding",
            "private_sector_funding_required",
            "private_sector_funding_secured",
            "additional_comments",
        ],
        fk_relations=[
            FKMapping(
                parent_lookups=["project_id"],
                parent_model=ents.Project,
                child_fk="project_id",
                child_lookups=["project_id"],
            ),
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
            "Project ID": "project_id",
            "Submission ID": "submission_id",
            "Programme ID": "programme_id",
            "Start_Date": "start_date",
            "End_Date": "end_date",
            "Output": "output",
            "Unit of Measurement": "unit_of_measurement",
            "Actual/Forecast": "state",
            "Amount": "amount",
            "Additional Information": "additional_information",
        },
        cols_to_jsonb=[
            "unit_of_measurement",
            "state",
            "amount",
            "additional_information",
        ],
        fk_relations=[
            FKMapping(
                parent_lookups=["project_id"],
                parent_model=ents.Project,
                child_fk="project_id",
                child_lookups=["project_id"],
            ),
            FKMapping(
                parent_lookups=["programme_id", "submission_id"],
                parent_model=ents.ProgrammeJunction,
                child_fk="programme_junction_id",
                child_lookups=["programme_id", "submission_id"],
            ),
            FKMapping(
                parent_lookups=["output_name"],
                parent_model=ents.OutputDim,
                child_fk="output_id",
                child_lookups=["output"],
            ),
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
            "Project ID": "project_id",
            "Submission ID": "submission_id",
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
        cols_to_jsonb=[
            "unit_of_measurement",
            "geography_indicator",
            "amount",
            "state",
            "higher_frequency",
        ],
        fk_relations=[
            FKMapping(
                parent_lookups=["project_id"],
                parent_model=ents.Project,
                child_fk="project_id",
                child_lookups=["project_id"],
            ),
            FKMapping(
                parent_lookups=["programme_id", "submission_id"],
                parent_model=ents.ProgrammeJunction,
                child_fk="programme_junction_id",
                child_lookups=["programme_id", "submission_id"],
            ),
            FKMapping(
                parent_lookups=["outcome_name"],
                parent_model=ents.OutcomeDim,
                child_fk="outcome_id",
                child_lookups=["outcome"],
            ),
        ],
    ),
    DataMapping(
        table="RiskRegister",
        model=ents.RiskRegister,
        column_mapping={
            "Submission ID": "submission_id",
            "Project ID": "project_id",
            "Programme ID": "programme_id",
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
        cols_to_jsonb=[
            "risk_name",
            "risk_category",
            "short_desc",
            "full_desc",
            "consequences",
            "pre_mitigated_impact",
            "pre_mitigated_likelihood",
            "mitigations",
            "post_mitigated_impact",
            "post_mitigated_likelihood",
            "proximity",
            "risk_owner_role",
        ],
        fk_relations=[
            FKMapping(
                parent_lookups=["project_id"],
                parent_model=ents.Project,
                child_fk="project_id",
                child_lookups=["project_id"],
            ),
            FKMapping(
                parent_lookups=["programme_id", "submission_id"],
                parent_model=ents.ProgrammeJunction,
                child_fk="programme_junction_id",
                child_lookups=["programme_id", "submission_id"],
            ),
        ],
    ),
    DataMapping(
        table="ProjectFinanceChange",
        model=ents.ProjectFinanceChange,
        column_mapping={
            "Submission ID": "submission_id",
            "Programme ID": "programme_id",
            "Change Number": "change_number",
            "Project Funding Moved From": "project_funding_moved_from",
            "Intervention Theme Moved From": "intervention_theme_moved_from",
            "Project Funding Moved To": "project_funding_moved_to",
            "Intervention Theme Moved To": "intervention_theme_moved_to",
            "Amount Moved": "amount_moved",
            "Change Made": "changes_made",
            "Reason for Change": "reasons_for_change",
            "Actual or Forecast": "state",
            "Reporting Period Change Takes Place": "reporting_period_change_takes_place",
        },
        cols_to_jsonb=[
            "change_number",
            "project_funding_moved_from",
            "intervention_theme_moved_from",
            "project_funding_moved_to",
            "intervention_theme_moved_to",
            "amount_moved",
            "changes_made",
            "reasons_for_change",
            "state",
            "reporting_period_change_takes_place",
        ],
        fk_relations=[
            FKMapping(
                parent_lookups=["programme_id", "submission_id"],
                parent_model=ents.ProgrammeJunction,
                child_fk="programme_junction_id",
                child_lookups=["programme_id", "submission_id"],
            ),
        ],
    ),
    DataMapping(
        table="Programme Management",
        model=ents.ProgrammeFundingManagement,
        column_mapping={
            "Submission ID": "submission_id",
            "Programme ID": "programme_id",
            "Payment Type": "payment_type",
            "Spend for Reporting Period": "spend_for_reporting_period",
            "Start_Date": "start_date",
            "End_Date": "end_date",
            "Actual/Forecast": "state",
        },
        cols_to_jsonb=[
            "payment_type",
            "spend_for_reporting_period",
            "state",
        ],
        fk_relations=[
            FKMapping(
                parent_lookups=["programme_id", "submission_id"],
                parent_model=ents.ProgrammeJunction,
                child_fk="programme_junction_id",
                child_lookups=["programme_id", "submission_id"],
            ),
        ],
    ),
)
