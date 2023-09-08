from dataclasses import dataclass

import pandas as pd
from openpyxl import load_workbook
from openpyxl_image_loader import SheetImageLoader
from werkzeug.datastructures import FileStorage

from core.validation.failures import ValidationFailure


def validate(workbook: dict[str, pd.DataFrame], excel_file: FileStorage) -> list["TownsFundRoundFourValidationFailure"]:
    """Top-level Towns Fund Round 4 specific validation.

    Validates against context specific rules that sit outside the general validation flow.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames.
    :excel_file: the Excel file before it is converted into pandas DataFrames.
    :return: A list of ValidationFailure objects representing any validation errors
             found.
    """
    validations = (validate_project_risks, validate_programme_risks, validate_project_admin_gis_provided)

    validation_failures = []
    for validation_func in validations:
        failures = validation_func(workbook)
        if failures:
            validation_failures.extend(failures)

    if failures := validate_sign_off(excel_file):
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


def validate_sign_off(excel_file: FileStorage) -> list["TownsFundRoundFourValidationFailure"] | None:
    """Validate the "Review & Sign-Off" sheet in the given Excel file.

    This function checks for the presence of required signatures and text fields
    and generates validation failures if any are missing.

    :param excel_file: The Excel file before it is converted into pandas DataFrames.
    :return: A list of TownsFundRoundFourValidationFailure objects representing any
             validation errors found.
    """
    wb = load_workbook(excel_file)
    sheet = wb["8 - Review & Sign-Off"]

    fields_and_sections = []

    image_loader = SheetImageLoader(sheet)
    if not image_loader.image_in("C10"):
        fields_and_sections.append(("Signature", "Section 151 Officer / Chief Finance Officer"))
    if not image_loader.image_in("C17"):
        fields_and_sections.append(("Signature", "Town Board Chair"))

    section_151_text_cells = [("B8", "C8"), ("B9", "C9"), ("B11", "C11")]
    town_board_chair_cells = [("B15", "C15"), ("B15", "C16"), ("B18", "C18")]

    for field, value in section_151_text_cells:
        if not sheet[value].value:
            fields_and_sections.append((sheet[field].value, "Section 151 Officer / Chief Finance Officer"))

    for field, value in town_board_chair_cells:
        if not sheet[value].value:
            fields_and_sections.append((sheet[field].value, "Town Board Chair"))

    section_to_approver = {
        "Section 151 Officer / Chief Finance Officer": "an S151 Officer or Chief Finance Officer",
        "Town Board Chair": "a programme SRO",
    }

    if len(fields_and_sections) > 0:
        return [
            TownsFundRoundFourValidationFailure(
                tab="Review & Sign-Off",
                section=section,
                message=(
                    f"You must fill out the {field} for this section. "
                    f"You need to get sign off from {str(section_to_approver[section])}"
                ),
            )
            for field, section in fields_and_sections
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
