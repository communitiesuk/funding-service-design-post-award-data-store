from dataclasses import dataclass

import pandas as pd

from core.validation.failures import ValidationFailure


def validate(workbook: dict[str, pd.DataFrame]) -> list["TownsFundRoundFourValidationFailure"]:
    """Top-level Towns Fund Round 4 specific validation.

    Validates against context specific rules that sit outside the general validation flow.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames.
    :return: A list of ValidationFailure objects representing any validation errors
             found.
    """
    validations = (validate_project_risks, validate_programme_risks)

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
        project_numbers = [int(project_id.split("-")[2]) for project_id in projects_missing_risks]
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
    risk_programme_ids = list(workbook["RiskRegister"]["Programme ID"].dropna())

    # TODO: Confirm if 1 or 3 programme risks are required and change this function accordingly
    if len(risk_programme_ids) < 3:
        return [
            TownsFundRoundFourValidationFailure(
                tab="Risk Register",
                section="Programme Risks",
                message="You have not entered enough programme level risks. You must enter 3 programme level risks",
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
