from dataclasses import dataclass

import numpy as np
import pandas as pd

import core.validation.messages as msgs
from config.envs.default import DefaultConfig
from core.aws import get_file
from core.const import (
    INTERNAL_TABLE_TO_FORM_TAB,
    PRE_DEFINED_FUNDING_SOURCES,
    TF_FUNDING_ALLOCATED_FILE,
    FundingSourceCategoryEnum,
    MultiplicityEnum,
    StatusEnum,
    YesNoEnum,
)
from core.util import get_project_number_by_id, get_project_number_by_position
from core.validation.failures import ValidationFailure, construct_cell_index


def validate(workbook: dict[str, pd.DataFrame]) -> list["TownsFundRoundFourValidationFailure"]:
    """Top-level Towns Fund Round 4 specific validation.

    Validates against context specific rules that sit outside the general validation flow.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames.
    :return: A list of ValidationFailure objects representing any validation errors
             found.
    """
    validations = (
        validate_project_risks,
        validate_programme_risks,
        validate_funding_profiles_funding_source,
        validate_psi_funding_gap,
        validate_locations,
        validate_leading_factor_of_delay,
        validate_funding_spent,
    )

    validation_failures = []
    for validation_func in validations:
        failures = validation_func(workbook)
        if failures:
            validation_failures.extend(failures)

    return validation_failures


def validate_project_risks(workbook: dict[str, pd.DataFrame]) -> list["TownsFundRoundFourValidationFailure"] | None:
    """Validates that each non-completed project has at least one Risk row associated with it.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    project_details_df = workbook["Project Details"]
    active_project_ids = project_details_df["Project ID"].to_list()

    # filter to projects with risks
    risk_df = workbook["RiskRegister"]
    projects_with_risks = risk_df["Project ID"].dropna()  # drop programme risks
    project_with_risks_mask = project_details_df["Project ID"].isin(projects_with_risks)

    # filter to completed projects
    project_progress_df = workbook["Project Progress"]
    completed_projects = project_progress_df[project_progress_df["Project Delivery Status"] == StatusEnum.COMPLETED][
        "Project ID"
    ]
    completed_projects_mask = project_details_df["Project ID"].isin(completed_projects)

    # projects that have no risks and are not completed
    projects_missing_risks = project_details_df[~project_with_risks_mask & ~completed_projects_mask]["Project ID"]

    if len(projects_missing_risks) > 0:
        projects_missing_risks = list(projects_missing_risks)
        projects_missing_risks.sort()
        project_numbers = [
            get_project_number_by_id(project_id, active_project_ids) for project_id in projects_missing_risks
        ]
        return [
            TownsFundRoundFourValidationFailure(
                sheet="RiskRegister",
                section=f"Project Risks - Project {project}",
                column="RiskName",
                message=msgs.PROJECT_RISKS,
                row_indexes=[13 + project * 8] if project <= 3 else [14 + project * 8],
                # hacky fix to inconsistent spreadsheet format (extra row at line 42)
                # cell location points to first cell in project risk section
            )
            for project in project_numbers
        ]


def validate_programme_risks(workbook: dict[str, pd.DataFrame]) -> list["TownsFundRoundFourValidationFailure"] | None:
    """Validates that each submission has at least 3 Programme level Risks.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    risk_programme_ids = workbook["RiskRegister"]["Programme ID"].dropna()  # drop project risk rows

    if len(risk_programme_ids) < 1:
        return [
            TownsFundRoundFourValidationFailure(
                sheet="RiskRegister",
                section="Programme Risks",
                column="RiskName",
                message=msgs.PROGRAMME_RISKS,
                row_indexes=[10],
                # cell location points to first cell in programme risk section
            )
        ]


def validate_funding_profiles_funding_source(
    workbook: dict[str, pd.DataFrame]
) -> list["TownsFundRoundFourValidationFailure"] | None:
    """Validates that funding source data from "Other Funding Sources" is from an allowed set of values.

    This cannot be done as part of the schema validation flow because data from the pre-defined funding source section
    above "Other Funding Sources" is also ingested as part of the Funding Profiles table and contains data with a
    "Funding Source" ("Towns Fund") outside the allowed values for "Other Funding Sources".

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    funding_df = workbook["Funding"]

    # filters out pre-defined funding sources
    non_pre_defined_source_mask = ~funding_df["Funding Source Name"].isin(PRE_DEFINED_FUNDING_SOURCES)
    # filters out valid Funding Sources
    invalid_source_mask = ~funding_df["Funding Source Type"].isin(set(FundingSourceCategoryEnum))

    invalid_rows = funding_df[non_pre_defined_source_mask & invalid_source_mask]

    # due to the pd.melt during transformation that maps a single spreadsheet row to multiple df rows, here we just keep
    # the first of each unique index (this refers to the spreadsheet row number). This ensures we only produce one error
    # for a single incorrect row in the spreadsheet
    invalid_rows = invalid_rows[~invalid_rows.index.duplicated(keep="first")]
    if len(invalid_rows) > 0:
        return [
            TownsFundRoundFourValidationFailure(
                sheet="Funding",
                section=f"Project Funding Profiles - Project {get_project_number_by_position(row.name, 'Funding')}",
                column="Funding Source Type",
                message=msgs.DROPDOWN,
                row_indexes=[row.name],
            )
            for _, row in invalid_rows.iterrows()
        ]


def validate_locations(workbook: dict[str, pd.DataFrame]) -> list["TownsFundRoundFourValidationFailure"]:
    """Validates the location columns on the Project Admin sheet.

    This carries out:
     - empty cell validation on the Post Code, Lat/Long and GIS Provided columns
     - enum validation on GIS Provided

    This is done separately from the schema validation so that we can skip validation on these columns for rows where
    the user has not selected a Single or Multiple location correctly.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    project_details_df = workbook["Project Details"]

    # don't validate any rows that are not Single or Multiple - these will already be caught during schema validation
    single_rows = project_details_df[project_details_df["Single or Multiple Locations"] == MultiplicityEnum.SINGLE]
    multiple_rows = project_details_df[project_details_df["Single or Multiple Locations"] == MultiplicityEnum.MULTIPLE]

    # tuples of (table_column,  form_column, column_data) to validate empty cells on
    empty_cell_validation = (
        (
            "Locations",
            "Single location | Project Location - Post Code (e.g. SW1P 4DF)",
            single_rows["Locations"],
        ),
        (
            "Lat/Long",
            "Single location | Project Location - Lat/Long Coordinates (3.d.p e.g. 51.496, -0.129)",
            single_rows["Lat/Long"],
        ),
        ("Locations", "Multiple locations | Project Locations - Post Code (e.g. SW1P 4DF)", multiple_rows["Locations"]),
        (
            "Lat/Long",
            "Multiple locations | Project Locations - Lat/Long Coordinates (3.d.p e.g. 51.496, -0.129)",
            multiple_rows["Lat/Long"],
        ),
        (
            "GIS Provided",
            "Multiple locations | Are you providing a GIS map (see guidance) with your return?",
            multiple_rows["GIS Provided"],
        ),
    )

    failures = []

    # empty cell validation
    for table_column, form_column, column_data in empty_cell_validation:
        if failed_indexes := column_data.index[pd.isna(column_data) | (column_data.astype("string") == "")].tolist():
            failures.append(
                TownsFundRoundFourValidationFailure(
                    sheet="Project Details",
                    section="Project Details",
                    column=table_column,
                    message=msgs.BLANK,
                    row_indexes=failed_indexes,
                )
            )

    # enum validation
    valid_enum_values = set(YesNoEnum)
    valid_enum_values.add("")  # allow empty string here to avoid duplicate errors for empty cells
    row_is_valid = multiple_rows["GIS Provided"].isin(valid_enum_values)
    invalid_rows = multiple_rows[~row_is_valid]  # noqa: E712 pandas notation
    for _, row in invalid_rows.iterrows():
        invalid_value = row["GIS Provided"]
        if not pd.isna(invalid_value):
            failures.append(
                TownsFundRoundFourValidationFailure(
                    sheet="Project Details",
                    section="Project Details",
                    column="GIS Provided",
                    message=msgs.DROPDOWN,
                    row_indexes=[row.name],
                )
            )

    return failures


def validate_psi_funding_gap(workbook: dict[str, pd.DataFrame]) -> list["TownsFundRoundFourValidationFailure"] | None:
    """Validates that if a funding gap of > 0 is specified in the PSI (Private Sector Investment) sheet that an
    additional comment is supplied to explain why

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    psi_df = workbook["Private Investments"]
    invalid_mask = (psi_df["Private Sector Funding Required"] > psi_df["Private Sector Funding Secured"]) & (
        psi_df["Additional Comments"].isna()
    )

    invalid_psi_rows = psi_df.loc[invalid_mask]
    if len(invalid_psi_rows) > 0:
        invalid_indexes = invalid_psi_rows.index.tolist()
        return [
            TownsFundRoundFourValidationFailure(
                sheet="Private Investments",
                section="Private Sector Investment",
                column="Additional Comments",
                message=msgs.BLANK_PSI,
                row_indexes=invalid_indexes,
            )
        ]


def validate_leading_factor_of_delay(
    workbook: dict[str, pd.DataFrame]
) -> list["TownsFundRoundFourValidationFailure"] | None:
    """Validates that Leading Factor of Delay is present for delayed projects.

    This means rows where Project Delivery Status is "1. Not yet started" or "3. Ongoing - delayed", there must be a
    valid value for Leading Factor of Delay.

    If Leading Factor of Delay is present but not required due to the above constraint, then do not fail.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    project_progress_df = workbook["Project Progress"]
    delayed_mask = project_progress_df["Project Delivery Status"].isin(
        {StatusEnum.NOT_YET_STARTED, StatusEnum.ONGOING_DELAYED}
    )

    na_values = {"", "< Select >", np.nan, None}
    delayed_rows = project_progress_df[delayed_mask]
    invalid_indexes = delayed_rows.index[delayed_rows["Leading Factor of Delay"].isin(na_values)].tolist()
    if invalid_indexes:
        return [
            TownsFundRoundFourValidationFailure(
                sheet="Project Progress",
                section="Projects Progress Summary",
                column="Leading Factor of Delay",
                message=msgs.BLANK,
                row_indexes=invalid_indexes,
            )
        ]


def validate_funding_spent(workbook: dict[str, pd.DataFrame]) -> list["TownsFundRoundFourValidationFailure"] | None:
    """Validates that total reported funding spent on the sheet is less than the amount specified as allocated in a
    separate sheet stored on S3.

    For Town deal funds this is done on a per-project basis whereas for future High Street Funds this is done
    per-programme leading to slightly different logics for both.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    # pull programme and project indexes from the workbook
    programme_id = workbook["Programme_Ref"].iloc[0]["Programme ID"]
    fund_type = workbook["Programme_Ref"].iloc[0]["FundType_ID"]
    project_ids = workbook["Project Details"]["Project ID"].tolist()
    funding_df = workbook["Funding"]

    # pull funding spent for individual projects and programme wide total
    funding_spent = {project: spend_per_project(funding_df, project) for project in project_ids}
    funding_spent[programme_id] = sum(funding_spent.values())

    funding_allocated = get_allocated_funding()

    funding_spent_failures = []
    if fund_type == "HS":
        # check funding against programme wide funding allocated for Future High Street Fund submissions
        validate_by = "programme"
        ids_to_check = [programme_id]

    else:
        # check funding against individual project funding allocated for Towns Deal submissions
        validate_by = "project"
        ids_to_check = project_ids

    for idx in ids_to_check:
        if funding_spent[idx] > funding_allocated[idx]:
            funding_spent_failures.append(
                TownsFundRoundFourValidationFailure(
                    sheet="Funding",
                    section="Project Funding Profiles"
                    + (f" - Project {get_project_number_by_id(idx, project_ids)}" if validate_by == "project" else ""),
                    column="Grand Total",
                    message=msgs.OVERSPEND,
                    row_indexes=[15 + 28 * get_project_number_by_id(idx, project_ids)]
                    if validate_by == "project"
                    else [15 + 28 * get_project_number_by_id(proj_id, project_ids) for proj_id in project_ids],
                )
            )

    return funding_spent_failures


def spend_per_project(funding_df: pd.DataFrame, project_id: str) -> float:
    """return the total funding spent per an individual project

    :param funding_df: A dataframe of the funding table from a submission
    :param: project_id: ID of project in question

    :return: Total funding spent per project
    """
    funding_spent = (
        funding_df["Spend for Reporting Period"]
        .loc[
            (funding_df["Project ID"] == project_id)
            & (funding_df["Funding Source Type"] == "Towns Fund")
            & ~(funding_df["Funding Source Name"].str.contains(r"contractually committed"))
        ]
        .sum()
    )
    # Business logic here is taken from spreadsheet 4a - Funding Profile Z45 for grand total expenditure
    return funding_spent


def get_allocated_funding():
    return pd.read_csv(
        get_file(DefaultConfig.AWS_S3_BUCKET_FILE_ASSETS, TF_FUNDING_ALLOCATED_FILE), index_col="Index Code"
    )["Grant Awarded"]


@dataclass
class TownsFundRoundFourValidationFailure(ValidationFailure):
    """Generic Towns Fund Round 4 Validation Failure."""

    sheet: str
    section: str
    column: str
    message: str
    row_indexes: list[int]

    def __str__(self):
        pass

    def to_message(self) -> tuple[str | None, str | None, str | None, str]:
        cell_index = construct_cell_index(self.sheet, self.column, self.row_indexes)
        sheet = INTERNAL_TABLE_TO_FORM_TAB[self.sheet]
        return sheet, self.section, cell_index, self.message
