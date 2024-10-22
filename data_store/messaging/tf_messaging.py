from datetime import datetime

import pandas as pd

from data_store.messaging import Message, MessengerBase, SharedMessages
from data_store.util import get_project_number_by_position, join_as_string
from data_store.validation.towns_fund.failures.user import (
    GenericFailure,
    InvalidEnumValueFailure,
    NonNullableConstraintFailure,
    NonUniqueCompositeKeyFailure,
    UnauthorisedSubmissionFailure,
    UserValidationFailure,
    WrongTypeFailure,
)


class TFMessages(SharedMessages):
    """Towns Fund specific validation failure messages to be returned to the user."""

    OVERSPEND = (
        "The total {expense_type} amount is greater than your allocation. Check the data for each financial year "
        "is correct."
    )
    OVERSPEND_PROGRAMME = (
        "The grand total amounts are greater than your allocation. Check the data for each financial year is correct."
    )
    MISSING_OTHER_FUNDING_SOURCES = (
        "You’ve not entered any Other Funding Sources. You must enter at least 1 over all projects."
    )
    DATA_MISMATCH_PROJECT_START = (
        "You've entered a project start date that is before the end of the reporting period, but the project delivery "
        "status has been entered as 'Not yet started'. Add a valid start date or change the status."
    )


class TFMessenger(MessengerBase):
    """Messaging class ABC. Classes that inherit must implement a constructor, and failures_to_message function"""

    # Internal table names to Round 3 & 4 TF tab names mapping
    INTERNAL_TABLE_TO_FORM_SHEET = {
        "Project Details": "Project Admin",
        "Project Progress": "Programme Progress",
        "Programme Progress": "Programme Progress",
        "Funding": "Funding Profiles",
        "Funding Questions": "Funding Profiles",
        "Outcome_Data": "Outcomes",
        "Output_Data": "Project Outputs",
        "RiskRegister": "Risk Register",
        "Place Details": "Project Admin",
        "Private Investments": "PSI",
        "Review & Sign-Off": "Review & Sign-Off",
    }

    # Internal table and column names to spreadsheet section and column names mapping
    INTERNAL_TABLE_AND_COLUMN_TO_SPREADSHEET_SECTION_AND_COLUMNS = {
        "Project Details": {
            "section": "Project Details",
            "columns": {
                "location_multiplicity": (
                    "Does the project have a single location (e.g. one site) or multiple (e.g. multiple sites or "
                    "across a number of post codes)?"
                ),
                "gis_provided": "Are you providing a GIS map (see guidance) with your return?",
                "project_name": "Project Name",
                "primary_intervention_theme": "Primary Intervention Theme",
                "locations": "Project Location(s) - Post Code (e.g. SW1P 4DF)",
                "lat_long": "Project Location - Lat/Long Coordinates (3.d.p e.g. 51.496, -0.129)",
            },
        },
        "Programme Progress": {
            "section": "Programme Progress",
            "columns": {
                "answer": "Answer",
            },
        },
        "Project Progress": {
            "section": "Projects Progress Summary",
            "columns": {
                "start_date": "Start Date - mmm/yy (e.g. Dec-22)",
                "end_date": "Completion Date - mmm/yy (e.g. Dec-22)",
                "delivery_stage": "Current Project Delivery Stage",
                "adjustment_request_status": "Project Adjustment Request Status",
                "delivery_status": "Project Delivery Status",
                "leading_factor_of_delay": "Leading Factor of Delay",
                "delivery_rag": "Delivery (RAG)",
                "spend_rag": "Spend (RAG)",
                "risk_rag": "Risk (RAG)",
                "commentary": "Commentary on Status and RAG Ratings",
                "important_milestone": "Most Important Upcoming Comms Milestone",
                "date_of_important_milestone": "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
            },
        },
        "Funding": {
            "section": "Project Funding Profiles",
            "columns": {
                "secured": "Has this funding source been secured?",
                "funding_source": "Funding Source Name",
                "spend_type": "Funding Source Type",
                "start_date": "H1 (Apr-Sep)",
                "end_date": "H2 (Oct-Mar)",
                "spend_for_reporting_period": "Financial Year 2021/22 - Financial Year 2025/26",
            },
        },
        "RiskRegister": {
            "section": "Programme / Project Risks",
            "columns": {
                "risk_name": "Risk Name",
                "risk_category": "Risk Category",
                "short_desc": "Short description of the Risk",
                "full_desc": "Full Description",
                "consequences": "Consequences",
                "pre_mitigated_impact": "Pre-mitigated Impact",
                "pre_mitigated_likelihood": "Pre-mitigated Likelihood",
                "mitigations": "Mitigations",
                "post_mitigated_impact": "Post-Mitigated Impact",
                "post_mitigated_likelihood": "Post-mitigated Likelihood",
                "proximity": "Proximity",
                "risk_owner_role": "Risk Owner/Role",
            },
        },
        "Private Investments": {
            "section": "Private Sector Investment",
            "columns": {
                "total_project_value": "Total Project Value (£)",
                "townsfund_funding": "Award From Townsfund (£)",
                "private_sector_funding_required": "Private Sector Funding Required",
                "private_sector_funding_secured": "Private Sector Funding Secured",
            },
        },
        "Output_Data": {
            "section": "Project Outputs",
            "columns": {
                "output": "Output",
                "unit_of_measurement": "Unit of Measurement",
                "amount": "Financial Year 2021/22 - Financial Year 2025/26",
            },
        },
        "Outcome_Data": {
            "section": "Outcome Indicators (excluding footfall) / Footfall Indicator",
            "columns": {
                "geography_indicator": "Geography Indicator",
                "unit_of_measurement": "Unit of Measurement",
                "outcome": "Indicator Name",
                "amount": "Financial Year 2021/22 - Financial Year 2025/26",
            },
        },
    }

    # mapping of user submitted column names per table to its original excel column letter index
    # for the Towns Fund round 4 spreadsheet
    TABLE_AND_COLUMN_TO_ORIGINAL_COLUMN_LETTER = {
        "Place Details": {"question": "C{i}", "indicator": "D{i}", "answer": "E{i}"},
        "Project Details": {
            "project_name": "E{i}",
            "primary_intervention_theme": "F{i}",
            "location_multiplicity": "G{i}",
            "locations": "H{i} or K{i}",
            "postcodes": "H{i} or K{i}",
            "lat_long": "I{i} or L{i}",
            "gis_provided": "J{i}",
        },
        "Programme Progress": {"question": "C{i}", "answer": "D{i}"},
        "Project Progress": {
            "start_date": "D{i}",
            "end_date": "E{i}",
            "delivery_stage": "F{i}",
            "delivery_status": "G{i}",
            "leading_factor_of_delay": "H{i}",
            "adjustment_request_status": "I{i}",
            "delivery_rag": "J{i}",
            "spend_rag": "K{i}",
            "risk_rag": "L{i}",
            "commentary": "M{i}",
            "important_milestone": "N{i}",
            "date_of_important_milestone": "O{i}",
        },
        "Funding Questions": {
            "All Columns": "E{i}",  # stretches across all 3 columns below
            "TD 5% CDEL Pre-Payment\n(Towns Fund FAQs p.46 - 49)": "E{i}",
            "TD RDEL Capacity Funding": "F{i}",
            "TD Accelerated Funding": "I{i}",
        },
        "Funding Comments": {"comment": "C{i} to E{i}"},
        "Funding": {
            "funding_source": "C{i}",
            "spend_type": "D{i}",
            "secured": "E{i}",
            "spend_for_reporting_period": "F{i} to Y{i}",
            "Grand Total": "Z{i}",
        },
        "Private Investments": {
            "private_sector_funding_required": "G{i}",
            "private_sector_funding_secured": "H{i}",
            "additional_comments": "J{i}",
        },
        "Output_Data": {
            "output": "C{i}",
            "unit_of_measurement": "D{i}",
            "amount": "E{i} to W{i}",
            "additional_information": "Y{i}",
        },
        "Outcome_Data": {
            "outcome": "B{i}",
            "unit_of_measurement": "C{i}",
            "Relevant project(s)": "D{i}",
            "geography_indicator": "E{i}",
            "amount": "F{i} to O{i}",
            "higher_frequency": "P{i}",
        },
        "RiskRegister": {
            "risk_name": "C{i}",
            "risk_category": "D{i}",
            "short_desc": "E{i}",
            "full_desc": "F{i}",
            "consequences": "G{i}",
            "pre_mitigated_impact": "H{i}",
            "pre_mitigated_likelihood": "I{i}",
            "mitigations": "K{i}",
            "post_mitigated_impact": "L{i}",
            "post_mitigated_likelihood": "M{i}",
            "proximity": "O{i}",
            "risk_owner_role": "P{i}",
        },
    }

    INTERNAL_TYPE_TO_MESSAGE_FORMAT = {
        datetime: "a date",
        float: "a number",
        str: "text",
        int: "a number",
        object: "an unknown datatype",
    }

    # maps the financial year's start year back to original col letter for non-footfall outcomes
    FINANCIAL_YEAR_TO_ORIGINAL_COLUMN_LETTER_FOR_NON_FOOTFALL_OUTCOMES = {
        2020: "F{i}",
        2021: "G{i}",
        2022: "H{i}",
        2023: "I{i}",
        2024: "J{i}",
        2025: "K{i}",
        2026: "L{i}",
        2027: "M{i}",
        2028: "N{i}",
        2029: "O{i}",
    }

    # maps the month of the financial year's start year back to the original column for footfall outcomes
    MONTH_TO_ORIGINAL_COLUMN_LETTER_FOR_FOOTFALL_OUTCOMES = {
        4: "D{i}",
        5: "E{i}",
        6: "F{i}",
        7: "G{i}",
        8: "H{i}",
        9: "I{i}",
        10: "J{i}",
        11: "K{i}",
        12: "L{i}",
        1: "M{i}",
        2: "N{i}",
        3: "O{i}",
    }

    msgs = TFMessages()

    def to_message(self, validation_failure: UserValidationFailure) -> Message:
        if isinstance(validation_failure, NonUniqueCompositeKeyFailure):
            return self._non_unique_composite_key_failure_message(validation_failure)
        elif isinstance(validation_failure, WrongTypeFailure):
            return self._wrong_type_failure_message(validation_failure)
        elif isinstance(validation_failure, InvalidEnumValueFailure):
            return self._invalid_enum_value_failure_message(validation_failure)
        elif isinstance(validation_failure, NonNullableConstraintFailure):
            return self._non_nullable_constraint_failure_message(validation_failure)
        elif isinstance(validation_failure, UnauthorisedSubmissionFailure):
            return self._unauthorised_submission_failure(validation_failure)
        elif isinstance(validation_failure, GenericFailure):
            return self._generic_failure(validation_failure)
        else:
            raise TypeError(
                f"Validation failure of type {type(validation_failure)} is not supported by "
                f"{self.__class__.__name__}.{self.to_message.__name__}"
            )

    def _non_unique_composite_key_failure_message(self, validation_failure: NonUniqueCompositeKeyFailure) -> Message:
        """Generate user-centered components for NonUniqueCompositeKeyFailure.

        This function returns user-centered components in the case of a NonUniqueCompositeKeyFailure.
        When a Unique combination of cell values is required on separate row to act as composite keys this function
        will return a message. The function distinguishes between Funding profiles, Outputs, Outcomes, and Risk Register
        and displays an appropriate message.

        return: tuple[str, str, str]: A tuple containing the sheet name, section, and error message.
        """
        sheet = self.INTERNAL_TABLE_TO_FORM_SHEET[validation_failure.table]
        message = self.msgs.DUPLICATION

        if sheet == "Funding Profiles":
            project_number = get_project_number_by_position(validation_failure.row_index, validation_failure.table)
            section = f"Funding Profiles - Project {project_number}"
        elif sheet == "Project Outputs":
            project_number = get_project_number_by_position(validation_failure.row_index, validation_failure.table)
            section = f"Project Outputs - Project {project_number}"
        elif sheet == "Outcomes":
            section = self._get_section_for_outcomes_by_row_index(validation_failure.row_index)
        elif sheet == "Risk Register":
            project_id = validation_failure.row[1]
            section = self._risk_register_section(project_id, validation_failure.row_index, validation_failure.table)
        else:
            raise ValueError(f"Unrecognised sheet during messaging, {sheet}")

        # TODO: Can we return a Failure for each column separately and let them be joined together downstream
        cell_indexes = tuple(
            self._construct_cell_index(
                table=validation_failure.table, column=column, row_index=validation_failure.row_index
            )
            for column in validation_failure.column
            if column
            not in [
                "project_id",
                "programme_id",
                "start_date",
                "end_date",
                "state",
            ]  # these columns do not translate to the spreadsheet
        )

        return Message(sheet, section, cell_indexes, message, validation_failure.__class__.__name__)

    def _wrong_type_failure_message(self, validation_failure: WrongTypeFailure) -> Message:
        sheet = self.INTERNAL_TABLE_TO_FORM_SHEET[validation_failure.table]
        section_columns = self.INTERNAL_TABLE_AND_COLUMN_TO_SPREADSHEET_SECTION_AND_COLUMNS[validation_failure.table]
        section = section_columns["section"]
        actual_type = self.INTERNAL_TYPE_TO_MESSAGE_FORMAT[validation_failure.actual_type]

        # if column is a str make it a list
        columns = (
            [validation_failure.column] if isinstance(validation_failure.column, str) else validation_failure.column
        )

        cell_index: tuple[str, ...] | None = tuple(
            self._construct_cell_index(
                table=validation_failure.table,
                column=column,
                row_index=validation_failure.row_index,
            )
            for column in columns
        )

        if sheet == "Outcomes":
            _, section = (
                "Financial Year 2021/22 - Financial Year 2029/30",
                ("Outcome Indicators (excluding " "footfall) and Footfall Indicator"),
            )

            cell_index = (
                (self._get_cell_indexes_for_outcomes(validation_failure.failed_row),)
                if validation_failure.failed_row is not None
                else None
            )
        if validation_failure.expected_type == datetime:
            message = self.msgs.WRONG_TYPE_DATE.format(wrong_type=actual_type)
        elif sheet == "PSI":
            message = self.msgs.WRONG_TYPE_CURRENCY
        elif sheet == "Funding Profiles":
            message = self.msgs.WRONG_TYPE_CURRENCY
        elif sheet in ["Project Outputs", "Outcomes"]:
            message = self.msgs.WRONG_TYPE_NUMERICAL
        else:
            message = self.msgs.WRONG_TYPE_UNKNOWN

        return Message(sheet, section, cell_index, message, validation_failure.__class__.__name__)

    def _invalid_enum_value_failure_message(self, validation_failure: InvalidEnumValueFailure) -> Message:
        sheet = self.INTERNAL_TABLE_TO_FORM_SHEET[validation_failure.table]
        section_columns = self.INTERNAL_TABLE_AND_COLUMN_TO_SPREADSHEET_SECTION_AND_COLUMNS[validation_failure.table]
        section = section_columns["section"]
        column = section_columns["columns"][validation_failure.column]
        message = self.msgs.DROPDOWN

        # additional logic for outcomes to differentiate between footfall and non-footfall
        if sheet == "Outcomes" and validation_failure.row_values[4] == "Year-on-year % change in monthly footfall":
            section = "Footfall Indicator"
            # +5 as Geography Indicator is 5 rows below Footfall Indicator
            if column == "Geography Indicator":
                actual_index = validation_failure.row_index + 5
                return Message(sheet, section, (f"C{actual_index}",), message, validation_failure.__class__.__name__)

        # additional logic for risk location
        if sheet == "Risk Register":
            project_id = validation_failure.row_values[1]
            section = self._risk_register_section(project_id, validation_failure.row_index, validation_failure.table)

        if section == "Project Funding Profiles":
            project_number = get_project_number_by_position(validation_failure.row_index, validation_failure.table)
            section = f"Project Funding Profiles - Project {project_number}"

        # if column is a str make it a list
        columns = (
            [validation_failure.column] if isinstance(validation_failure.column, str) else validation_failure.column
        )

        cell_index = tuple(
            self._construct_cell_index(
                table=validation_failure.table,
                column=column,
                row_index=validation_failure.row_index,
            )
            for column in columns
        )

        return Message(sheet, section, cell_index, message, validation_failure.__class__.__name__)

    def _non_nullable_constraint_failure_message(self, validation_failure: NonNullableConstraintFailure) -> Message:
        """Generate error message components for NonNullableConstraintFailure.

        This function returns error message components in the case of a NonNullableConstraintFailure.
        In instances where the Unit of Measurement is null, a distinct error message is necessary.
        The function distinguishes between Outputs and Outcomes and adjusts the error message accordingly.

        return: tuple[str, str, str]: A tuple containing the sheet name, section, and error message.
        """
        sheet = self.INTERNAL_TABLE_TO_FORM_SHEET[validation_failure.table]
        section_columns = self.INTERNAL_TABLE_AND_COLUMN_TO_SPREADSHEET_SECTION_AND_COLUMNS[validation_failure.table]
        section = section_columns["section"]
        column = section_columns["columns"][validation_failure.column]

        # if column is a str make it a list
        columns = (
            [validation_failure.column] if isinstance(validation_failure.column, str) else validation_failure.column
        )

        cell_index: tuple[str, ...] | None = tuple(
            self._construct_cell_index(
                table=validation_failure.table,
                column=column,
                row_index=validation_failure.row_index,
            )
            for column in columns
        )

        message = self.msgs.BLANK
        if sheet == "Project Outputs":
            if column == "Unit of Measurement":
                message = self.msgs.BLANK_UNIT_OF_MEASUREMENT
            if column == "Financial Year 2021/22 - Financial Year 2025/26":
                message = self.msgs.BLANK_ZERO
        elif sheet == "Outcomes":
            if column == "Unit of Measurement":
                message = self.msgs.BLANK_UNIT_OF_MEASUREMENT
            if column == "Financial Year 2021/22 - Financial Year 2025/26":
                section = "Outcome Indicators (excluding footfall) / Footfall Indicator"
                message = self.msgs.BLANK_ZERO
                cell_index = (
                    (self._get_cell_indexes_for_outcomes(validation_failure.failed_row),)
                    if validation_failure.failed_row is not None
                    else None
                )
        elif sheet == "Funding Profiles":
            message = self.msgs.BLANK_ZERO
        elif section == "Programme-Wide Progress Summary":
            message = self.msgs.BLANK

        return Message(sheet, section, cell_index, message, validation_failure.__class__.__name__)

    def _unauthorised_submission_failure(self, validation_failure: UnauthorisedSubmissionFailure) -> Message:
        places_or_funds = join_as_string(validation_failure.expected_values)
        message = self.msgs.UNAUTHORISED.format(
            entered_value=validation_failure.entered_value, allowed_values=places_or_funds
        )
        return Message(None, None, None, message, validation_failure.__class__.__name__)

    def _generic_failure(self, validation_failure: GenericFailure) -> Message:
        if validation_failure.cell_index is not None:
            cell_indexes = (validation_failure.cell_index,)
        elif validation_failure.column is not None:
            validation_failure.cell_index = self._construct_cell_index(
                table=validation_failure.table,
                column=validation_failure.column,
                row_index=validation_failure.row_index or 0,
            )

            cell_indexes = (validation_failure.cell_index,)
        else:
            cell_indexes = None

        return Message(
            self.INTERNAL_TABLE_TO_FORM_SHEET[validation_failure.table],
            validation_failure.section,
            cell_indexes,
            validation_failure.message,
            validation_failure.__class__.__name__,
        )

    def _construct_cell_index(self, table: str, column: str, row_index: int) -> str:
        """Constructs the index of an error from the column and row it occurred in.

        :param table: the internal table name where the error occurred
        :param column: the internal column name where the error occurred
        :param row_index: a row index where the error occurred
        :return: indexes tuple of constructed letter and number indexes
        """
        column_letter = self.TABLE_AND_COLUMN_TO_ORIGINAL_COLUMN_LETTER[table][column]
        return column_letter.format(i=row_index or "")

    def _get_section_for_outcomes_by_row_index(self, index: int) -> str:
        return "Outcomes Indicators (excluding footfall)" if index < 60 else "Footfall Indicator"

    def _get_cell_indexes_for_outcomes(self, failed_row: pd.Series) -> str:
        """
        Constructs cell indexes for outcomes based on the provided failed row.

        The function determines whether the error occurred in footfall outcomes (starting from row 60)
        or non-footfall outcomes. If the index is greater than or equal to 60, it calculates the cell
        index for footfall outcomes based on the provided 'Start_Date'. If the index is less than 60,
        it calculates the cell index for non-footfall outcomes.

        For footfall outcomes, the cell index is determined by adding a row index gap calculated from
        the start year of the UK financial year as each year represents an additional 5 rows in the
        original spreadsheet from the row where the entry for a given footfall outcome's data begins.

        :param failed_row: A pandas Series representing a row where an error has occurred.
        :return: A string containing the constructed cell index for outcomes.
        """
        start_date = failed_row["start_date"]
        financial_year = self._get_uk_financial_year_start(start_date)
        index = failed_row.name

        if not isinstance(index, int):
            raise TypeError(f"Cell index not int for failed row {failed_row}")

        # footfall outcomes starts from row 60
        if self._get_section_for_outcomes_by_row_index(index) == "Footfall Indicator":
            # row for 'amount' column is end number of start year of financial year * 5 + 'Footfall Indicator' index
            row_index_gap = int(str(financial_year)[-1]) * 5
            index = int(index) + row_index_gap
            cell_index = self.MONTH_TO_ORIGINAL_COLUMN_LETTER_FOR_FOOTFALL_OUTCOMES[start_date.month].format(i=index)
        else:
            cell_index = self.FINANCIAL_YEAR_TO_ORIGINAL_COLUMN_LETTER_FOR_NON_FOOTFALL_OUTCOMES[financial_year].format(
                i=index
            )

        return cell_index

    @staticmethod
    def _risk_register_section(project_id: None | str, row_index: int, table: str):
        """Works out the particular section of the Risk Register sheet that a row of data belongs to.

        :param project_id: Project ID for that row
        :param row_index:
        :param table:
        :return:
        """
        if pd.notna(project_id):
            # project risk
            project_number = get_project_number_by_position(row_index, table)
            section = f"Project Risks - Project {project_number}"
        else:
            # programme risk
            section = "Programme Risks"
        return section

    @staticmethod
    def _get_uk_financial_year_start(start_date: datetime) -> int:
        """
        Gets the start year of the UK financial year based on the provided start date.

        :param start_date: A datetime in the format '%Y-%m-%d %H:%M:%S'.
        :return: An integer representing the start year of the UK financial year.
        """

        financial_year = start_date.year if start_date.month >= 4 else start_date.year - 1
        return financial_year
