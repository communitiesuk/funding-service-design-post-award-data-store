from dataclasses import dataclass

import pandas as pd

from core.const import PRE_DEFINED_FUNDING_SOURCES, FundingSourceCategoryEnum
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
        validate_project_admin_gis_provided,
        validate_funding_profiles_funding_source,
    )

    validation_failures = []
    for validation_func in validations:
        failures = validation_func(workbook)
        if failures:
            validation_failures.extend(failures)

    return validation_failures


def validate_project_risks(workbook: dict[str, pd.DataFrame]) -> list["TownsFundRoundFourValidationFailure"] | None:
    """Validates that each project has at least one Risk row associated with it.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    all_project_ids = workbook["Project Details"]["Project ID"]
    risk_project_ids = workbook["RiskRegister"]["Project ID"]
    projects_missing_risks = list(set(all_project_ids).difference(risk_project_ids))

    if projects_missing_risks:
        projects_missing_risks.sort()
        project_numbers = [get_project_number(project_id) for project_id in projects_missing_risks]
        return [
            TownsFundRoundFourValidationFailure(
                tab="Risk Register",
                section=f"Project Risks - Project {project}",
                message="You have not entered any risks for this project. You must enter at least 1 risk per project",
            )
            for project in project_numbers
        ]


def validate_programme_risks(workbook: dict[str, pd.DataFrame]) -> list["TownsFundRoundFourValidationFailure"] | None:
    """Validates that each submission has at least 3 Programme level Risks.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    risk_programme_ids = workbook["RiskRegister"]["Programme ID"].dropna()

    if len(risk_programme_ids) < 1:
        return [
            TownsFundRoundFourValidationFailure(
                tab="Risk Register",
                section="Programme Risks",
                message="You have not entered enough programme level risks. "
                "You must enter at least 1 programme level risks",
            )
        ]


def validate_project_admin_gis_provided(
    workbook: dict[str, pd.DataFrame]
) -> list["TownsFundRoundFourValidationFailure"] | None:
    """Validates that each project stating multiple locations contains a value for "GIS provided".

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    project_details_df = workbook["Project Details"]
    condition_broken = any(
        project_details_df["GIS Provided"][project_details_df["Single or Multiple Locations"] == "Multiple"].isna()
    )

    if condition_broken:
        return [
            TownsFundRoundFourValidationFailure(
                tab="Project Admin",
                section="Project Details",
                message='There are blank cells in column: "Are you providing a GIS map (see guidance) with your '
                'return?". Use the space provided to tell us the relevant information',
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
