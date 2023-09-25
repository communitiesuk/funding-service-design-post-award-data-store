from dataclasses import dataclass

import numpy as np
import pandas as pd

from core.const import (
    PRE_DEFINED_FUNDING_SOURCES,
    FundingSourceCategoryEnum,
    MultiplicityEnum,
    StatusEnum,
    YesNoEnum,
)
from core.util import get_project_number
from core.validation.failures import ValidationFailure


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
        # validate_sign_off,  # TODO: This needs to be fixed.
        validate_psi_funding_gap,
        validate_locations,
        validate_leading_factor_of_delay,
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

    # filter to projects with risks
    projects_with_risks = workbook["RiskRegister"]["Project ID"].dropna()  # drop programme risks
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
        project_numbers = [get_project_number(project_id) for project_id in projects_missing_risks]
        return [
            TownsFundRoundFourValidationFailure(
                tab="Risk Register",
                section=f"Project Risks - Project {project}",
                message="You have not entered any risks for this project. You must enter at least 1 risk per "
                "non-complete project",
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
                tab="Risk Register",
                section="Programme Risks",
                message="You have not entered enough programme level risks. "
                "You must enter at least 1 programme level risk",
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
    if len(invalid_rows) > 0:
        return [
            TownsFundRoundFourValidationFailure(
                tab="Funding Profiles",
                section=f"Project Funding Profiles - Project {get_project_number(row['Project ID'])}",
                message=f'For column "Funding Source", you have entered "{row["Funding Source Type"]}" which isn\'t '
                f"correct. You must select an option from the list provided",
            )
            for _, row in invalid_rows.iterrows()
        ]


def validate_sign_off(workbook: dict[str, pd.DataFrame]) -> list["TownsFundRoundFourValidationFailure"] | None:
    """Validates Name, Role, and Date for the Review & Sign-Off Section

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    sheet = workbook.get("8 - Review & Sign-Off")
    sheet.replace(r"", np.nan, inplace=True)

    section_151_text_cells = [6, 7, 9]
    town_board_chair_cells = [13, 14, 16]

    failures = []

    for y_axis in section_151_text_cells:
        if pd.isnull(sheet.iloc[y_axis, 2]):
            failures.append(
                TownsFundRoundFourValidationFailure(
                    tab="Review & Sign-Off",
                    section="Section 151 Officer / Chief Finance Officer",
                    message=(
                        f"You must fill out the {str(sheet.iloc[y_axis, 1])} for this section. "
                        "You need to get sign off from an S151 Officer or Chief Finance Officer"
                    ),
                )
            )

    for y_axis in town_board_chair_cells:
        if pd.isnull(sheet.iloc[y_axis, 2]):
            failures.append(
                TownsFundRoundFourValidationFailure(
                    tab="Review & Sign-Off",
                    section="Town Board Chair",
                    message=(
                        f"You must fill out the {str(sheet.iloc[y_axis, 1])} for this section. "
                        "You need to get sign off from a programme SRO"
                    ),
                )
            )

    if failures:
        return failures


def validate_locations(workbook: dict[str, pd.DataFrame]) -> list["TownsFundRoundFourValidationFailure"]:
    """Validates the location columns on the Project Admin tab.

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

    # tuples of (column_data, column_name) to validate empty cells on
    empty_cell_validation = (
        (single_rows["Locations"], "Single location | Project Location - Post Code (e.g. SW1P 4DF)"),
        (
            single_rows["Lat/Long"],
            "Single location | Project Location - Lat/Long Coordinates (3.d.p e.g. 51.496, -0.129)",
        ),
        (multiple_rows["Locations"], "Multiple locations | Project Locations - Post Code (e.g. SW1P 4DF)"),
        (
            multiple_rows["Lat/Long"],
            "Multiple locations | Project Locations - Lat/Long Coordinates (3.d.p e.g. 51.496, -0.129)",
        ),
        (
            multiple_rows["GIS Provided"],
            "Multiple locations | Are you providing a GIS map (see guidance) with your return?",
        ),
    )

    failures = []

    # empty cell validation
    for column_data, column_name in empty_cell_validation:
        if pd.isna(column_data).any() | (column_data.astype("string") == "").any():
            failures.append(
                TownsFundRoundFourValidationFailure(
                    tab="Project Admin",
                    section="Project Details",
                    message=f"There are blank cells in column: {column_name}. "
                    "Use the space provided to tell us the relevant information",
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
                    tab="Project Admin",
                    section="Project Details",
                    message='For column "Multiple locations | Are you providing a GIS map (see guidance) with your '
                    f'return?", you have entered "{invalid_value}" which isn\'t correct. '
                    "You must select an option from the list provided",
                )
            )

    return failures


def validate_psi_funding_gap(workbook: dict[str, pd.DataFrame]) -> list["TownsFundRoundFourValidationFailure"] | None:
    """Validates that if a funding gap of > 0 is specified in the PSI (Private Sector Investment) tab that an
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
        return [
            TownsFundRoundFourValidationFailure(
                tab="PSI",
                section="Private Sector Investment",
                message=(
                    'You have entered data with a greater than zero "Private Sector Investment Gap" without providing '
                    "an additional comment. Use the space provided to tell us why"
                ),
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
    if any(delayed_rows["Leading Factor of Delay"].isin(na_values)):
        return [
            TownsFundRoundFourValidationFailure(
                tab="Programme Progress",
                section="Projects Progress Summary",
                message=(
                    'Projects with Project Delivery Status as "1. Not yet started" or "3. Ongoing - delayed" must not '
                    "contain blank cells for the column: Leading Factor of Delay. "
                    "Use the space provided to tell us the relevant information"
                ),
            )
        ]


@dataclass
class TownsFundRoundFourValidationFailure(ValidationFailure):
    """Generic Towns Fund Round 4 Validation Failure."""

    tab: str
    section: str
    message: str

    def __str__(self):
        pass

    def to_message(self) -> tuple[str | None, str | None, str]:
        return self.tab, self.section, self.message
