"""Module for functions relating to data validation specific to Town's Fund Round 4."""

import re
from pathlib import Path

import numpy as np
import pandas as pd

from core.const import (
    FundingSourceCategoryEnum,
    FundingUses,
    MultiplicityEnum,
    StatusEnum,
    YesNoEnum,
)
from core.messaging.tf_messaging import TFMessages as msgs
from core.transformation.utils import POSTCODE_REGEX
from core.util import get_project_number_by_id, get_project_number_by_position
from core.validation.failures.user import GenericFailure
from core.validation.utils import (
    find_null_values,
    is_blank,
    is_from_dropdown,
    is_numeric,
    remove_duplicate_indexes,
)

PRE_DEFINED_FUNDING_SOURCES = [
    "Commercial Income",
    "How much of your CDEL forecast is contractually committed?",
    "How much of your RDEL forecast is contractually committed?",
    "Town Deals 5% CDEL Pre-Payment",
    "Towns Fund CDEL which is being utilised on TF project related activity (For Town Deals, this excludes the 5% CDEL "
    "Pre-Payment)",
    "Towns Fund RDEL Payment which is being utilised on TF project related activity",
]


FUNDING_ALLOCATION = pd.read_csv(Path(__file__).parent / "resources" / "TF-grant-awarded.csv", index_col="Index Code")


def validate(
    data_dict: dict[str, pd.DataFrame], original_workbook: dict[str, pd.DataFrame] | None = None
) -> list[GenericFailure]:
    """Top-level Towns Fund Round 4 specific validation.

    Validates against context specific rules that sit outside the general validation flow.

    :param data_dict: A dictionary where keys are table names and values are pandas
                     DataFrames of extracted and transformed data.
    :param original_workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames of the original source Excel sheets.
    :return: A list of ValidationFailure objects representing any validation errors
             found.
    """
    validations = (
        validate_project_risks,
        validate_programme_risks,
        validate_funding_profiles_funding_source_enum,
        validate_funding_profiles_at_least_one_other_funding_source_fhsf,
        validate_psi_funding_gap,
        validate_locations,
        validate_funding_spent,
        validate_funding_profiles_funding_secured_not_null,
        validate_psi_funding_not_negative,
        validate_postcodes,
        validate_project_progress,
        validate_funding_questions,
    )

    validation_failures = []
    for validation_func in validations:
        failures = validation_func(data_dict)
        if failures:
            validation_failures.extend(failures)

    sign_off_failures = validate_sign_off(original_workbook)
    validation_failures = [*validation_failures, *sign_off_failures]

    return validation_failures


def validate_project_risks(workbook: dict[str, pd.DataFrame]) -> list["GenericFailure"] | None:
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
            GenericFailure(
                table="RiskRegister",
                section=f"Project Risks - Project {project}",
                column="RiskName",
                message=msgs.PROJECT_RISKS,
                row_index=13 + project * 8 if project <= 3 else 14 + project * 8,
                # hacky fix to inconsistent spreadsheet format (extra row at line 42)
                # cell location points to first cell in project risk section
            )
            for project in project_numbers
        ]


def validate_programme_risks(workbook: dict[str, pd.DataFrame]) -> list["GenericFailure"] | None:
    """Validates that each submission has at least 3 Programme level Risks.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    risk_programme_ids = workbook["RiskRegister"]["Programme ID"].dropna()  # drop project risk rows

    if len(risk_programme_ids) < 1:
        return [
            GenericFailure(
                table="RiskRegister",
                section="Programme Risks",
                column="RiskName",
                message=msgs.PROGRAMME_RISKS,
                row_index=10,
                # cell location points to first cell in programme risk section
            )
        ]


def validate_funding_profiles_funding_source_enum(workbook: dict[str, pd.DataFrame]) -> list["GenericFailure"] | None:
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
    other_funding_sources_mask = ~funding_df["Funding Source Name"].isin(PRE_DEFINED_FUNDING_SOURCES)
    # filters out valid Funding Sources
    invalid_source_mask = ~funding_df["Funding Source Type"].isin(set(FundingSourceCategoryEnum))

    invalid_rows = funding_df[other_funding_sources_mask & invalid_source_mask]

    # handle melted rows
    invalid_rows = remove_duplicate_indexes(invalid_rows)

    if len(invalid_rows) > 0:
        return [
            GenericFailure(
                table="Funding",
                section=f"Project Funding Profiles - Project {get_project_number_by_position(row.name, 'Funding')}",
                column="Funding Source Type",
                message=msgs.DROPDOWN,
                row_index=row.name,
            )
            for _, row in invalid_rows.iterrows()
        ]


def validate_funding_profiles_at_least_one_other_funding_source_fhsf(
    workbook: dict[str, pd.DataFrame]
) -> list["GenericFailure"] | None:
    """Validates that there is at least one Other Funding Source entry across any projects for a FHSF submission.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    if workbook["Programme_Ref"].iloc[0]["FundType_ID"] != "HS":
        return  # skip validation if not FHSF

    funding_df = workbook["Funding"]

    # filters out pre-defined funding sources
    other_funding_sources_mask = ~funding_df["Funding Source Name"].isin(PRE_DEFINED_FUNDING_SOURCES)

    other_funding_sources = funding_df[other_funding_sources_mask]

    # handle melted rows
    other_funding_sources = remove_duplicate_indexes(other_funding_sources)

    if len(other_funding_sources) == 0:
        return [
            GenericFailure(
                table="Funding",
                section="Project Funding Profiles",
                column="Funding Source Type",
                message=msgs.MISSING_OTHER_FUNDING_SOURCES,
                row_index=None,
            )
        ]


def validate_funding_profiles_funding_secured_not_null(
    workbook: dict[str, pd.DataFrame]
) -> list["GenericFailure"] | None:
    """Validates that Secured is not null for custom funding sources.

    This function checks the 'Funding' sheet for rows with custom funding sources where 'Secured' is not null.
    If invalid rows are found, it returns a list of validation failures.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    funding_df = workbook["Funding"]

    # filters out pre-defined funding sources
    other_funding_sources_mask = ~funding_df["Funding Source Name"].isin(PRE_DEFINED_FUNDING_SOURCES)
    # filters out Secured if not null
    invalid_source_mask = funding_df["Secured"].isna()

    invalid_rows = funding_df[other_funding_sources_mask & invalid_source_mask]
    invalid_rows = remove_duplicate_indexes(invalid_rows)

    if len(invalid_rows) > 0:
        return [
            GenericFailure(
                table="Funding",
                section=f"Project Funding Profiles - Project {get_project_number_by_position(row.name, 'Funding')}",
                column="Secured",
                message=msgs.BLANK,
                row_index=row.name,
            )
            for _, row in invalid_rows.iterrows()
        ]


def validate_locations(workbook: dict[str, pd.DataFrame]) -> list["GenericFailure"]:
    """Validates the location columns on the Project Admin sheet.

    This carries out:
     - empty cell validation on the Post Code and GIS Provided columns
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
        ("Locations", "Multiple locations | Project Locations - Post Code (e.g. SW1P 4DF)", multiple_rows["Locations"]),
        (
            "GIS Provided",
            "Multiple locations | Are you providing a GIS map (see guidance) with your return?",
            multiple_rows["GIS Provided"],
        ),
    )

    failures = []

    # empty cell validation
    for table_column, form_column, column_data in empty_cell_validation:
        for idx, value in column_data.items():
            if is_blank(value):
                failures.append(
                    GenericFailure(
                        table="Project Details",
                        section="Project Details",
                        column=table_column,
                        message=msgs.BLANK,
                        row_index=idx,
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
                GenericFailure(
                    table="Project Details",
                    section="Project Details",
                    column="GIS Provided",
                    message=msgs.DROPDOWN,
                    row_index=row.name,
                )
            )

    return failures


def validate_psi_funding_gap(workbook: dict[str, pd.DataFrame]) -> list["GenericFailure"] | None:
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
        return [
            GenericFailure(
                table="Private Investments",
                section="Private Sector Investment",
                column="Additional Comments",
                message=msgs.BLANK_PSI,
                row_index=idx,
            )
            for idx, _ in invalid_psi_rows.iterrows()
        ]


def validate_funding_spent(workbook: dict[str, pd.DataFrame]) -> list["GenericFailure"] | None:
    """Validates that total reported funding spent on the sheet is less than the amount specified as allocated in a
    separate sheet stored in this repo (data-store).

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

    try:
        funding_spent = [spend_per_project(funding_df, project) for project in project_ids]
    except TypeError:
        # data contains non-numeric values so cannot validate funding
        return

    # pull funding spent for individual projects into a DataFrame
    funding_spent = pd.DataFrame(funding_spent).set_index("index")

    # TODO: create a single Failure instance for a single overspend error with a set of "locations" rather
    #   than a Failure for each cell
    if fund_type == "HS":
        # check funding against programme wide funding allocated for Future High Street Fund submissions
        if round(funding_spent["Total"].sum()) > get_allocated_funding(programme_id, "Total"):
            return [
                # one failure per cell to return to the user
                GenericFailure(
                    table="Funding",
                    section="Project Funding Profiles",
                    column="Grand Total",
                    message=msgs.OVERSPEND_PROGRAMME,
                    # first project begins after 17 and each project is seperated by 28 cells
                    row_index=row_index,
                )
                for row_index in [17 + 28 * get_project_number_by_id(proj_id, project_ids) for proj_id in project_ids]
            ]
    else:
        # check funding against individual project funding allocated for Towns Deal submissions
        funding_spent_failures = []
        for expense_type in ["CDEL", "RDEL"]:
            for project_id in project_ids:
                project_number = get_project_number_by_id(project_id, project_ids)
                if round(funding_spent[expense_type][project_id]) > get_allocated_funding(project_id, expense_type):
                    funding_spent_failures.append(
                        GenericFailure(
                            table="Funding",
                            section=f"Project Funding Profiles - Project {project_number}",
                            column="Grand Total",
                            message=msgs.OVERSPEND.format(expense_type=expense_type),
                            row_index=13 + 28 * project_number if expense_type == "CDEL" else 16 + 28 * project_number,
                        )
                    )
        return funding_spent_failures


def spend_per_project(funding_df: pd.DataFrame, project_id: str) -> dict[str:int]:
    """return the total funding spent per an individual project

    :param funding_df: A dataframe of the funding table from a submission
    :param: project_id: ID of project in question

    :return: Total funding spent per project
    """
    funding_df = funding_df.loc[
        (funding_df["Project ID"] == project_id)
        & (funding_df["Funding Source Type"] == "Towns Fund")
        & ~(funding_df["Funding Source Name"].str.contains("contractually committed"))
    ]

    funding_spent = {
        "index": project_id,
        "CDEL": (
            funding_df["Spend for Reporting Period"].loc[(funding_df["Funding Source Name"].str.contains("CDEL"))].sum()
        ),
        "RDEL": (
            funding_df["Spend for Reporting Period"].loc[(funding_df["Funding Source Name"].str.contains("RDEL"))].sum()
        ),
        "Total": (funding_df["Spend for Reporting Period"].sum()),
    }

    # Business logic here is taken from spreadsheet 4a - Funding Profile Z45 for grand total expenditure
    return funding_spent


def get_allocated_funding(idx: str, expense_type: str) -> int:
    """return the total funding allocated of a given expense_type for a project or programme ID

    :param idx: The ID of the funded entity project/programme
    :param expense_type: The type of allocated expense i.e. CDEL, RDEL or grand total.

    :return: Total funding allocated for entity and expense_type
    """
    return int(FUNDING_ALLOCATION[expense_type][idx])


def validate_psi_funding_not_negative(workbook: dict[str, pd.DataFrame]) -> list["GenericFailure"] | None:
    """
    Validates that Private Sector Funding amounts are not negative.

    This function checks the 'Private Investments' sheet for rows where either
    'Private Sector Funding Required' or 'Private Sector Funding Secured' is negative.
    If invalid rows are found, it returns a list of validation failures.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors or None if no errors are found.
    """
    psi_df = workbook["Private Investments"]
    cols_to_check = ("Private Sector Funding Required", "Private Sector Funding Secured")
    # coerce to numeric so that value can be checked if less than 0, and error not raised on strings
    errors = [
        (col, index)
        for col in cols_to_check
        for index, val in pd.to_numeric(psi_df[col], errors="coerce").iteritems()
        if val < 0
    ]

    if len(errors) > 0:
        return [
            GenericFailure(
                table="Private Investments",
                section="Private Sector Investment",
                column=col,
                message=msgs.NEGATIVE_NUMBER,
                row_index=index,
            )
            for col, index in errors
        ]


def validate_postcodes(workbook: dict[str, pd.DataFrame]) -> list["GenericFailure"] | None:
    """Validates that post codes entered on project admin tab match correct format for a postcode.

    If rows in project details table contain a value for Locations but no valid post code in Postcodes
    The information was entered in a form other than a valid postcode


    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    project_details_df = workbook["Project Details"]

    return [
        GenericFailure(
            table="Project Details",
            section="Project Details",
            column="Postcodes",
            message=msgs.POSTCODE,
            row_index=index,
        )
        for index, row in project_details_df.iterrows()
        if pd.notna(row["Locations"]) and not re.search(POSTCODE_REGEX, str(row["Postcodes"]))
    ]


def validate_funding_questions(workbook: dict[str, pd.DataFrame]) -> list["GenericFailure"] | None:
    """Validates the Funding Questions table.

    Validates that all cells have values and any dropdowns are used correctly.

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    funding_questions = workbook["Funding Questions"]
    check_dropdown = {
        "Beyond these three funding types, have you received any payments for specific projects?": YesNoEnum,
        "Please confirm whether the amount utilised represents your entire allocation": YesNoEnum,
        "Please select the option that best describes how the funding was, or will be, utilised": FundingUses,
    }
    check_numeric = ("Please indicate how much of your allocation has been utilised (in £s)",)

    failures = []
    for index, row in funding_questions.iterrows():
        column = row["Indicator"] if pd.notna(row["Indicator"]) else "All Columns"
        question = row["Question"]
        response = row["Response"]

        # do blank check
        if is_blank(response):
            failures.append(
                GenericFailure(
                    table="Funding Questions",
                    section='Towns Deal Only - "Other/Early" TD Funding',
                    column=column,
                    message=msgs.BLANK,
                    row_index=index,
                )
            )
            continue

        # do dropdown check
        if enum := check_dropdown.get(question):
            if not is_from_dropdown(response, enum):
                failures.append(
                    GenericFailure(
                        table="Funding Questions",
                        section='Towns Deal Only - "Other/Early" TD Funding',
                        column=column,
                        message=msgs.DROPDOWN,
                        row_index=index,
                    )
                )
                continue

        # is numeric check
        if question in check_numeric:
            if not is_numeric(response):
                failures.append(
                    GenericFailure(
                        table="Funding Questions",
                        section='Towns Deal Only - "Other/Early" TD Funding',
                        column=column,
                        message=msgs.WRONG_TYPE_NUMERICAL,
                        row_index=index,
                    )
                )

    return failures


def validate_project_progress(workbook: dict[str, pd.DataFrame]) -> list["GenericFailure"]:
    """
    Validates the Project Progress table for Round 4 submissions.

    Checks for specific conditions in the data related to project progress and returns a list of
    TownsFundRoundFourValidationFailure instances for any validation failures found.

    Conditions Checked:
    - If the project's delivery status is 'Not Yet Started' or 'Ongoing Delayed':
        - Validates the 'Leading Factor of Delay' column for null values.
    - For projects with a delivery status other than '4. Completed':
        - Validates the following columns for null values:
            - 'Current Project Delivery Stage'
            - 'Most Important Upcoming Comms Milestone'
            - 'Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)'

    :param workbook: A dictionary containing sheet names as keys and pandas DataFrames
                     representing each sheet in the Round 4 submission.
    :return: A list of TownsFundRoundFourValidationFailure instances if validation failures occur,
             otherwise returns an empty list.
    """
    project_progress_df = workbook["Project Progress"]
    delayed_mask = project_progress_df["Project Delivery Status"].isin(
        {StatusEnum.NOT_YET_STARTED, StatusEnum.ONGOING_DELAYED}
    )
    complete_mask = project_progress_df["Project Delivery Status"].isin({StatusEnum.COMPLETED})

    project_delayed_rows = project_progress_df[delayed_mask]
    project_incomplete_rows = project_progress_df[~complete_mask]

    # the column to check alongside the rows it should be checked in and the failure message
    columns_to_check = [
        ("Leading Factor of Delay", project_delayed_rows, msgs.BLANK),
        ("Current Project Delivery Stage", project_incomplete_rows, msgs.BLANK_IF_PROJECT_INCOMPLETE),
        ("Most Important Upcoming Comms Milestone", project_incomplete_rows, msgs.BLANK_IF_PROJECT_INCOMPLETE),
        (
            "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
            project_incomplete_rows,
            msgs.BLANK_IF_PROJECT_INCOMPLETE,
        ),
    ]

    failures = []
    for column, invalid_rows, message in columns_to_check:
        invalid_rows = find_null_values(invalid_rows, column)
        for _, row in invalid_rows.iterrows():
            failures.append(
                GenericFailure(
                    table="Project Progress",
                    section="Projects Progress Summary",
                    column=column,
                    message=message,
                    row_index=row.name,
                )
            )

    return failures


def validate_sign_off(workbook: dict[str, pd.DataFrame]) -> list[GenericFailure]:
    """Validates Name, Role, and Date for the Review & Sign-Off Section

    :param workbook: A dictionary where keys are sheet names and values are pandas
                     DataFrames representing each sheet in the Round 4 submission.
    :return: ValidationErrors
    """
    sheet = workbook["8 - Review & Sign-Off"]
    sheet.replace(r"", np.nan, inplace=True)

    section_151_text_cells = [7, 8, 10]
    town_board_chair_cells = [14, 15, 17]

    failures = []

    for y_axis in [*town_board_chair_cells, *section_151_text_cells]:
        if pd.isnull(sheet.iloc[y_axis, 2]):
            failures.append(
                GenericFailure(
                    table="Review & Sign-Off", section="-", cell_index="C" + str(y_axis + 1), message=msgs.BLANK
                )
            )

    return failures
