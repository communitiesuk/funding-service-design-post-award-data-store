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
    for validation_funct in validations:
        validation_failures.extend(validation_funct(workbook))

    return validation_failures


def validate_project_risks(workbook: dict[str, pd.DataFrame]) -> list["TownsFundRoundFourValidationFailure"]:
    # TODO: validate there is a risk for each project.
    return []


def validate_programme_risks(workbook: dict[str, pd.DataFrame]) -> list["TownsFundRoundFourValidationFailure"]:
    # TODO: validate there is a risk for each project.
    return []


class TownsFundRoundFourValidationFailure(ValidationFailure):
    """Generic Towns Fund Round 4 Validation Failure."""

    tab: str
    section: str
    message: str

    def __str__(self):
        pass

    def to_message(self) -> tuple[str | None, str | None, str]:
        return self.tab, self.section, self.message
