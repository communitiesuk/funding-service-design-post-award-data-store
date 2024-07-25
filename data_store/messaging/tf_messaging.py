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

    # Internal column names to Round 3 & 4 TF column and section mapping
    INTERNAL_COLUMN_TO_FORM_COLUMN_AND_SECTION = {
        "Single or Multiple Locations": (
            "Does the project have a single location (e.g. one site) or multiple (e.g. multiple sites or across a "
            "number of post codes)?",
            "Project Details",
        ),
        "GIS Provided": ("Are you providing a GIS map (see guidance) with your return?", "Project Details"),
        "Answer": ("Answer", "Programme-Wide Progress Summary"),
        "Start Date": ("Start Date - mmm/yy (e.g. Dec-22)", "Projects Progress Summary"),
        "Completion Date": ("Completion Date - mmm/yy (e.g. Dec-22)", "Projects Progress Summary"),
        "Current Project Delivery Stage": ("Current Project Delivery Stage", "Projects Progress Summary"),
        "Project Adjustment Request Status": ("Project Adjustment Request Status", "Projects Progress Summary"),
        "Project Delivery Status": ("Project Delivery Status", "Projects Progress Summary"),
        "Leading Factor of Delay": ("Leading Factor of Delay", "Projects Progress Summary"),
        "Delivery (RAG)": ("Delivery (RAG)", "Projects Progress Summary"),
        "Spend (RAG)": ("Spend (RAG)", "Projects Progress Summary"),
        "Risk (RAG)": ("Risk (RAG)", "Projects Progress Summary"),
        "Commentary on Status and RAG Ratings": ("Commentary on Status and RAG Ratings", "Projects Progress Summary"),
        "Most Important Upcoming Comms Milestone": (
            "Most Important Upcoming Comms Milestone",
            "Projects Progress Summary",
        ),
        "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": (
            "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
            "Projects Progress Summary",
        ),
        "Secured": ("Has this funding source been secured?", "Project Funding Profiles"),
        "GeographyIndicator": ("Geography Indicator", "Outcome Indicators (excluding footfall)"),
        "RiskName": ("Risk Name", "Programme / Project Risks"),
        "RiskCategory": ("Risk Category", "Programme / Project Risks"),
        "Short Description": ("Short description of the Risk", "Programme / Project Risks"),
        "Full Description": ("Full Description", "Programme / Project Risks"),
        "Consequences": ("Consequences", "Programme / Project Risks"),
        "Pre-mitigatedImpact": ("Pre-mitigated Impact", "Programme / Project Risks"),
        "Pre-mitigatedLikelihood": ("Pre-mitigated Likelihood", "Programme / Project Risks"),
        "Mitigatons": ("Mitigations", "Programme / Project Risks"),
        "PostMitigatedImpact": ("Post-Mitigated Impact", "Programme / Project Risks"),
        "PostMitigatedLikelihood": ("Post-mitigated Likelihood", "Programme / Project Risks"),
        "Proximity": ("Proximity", "Programme / Project Risks"),
        "RiskOwnerRole": ("Risk Owner/Role", "Programme / Project Risks"),
        "Funding Source Name": ("Funding Source Name", "Project Funding Profiles"),
        "Funding Source Type": ("Funding Source", "Project Funding Profiles"),
        "Start_Date": ("H1 (Apr-Sep)", "Project Funding Profiles"),
        "End_Date": ("H2 (Oct-Mar)", "Project Funding Profiles"),
        "Total Project Value": ("Total Project Value (£)", "Private Sector Investment"),
        "Townsfund Funding": ("Award From Townsfund (£)", "Private Sector Investment"),
        "Output": ("Indicator Name", "Project Outputs"),
        "Unit of Measurement": ("Unit of Measurement", "Project Outputs"),
        "UnitofMeasurement": ("Unit of Measurement", "Outcome Indicators (excluding footfall) / Footfall Indicator"),
        "Outcome": ("Indicator Name", "Outcome Indicators (excluding footfall) / Footfall Indicator"),
        "Project Name": ("Project Name", "Project Details"),
        "Primary Intervention Theme": ("Primary Intervention Theme", "Project Details"),
        "Locations": ("Project Location(s) - Post Code (e.g. SW1P 4DF)", "Project Details"),
        "Lat/Long": ("Project Location - Lat/Long Coordinates (3.d.p e.g. 51.496, -0.129)", "Project Details"),
        "Private Sector Funding Required": ("Private Sector Funding Required", "Private Sector Investment"),
        "Private Sector Funding Secured": ("Private Sector Funding Secured", "Private Sector Investment"),
        "Spend for Reporting Period": ("Financial Year 2022/21 - Financial Year 2025/26", "Project Funding Profiles"),
        "Amount": ("Financial Year 2022/21 - Financial Year 2025/26", "Project Outputs"),
    }

    # mapping of user submitted column names per table to its original excel column letter index
    # for the Towns Fund round 4 spreadsheet
    TABLE_AND_COLUMN_TO_ORIGINAL_COLUMN_LETTER = {
        "Place Details": {"Question": "C{i}", "Indicator": "D{i}", "Answer": "E{i}"},
        "Project Details": {
            "Project name": "E{i}",
            "Primary Intervention Theme": "F{i}",
            "Single or Multiple Locations": "G{i}",
            "Locations": "H{i} or K{i}",
            "Postcodes": "H{i} or K{i}",
            "Lat/Long": "I{i} or L{i}",
            "GIS Provided": "J{i}",
        },
        "Programme Progress": {"Question": "C{i}", "Answer": "D{i}"},
        "Project Progress": {
            "Start Date": "D{i}",
            "Completion Date": "E{i}",
            "Current Project Delivery Stage": "F{i}",
            "Project Delivery Status": "G{i}",
            "Leading Factor of Delay": "H{i}",
            "Project Adjustment Request Status": "I{i}",
            "Delivery (RAG)": "J{i}",
            "Spend (RAG)": "K{i}",
            "Risk (RAG)": "L{i}",
            "Commentary on Status and RAG Ratings": "M{i}",
            "Most Important Upcoming Comms Milestone": "N{i}",
            "Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)": "O{i}",
        },
        "Funding Questions": {
            "All Columns": "E{i}",  # stretches across all 3 columns below
            "TD 5% CDEL Pre-Payment\n(Towns Fund FAQs p.46 - 49)": "E{i}",
            "TD RDEL Capacity Funding": "F{i}",
            "TD Accelerated Funding": "I{i}",
        },
        "Funding Comments": {"Comment": "C{i} to E{i}"},
        "Funding": {
            "Funding Source Name": "C{i}",
            "Funding Source Type": "D{i}",
            "Secured": "E{i}",
            "Spend for Reporting Period": "F{i} to Y{i}",
            "Grand Total": "Z{i}",
        },
        "Private Investments": {
            "Private Sector Funding Required": "G{i}",
            "Private Sector Funding Secured": "H{i}",
            "Additional Comments": "J{i}",
        },
        "Output_Data": {
            "Output": "C{i}",
            "Unit of Measurement": "D{i}",
            "Amount": "E{i} to W{i}",
            "Additional Information": "Y{i}",
        },
        "Outcome_Data": {
            "Outcome": "B{i}",
            "UnitofMeasurement": "C{i}",
            "Relevant project(s)": "D{i}",
            "GeographyIndicator": "E{i}",
            "Amount": "F{i} to O{i}",
            "Higher Frequency": "P{i}",
        },
        "RiskRegister": {
            "RiskName": "C{i}",
            "RiskCategory": "D{i}",
            "Short Description": "E{i}",
            "Full Description": "F{i}",
            "Consequences": "G{i}",
            "Pre-mitigatedImpact": "H{i}",
            "Pre-mitigatedLikelihood": "I{i}",
            "Mitigatons": "K{i}",
            "PostMitigatedImpact": "L{i}",
            "PostMitigatedLikelihood": "M{i}",
            "Proximity": "O{i}",
            "RiskOwnerRole": "P{i}",
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
                "Project ID",
                "Programme ID",
                "Start_Date",
                "End_Date",
                "Actual/Forecast",
            ]  # these columns do not translate to the spreadsheet
        )

        return Message(sheet, section, cell_indexes, message, validation_failure.__class__.__name__)

    def _wrong_type_failure_message(self, validation_failure: WrongTypeFailure) -> Message:
        sheet = self.INTERNAL_TABLE_TO_FORM_SHEET[validation_failure.table]
        _, section = self.INTERNAL_COLUMN_TO_FORM_COLUMN_AND_SECTION[validation_failure.column]
        actual_type = self.INTERNAL_TYPE_TO_MESSAGE_FORMAT[validation_failure.actual_type]
        cell_index = self._construct_cell_index(
            table=validation_failure.table,
            column=validation_failure.column,
            row_index=validation_failure.row_index,
        )

        if sheet == "Outcomes":
            _, section = (
                "Financial Year 2022/21 - Financial Year 2029/30",
                ("Outcome Indicators (excluding " "footfall) and Footfall Indicator"),
            )
            cell_index = self._get_cell_indexes_for_outcomes(validation_failure.failed_row)

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

        return Message(sheet, section, (cell_index,), message, validation_failure.__class__.__name__)

    def _invalid_enum_value_failure_message(self, validation_failure: InvalidEnumValueFailure) -> Message:
        sheet = self.INTERNAL_TABLE_TO_FORM_SHEET[validation_failure.table]
        column, section = self.INTERNAL_COLUMN_TO_FORM_COLUMN_AND_SECTION[validation_failure.column]
        message = self.msgs.DROPDOWN

        # additional logic for outcomes to differentiate between footfall and non-footfall
        if sheet == "Outcomes" and validation_failure.row_values[4] == "Year-on-year % change in monthly footfall":
            section = "Footfall Indicator"
            # +5 as GeographyIndicator is 5 rows below Footfall Indicator
            if column == "Geography Indicator":
                actual_index = validation_failure.row_index + 5
                cell_index = f"C{actual_index}"
                return Message(sheet, section, (cell_index,), message, validation_failure.__class__.__name__)

        # additional logic for risk location
        if sheet == "Risk Register":
            project_id = validation_failure.row_values[1]
            section = self._risk_register_section(project_id, validation_failure.row_index, validation_failure.table)

        if section == "Project Funding Profiles":
            project_number = get_project_number_by_position(validation_failure.row_index, validation_failure.table)
            section = f"Project Funding Profiles - Project {project_number}"

        cell_index = self._construct_cell_index(
            table=validation_failure.table,
            column=validation_failure.column,
            row_index=validation_failure.row_index,
        )

        return Message(sheet, section, (cell_index,), message, validation_failure.__class__.__name__)

    def _non_nullable_constraint_failure_message(self, validation_failure: NonNullableConstraintFailure) -> Message:
        """Generate error message components for NonNullableConstraintFailure.

        This function returns error message components in the case of a NonNullableConstraintFailure.
        In instances where the Unit of Measurement is null, a distinct error message is necessary.
        The function distinguishes between Outputs and Outcomes and adjusts the error message accordingly.

        return: tuple[str, str, str]: A tuple containing the sheet name, section, and error message.
        """
        sheet = self.INTERNAL_TABLE_TO_FORM_SHEET[validation_failure.table]
        column, section = self.INTERNAL_COLUMN_TO_FORM_COLUMN_AND_SECTION[validation_failure.column]

        cell_index = self._construct_cell_index(
            table=validation_failure.table,
            column=validation_failure.column,
            row_index=validation_failure.row_index,
        )

        message = self.msgs.BLANK
        if sheet == "Project Outputs":
            if column == "Unit of Measurement":
                message = self.msgs.BLANK_UNIT_OF_MEASUREMENT
            if column == "Financial Year 2022/21 - Financial Year 2025/26":
                message = self.msgs.BLANK_ZERO
        elif sheet == "Outcomes":
            if column == "Unit of Measurement":
                message = self.msgs.BLANK_UNIT_OF_MEASUREMENT
            if column == "Financial Year 2022/21 - Financial Year 2025/26":
                section = "Outcome Indicators (excluding footfall) / Footfall Indicator"
                message = self.msgs.BLANK_ZERO
                cell_index = self._get_cell_indexes_for_outcomes(validation_failure.failed_row)
        elif sheet == "Funding Profiles":
            message = self.msgs.BLANK_ZERO
        elif section == "Programme-Wide Progress Summary":
            message = self.msgs.BLANK

        return Message(sheet, section, (cell_index,), message, validation_failure.__class__.__name__)

    def _unauthorised_submission_failure(self, validation_failure: UnauthorisedSubmissionFailure) -> Message:
        places_or_funds = join_as_string(validation_failure.expected_values)
        message = self.msgs.UNAUTHORISED.format(
            entered_value=validation_failure.entered_value, allowed_values=places_or_funds
        )
        return Message(None, None, None, message, validation_failure.__class__.__name__)

    def _generic_failure(self, validation_failure: GenericFailure) -> Message:
        if not validation_failure.cell_index:
            validation_failure.cell_index = self._construct_cell_index(
                validation_failure.table,
                validation_failure.column,
                validation_failure.row_index,
            )
        sheet = self.INTERNAL_TABLE_TO_FORM_SHEET[validation_failure.table]

        return Message(
            sheet,
            validation_failure.section,
            (validation_failure.cell_index,),
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

    def _get_section_for_outcomes_by_row_index(self, index):
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
        start_date = failed_row["Start_Date"]
        financial_year = self._get_uk_financial_year_start(start_date)
        index = failed_row.name

        # footfall outcomes starts from row 60
        if self._get_section_for_outcomes_by_row_index(index) == "Footfall Indicator":
            # row for 'Amount' column is end number of start year of financial year * 5 + 'Footfall Indicator' index
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
