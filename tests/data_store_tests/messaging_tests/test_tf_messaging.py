from datetime import datetime

import pandas as pd
import pytest

from data_store.messaging import Message
from data_store.messaging.messaging import failures_to_messages
from data_store.messaging.tf_messaging import TFMessenger
from data_store.validation.towns_fund.failures.user import (
    GenericFailure,
    InvalidEnumValueFailure,
    NonNullableConstraintFailure,
    NonUniqueCompositeKeyFailure,
    UnauthorisedSubmissionFailure,
    WrongTypeFailure,
)


def test_invalid_enum_messages():
    test_messeger = TFMessenger()
    test_messeger._invalid_enum_value_failure_message(
        InvalidEnumValueFailure(
            table="Project Details",
            column="Single or Multiple Locations",
            row_index=1,
            row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        )
    )
    test_messeger._invalid_enum_value_failure_message(
        InvalidEnumValueFailure(
            table="Project Progress",
            column="Project Delivery Status",
            row_index=2,
            row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        )
    )
    test_messeger._invalid_enum_value_failure_message(
        InvalidEnumValueFailure(
            table="Project Progress",
            column="Delivery (RAG)",
            row_index=2,
            row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        )
    )
    test_messeger._invalid_enum_value_failure_message(
        InvalidEnumValueFailure(
            table="Project Progress",
            column="Spend (RAG)",
            row_index=2,
            row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        )
    )
    test_messeger._invalid_enum_value_failure_message(
        InvalidEnumValueFailure(
            table="Project Progress",
            column="Risk (RAG)",
            row_index=2,
            row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        )
    )
    test_messeger._invalid_enum_value_failure_message(
        InvalidEnumValueFailure(
            table="Funding",
            column="Secured",
            row_index=50,
            row_values=("TD-ABC-1", "Value 2", "Value 3", "Value 4"),
        )
    )
    test_messeger._invalid_enum_value_failure_message(
        InvalidEnumValueFailure(
            table="RiskRegister",
            column="Pre-mitigatedImpact",
            row_index=23,
            row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        )
    )
    test_messeger._invalid_enum_value_failure_message(
        InvalidEnumValueFailure(
            table="RiskRegister",
            column="Pre-mitigatedLikelihood",
            row_index=24,
            row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        )
    )
    test_messeger._invalid_enum_value_failure_message(
        InvalidEnumValueFailure(
            table="RiskRegister",
            column="PostMitigatedImpact",
            row_index=25,
            row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        )
    )
    test_messeger._invalid_enum_value_failure_message(
        InvalidEnumValueFailure(
            table="RiskRegister",
            column="PostMitigatedLikelihood",
            row_index=23,
            row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        )
    )
    test_messeger._invalid_enum_value_failure_message(
        InvalidEnumValueFailure(
            table="RiskRegister",
            column="Proximity",
            row_index=24,
            row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        )
    )
    test_messeger._invalid_enum_value_failure_message(
        InvalidEnumValueFailure(
            table="Project Progress",
            column="Project Adjustment Request Status",
            row_index=2,
            row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        )
    )
    test_messeger._invalid_enum_value_failure_message(
        InvalidEnumValueFailure(
            table="Project Progress",
            column="Current Project Delivery Stage",
            row_index=2,
            row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        )
    )
    test_messeger._invalid_enum_value_failure_message(
        InvalidEnumValueFailure(
            table="Project Progress",
            column="Leading Factor of Delay",
            row_index=2,
            row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        )
    )
    test_messeger._invalid_enum_value_failure_message(
        InvalidEnumValueFailure(
            table="RiskRegister",
            column="RiskCategory",
            row_index=25,
            row_values=("Value 1", "TD-ABC-01", "Value 3", "Value 4"),
        )
    )


def test_non_nullable_messages_project_details():
    test_messeger = TFMessenger()
    failed_rows = pd.Series({"Start_Date": pd.to_datetime("2023-05-01 12:00:00")}, name=22)
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="Project Details", column="Locations", row_index=15, failed_row=None)
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="Project Details", column="Lat/Long", row_index=21, failed_row=None)
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="Project Progress", column="Start Date", row_index=1, failed_row=None)
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="Project Progress", column="Completion Date", row_index=4, failed_row=None)
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(
            table="Project Progress", column="Commentary on Status and RAG Ratings", row_index=2, failed_row=None
        )
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(
            table="Project Progress", column="Most Important Upcoming Comms Milestone", row_index=7, failed_row=None
        )
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(
            table="Project Progress",
            column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
            row_index=6,
            failed_row=None,
        )
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="Programme Progress", column="Answer", row_index=4, failed_row=None)
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(
            table="Project Progress", column="Current Project Delivery Stage", row_index=3, failed_row=None
        )
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(
            table="Outcome_Data", column="UnitofMeasurement", row_index=16, failed_row=failed_rows
        )
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="Outcome_Data", column="Amount", row_index=5, failed_row=failed_rows)
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(
            table="Outcome_Data", column="GeographyIndicator", row_index=5, failed_row=failed_rows
        )
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="Output_Data", column="Unit of Measurement", row_index=17, failed_row=None)
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="Output_Data", column="Amount", row_index=6, failed_row=None)
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="RiskRegister", column="Short Description", row_index=20, failed_row=None)
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="RiskRegister", column="Full Description", row_index=21, failed_row=None)
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="RiskRegister", column="Consequences", row_index=22, failed_row=None)
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="RiskRegister", column="Mitigatons", row_index=23, failed_row=None)
    )  # typo throughout code
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="RiskRegister", column="RiskOwnerRole", row_index=24, failed_row=None)
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="RiskRegister", column="RiskName", row_index=25, failed_row=None)
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="RiskRegister", column="RiskCategory", row_index=26, failed_row=None)
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="Funding", column="Spend for Reporting Period", row_index=7, failed_row=None)
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="Project Progress", column="Start Date", row_index=2, failed_row=None)
    )
    test_messeger._non_nullable_constraint_failure_message(
        NonNullableConstraintFailure(table="RiskRegister", column="Short Description", row_index=5, failed_row=None)
    )


def test_wrong_type_messages():
    test_messeger = TFMessenger()
    failed_rows = pd.Series({"Start_Date": pd.to_datetime("2023-05-01 12:00:00")}, name=22)
    test_messeger._wrong_type_failure_message(
        WrongTypeFailure(
            table="Project Progress",
            column="Start Date",
            expected_type=datetime,
            actual_type=str,
            row_index=22,
            failed_row=None,
        )
    )
    test_messeger._wrong_type_failure_message(
        WrongTypeFailure(
            table="Project Progress",
            column="Completion Date",
            expected_type=datetime,
            actual_type=str,
            row_index=22,
            failed_row=None,
        )
    )
    test_messeger._wrong_type_failure_message(
        WrongTypeFailure(
            table="Project Progress",
            column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
            expected_type=datetime,
            actual_type=str,
            row_index=22,
            failed_row=None,
        )
    )
    test_messeger._wrong_type_failure_message(
        WrongTypeFailure(
            table="Private Investments",
            column="Private Sector Funding Required",
            expected_type=float,
            actual_type=str,
            row_index=22,
            failed_row=None,
        )
    )
    test_messeger._wrong_type_failure_message(
        WrongTypeFailure(
            table="Private Investments",
            column="Private Sector Funding Secured",
            expected_type=float,
            actual_type=str,
            row_index=22,
            failed_row=None,
        )
    )
    test_messeger._wrong_type_failure_message(
        WrongTypeFailure(
            table="Funding",
            column="Spend for Reporting Period",
            expected_type=float,
            actual_type=str,
            row_index=22,
            failed_row=None,
        )
    )
    test_messeger._wrong_type_failure_message(
        WrongTypeFailure(
            table="Output_Data",
            column="Amount",
            expected_type=float,
            actual_type=str,
            row_index=22,
            failed_row=None,
        )
    )
    test_messeger._wrong_type_failure_message(
        WrongTypeFailure(
            table="Outcome_Data",
            column="Amount",
            expected_type=float,
            actual_type=str,
            row_index=22,
            failed_row=failed_rows,
        )
    )
    test_messeger._wrong_type_failure_message(
        WrongTypeFailure(
            table="Outcome_Data",
            column="Amount",
            expected_type=float,
            actual_type=object,
            row_index=22,
            failed_row=failed_rows,
        )
    )


def test_enum_failure_with_footfall_geography_indicator_wrong():
    test_messeger = TFMessenger()
    failure = InvalidEnumValueFailure(
        table="Outcome_Data",
        column="GeographyIndicator",
        row_index=60,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4", "Year-on-year % change in monthly footfall"),
    )

    assert test_messeger._invalid_enum_value_failure_message(failure) == Message(
        "Outcomes",
        "Footfall Indicator",
        ("C65",),
        "You’ve entered your own content, instead of selecting from the dropdown list "
        "provided. Select an option from the dropdown list.",
        "InvalidEnumValueFailure",
    )


def test_non_unique_composite_key_messages():
    test_messeger = TFMessenger()
    test_messeger._non_unique_composite_key_failure_message(
        NonUniqueCompositeKeyFailure(
            table="Funding",
            column=["Project ID", "Funding Source Name", "Funding Source Type", "Secured", "Start_Date", "End_Date"],
            row=[
                "HS-GRA-02",
                "Norfolk County Council",
                "Local Authority",
                "Yes",
                "2021-04-01 00:00:00",
                "2021-09-30 00:00:00",
            ],
            row_index=78,
        )
    )
    test_messeger._non_unique_composite_key_failure_message(
        NonUniqueCompositeKeyFailure(
            table="Output_Data",
            column=["Project ID", "Output", "Start_Date", "End_Date", "Unit of Measurement", "Actual/Forecast"],
            row=[
                "HS-GRA-02",
                "Total length of new cycle ways",
                "2020-04-01 00:00:00",
                "2020-09-30 00:00:00",
                "Km of cycle way",
                "Actual",
            ],
            row_index=82,
        )
    )
    test_messeger._non_unique_composite_key_failure_message(
        NonUniqueCompositeKeyFailure(
            table="Outcome_Data",
            column=["Project ID", "Outcome", "Start_Date", "End_Date", "GeographyIndicator"],
            row=[
                "HS-GRA-03",
                "Road traffic flows in corridors of interest (for road schemes)",
                "2020-04-01 00:00:00",
                "Travel corridor",
            ],
            row_index=1,
        )
    )
    test_messeger._non_unique_composite_key_failure_message(
        NonUniqueCompositeKeyFailure(
            table="RiskRegister",
            column=["Programme ID", "Project ID", "RiskName"],
            row=["HS-GRA", pd.NA, "Delivery Timeframe"],
            row_index=1,
        )
    )
    test_messeger._non_unique_composite_key_failure_message(
        NonUniqueCompositeKeyFailure(
            table="RiskRegister",
            column=["Programme ID", "Project ID", "RiskName"],
            row=[pd.NA, "HS-GRA-01", "Project Delivery"],
            row_index=23,
        )
    )

    with pytest.raises(ValueError):
        test_messeger._non_unique_composite_key_failure_message(
            NonUniqueCompositeKeyFailure(
                table="Project Progress",
                column=["Programme ID", "Project ID", "RiskName"],
                row=[pd.NA, "HS-GRA-01", "Project Delivery"],
                row_index=7,
            )
        )


def test_authorised_submission():
    test_messeger = TFMessenger()
    test_messeger._unauthorised_submission_failure(
        UnauthorisedSubmissionFailure(
            value_descriptor="Place Name", entered_value="Newark", expected_values=("Heanor",)
        )
    )
    test_messeger._unauthorised_submission_failure(
        UnauthorisedSubmissionFailure(value_descriptor="Fund Type", entered_value="TD", expected_values=("HS",))
    )


def test_generic_failure():
    test_messeger = TFMessenger()

    message = test_messeger._generic_failure(
        GenericFailure(
            table="Project Details",
            section="A Section",
            cell_index="C1",
            message="A message",
        )
    )

    assert message == Message(
        sheet="Project Admin",
        section="A Section",
        cell_indexes=("C1",),
        description="A message",
        error_type="GenericFailure",
    )


def test_generic_failure_when_column_is_none():
    test_messeger = TFMessenger()

    with pytest.raises(ValueError):
        test_messeger._generic_failure(
            GenericFailure(
                table="Project Details",
                section="A Section",
                cell_index=None,
                message="A message",
                column=None,
                row_index=None,
            )
        )


def test_failures_to_messages():
    failure1 = InvalidEnumValueFailure(
        table="Project Details",
        column="Single or Multiple Locations",
        row_index=1,
        row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
    )
    failure2 = NonNullableConstraintFailure(table="Project Details", column="Lat/Long", row_index=1, failed_row=None)
    failure3 = WrongTypeFailure(
        table="Project Progress",
        column="Date of Most Important Upcoming Comms Milestone (e.g. Dec-22)",
        expected_type=datetime,
        actual_type=str,
        row_index=22,
        failed_row=None,
    )
    failure4 = NonUniqueCompositeKeyFailure(
        table="RiskRegister",
        column=["Project ID", "RiskName"],
        row=[pd.NA, "HS-GRA-01", "Project Delivery"],
        row_index=23,
    )
    failure5 = NonUniqueCompositeKeyFailure(
        table="RiskRegister",
        column=["Project ID", "RiskName"],
        row=[pd.NA, "HS-GRA-01", "Project Delivery"],
        row_index=25,
    )  # intentional duplicate message, should only show up as a single message in the assertion

    failures = [failure1, failure2, failure3, failure4, failure5]
    test_messenger = TFMessenger()
    output = failures_to_messages(failures, test_messenger)

    assert isinstance(output, list)
    assert all(isinstance(message, Message) for message in output)
    assert len(output) == 4  # two messages should combine to make a single message


@pytest.mark.parametrize(
    "index_input, expected",
    [
        (("Place Details", "Question", 1), "C1"),
        (("Project Details", "Locations", 2), "H2 or K2"),
        (("Programme Progress", "Answer", 3), "D3"),
        (("Project Progress", "Delivery (RAG)", 4), "J4"),
        (("Funding Questions", "All Columns", 5), "E5"),
        (("Funding Comments", "Comment", 6), "C6 to E6"),
        (("Project Details", "Primary Intervention Theme", 27), "F27"),
    ],
)
def test_construct_cell_index(index_input, expected):
    test_messeger = TFMessenger()
    assert test_messeger._construct_cell_index(*index_input) == expected


def test_failures_to_message_with_outcomes_column_amount():
    test_messger = TFMessenger()

    failed_rows1 = pd.Series({"Start_Date": pd.to_datetime("2023-05-01 12:00:00")}, name=60)
    failed_rows2 = pd.Series({"Start_Date": pd.to_datetime("2023-06-01 12:00:00")}, name=23)
    failure1 = NonNullableConstraintFailure(
        table="Outcome_Data",
        column="Amount",
        row_index=60,
        failed_row=failed_rows1,
    )
    failure2 = WrongTypeFailure(
        table="Outcome_Data",
        column="Amount",
        expected_type=float,
        actual_type=str,
        row_index=23,
        failed_row=failed_rows2,
    )

    assert test_messger.to_message(failure1) == Message(
        "Outcomes",
        "Outcome Indicators (excluding footfall) / Footfall Indicator",
        ("E75",),
        "The cell is blank but is required. Enter a value, even if it’s zero.",
        "NonNullableConstraintFailure",
    )
    assert test_messger.to_message(failure2) == Message(
        "Outcomes",
        "Outcome Indicators (excluding footfall) and Footfall Indicator",
        ("I23",),
        "You entered text instead of a number. Remove any units of measurement and only use numbers, for example, 9.",
        "WrongTypeFailure",
    )


def test_failures_to_message_with_outcomes_column_without_failed_row():
    test_messger = TFMessenger()

    failure1 = WrongTypeFailure(
        table="Outcome_Data",
        column="Amount",
        expected_type=float,
        actual_type=str,
        row_index=23,
        failed_row=None,
    )

    # message needs to have an index, which does not exist when failed_row is None
    with pytest.raises(ValueError):
        test_messger.to_message(failure1)

    failure2 = NonNullableConstraintFailure(
        table="Outcome_Data",
        column="Amount",
        row_index=60,
        failed_row=None,
    )

    # message needs to have an index, which does not exist when failed_row is None
    with pytest.raises(ValueError):
        test_messger.to_message(failure2)


def test_failures_to_message_with_duplicated_errors():
    test_messger = TFMessenger()
    failed_row1 = pd.Series({"Start_Date": pd.to_datetime("2023-05-01 12:00:00")}, name=60)
    failed_row2 = pd.Series({"Start_Date": pd.to_datetime("2023-06-01 12:00:00")}, name=60)
    errors = [
        NonNullableConstraintFailure(
            table="Outcome_Data",
            column="Outcome",
            row_index=22,
            failed_row=failed_row1,
        ),
        NonNullableConstraintFailure(
            table="Outcome_Data",
            column="Outcome",
            row_index=22,
            failed_row=failed_row1,
        ),
        NonNullableConstraintFailure(
            table="Outcome_Data",
            column="Outcome",
            row_index=23,
            failed_row=failed_row1,
        ),
        NonNullableConstraintFailure(
            table="Outcome_Data",
            column="Amount",
            row_index=60,
            failed_row=failed_row1,
        ),
        NonNullableConstraintFailure(
            table="Outcome_Data",
            column="Amount",
            row_index=60,
            failed_row=failed_row2,
        ),
    ]

    filtered_errors = failures_to_messages(errors, test_messger)

    assert filtered_errors == [
        Message(
            "Outcomes",
            "Outcome Indicators (excluding footfall) / Footfall Indicator",
            ("B22", "B23"),
            "The cell is blank but is required.",
            "NonNullableConstraintFailure",
        ),
        Message(
            "Outcomes",
            "Outcome Indicators (excluding footfall) / Footfall Indicator",
            ("E75", "F75"),
            "The cell is blank but is required. Enter a value, even if it’s zero.",
            "NonNullableConstraintFailure",
        ),
    ]


def test_tf_messaging_to_message():
    test_messger = TFMessenger()

    assert test_messger.to_message(
        InvalidEnumValueFailure(
            table="Project Progress",
            column="Delivery (RAG)",
            row_index=2,
            row_values=("Value 1", "Value 2", "Value 3", "Value 4"),
        )
    ) == Message(
        sheet="Programme Progress",
        section="Projects Progress Summary",
        cell_indexes=("J2",),
        description=(
            "You’ve entered your own content, instead of selecting from the dropdown list provided. "
            "Select an option from the dropdown list."
        ),
        error_type="InvalidEnumValueFailure",
    )
    assert test_messger.to_message(
        NonNullableConstraintFailure(
            table="Project Progress", column="Current Project Delivery Stage", row_index=3, failed_row=None
        )
    ) == Message(
        sheet="Programme Progress",
        section="Projects Progress Summary",
        cell_indexes=("F3",),
        description="The cell is blank but is required.",
        error_type="NonNullableConstraintFailure",
    )
    assert test_messger.to_message(
        WrongTypeFailure(
            table="Project Progress",
            column="Start Date",
            expected_type=datetime,
            actual_type=str,
            row_index=22,
            failed_row=None,
        )
    ) == Message(
        sheet="Programme Progress",
        section="Projects Progress Summary",
        cell_indexes=("D22",),
        description=(
            "You entered text instead of a date. Check the cell is formatted as a date, for example, Dec-22 or Jun-23"
        ),
        error_type="WrongTypeFailure",
    )
    assert test_messger.to_message(
        InvalidEnumValueFailure(
            table="Outcome_Data",
            column="GeographyIndicator",
            row_index=60,
            row_values=("Value 1", "Value 2", "Value 3", "Value 4", "Year-on-year % change in monthly footfall"),
        )
    ) == Message(
        sheet="Outcomes",
        section="Footfall Indicator",
        cell_indexes=("C65",),
        description=(
            "You’ve entered your own content, instead of selecting from the dropdown list provided. "
            "Select an option from the dropdown list."
        ),
        error_type="InvalidEnumValueFailure",
    )
    assert test_messger.to_message(
        NonUniqueCompositeKeyFailure(
            table="Outcome_Data",
            column=["Project ID", "Outcome", "Start_Date", "End_Date", "GeographyIndicator"],
            row=[
                "HS-WRC-01",
                "Year on Year monthly % change in footfall",
                "2020-04-01 00:00:00",
                "2020-09-30 00:00:00",
                "Travel corridor",
            ],
            row_index=92,
        )
    ) == Message(
        sheet="Outcomes",
        section="Footfall Indicator",
        cell_indexes=("B92", "E92"),
        description="You entered duplicate data. Remove or replace the duplicate data.",
        error_type="NonUniqueCompositeKeyFailure",
    )
    assert test_messger.to_message(
        NonUniqueCompositeKeyFailure(
            table="Output_Data",
            column=["Project ID", "Output", "Start_Date", "End_Date", "Unit of Measurement", "Actual/Forecast"],
            row=[
                "HS-GRA-02",
                "Total length of new cycle ways",
                "2020-04-01 00:00:00",
                "2020-09-30 00:00:00",
                "Km of cycle way",
                "Actual",
            ],
            row_index=82,
        )
    ) == Message(
        sheet="Project Outputs",
        section="Project Outputs - Project 2",
        cell_indexes=("C82", "D82"),
        description="You entered duplicate data. Remove or replace the duplicate data.",
        error_type="NonUniqueCompositeKeyFailure",
    )
    assert test_messger.to_message(
        UnauthorisedSubmissionFailure(value_descriptor="Fund Type", entered_value="TD", expected_values=("HS",))
    ) == Message(
        sheet=None,
        section=None,
        cell_indexes=None,
        description="You’re not authorised to submit for TD. You can only submit for HS.",
        error_type="UnauthorisedSubmissionFailure",
    )
    assert test_messger.to_message(
        GenericFailure(
            table="Output_Data",
            section="A Section",
            cell_index="C1",
            message="A message",
        )
    ) == Message(
        sheet="Project Outputs",
        section="A Section",
        cell_indexes=("C1",),
        description="A message",
        error_type="GenericFailure",
    )


def test_get_cell_indexes_for_outcomes():
    test_messenger = TFMessenger()

    failed_row1 = pd.Series({"Start_Date": pd.to_datetime("2024-05-01 12:00:00")}, name=60)
    failed_row2 = pd.Series({"Start_Date": pd.to_datetime("2022-05-01 12:00:00")}, name=60)
    failed_row3 = pd.Series({"Start_Date": pd.to_datetime("2022-03-01 12:00:00")}, name=22)
    failed_row4 = pd.Series({"Start_Date": pd.to_datetime("2021-12-01 12:00:00")}, name=23)

    cell1 = test_messenger._get_cell_indexes_for_outcomes(failed_row1)
    cell2 = test_messenger._get_cell_indexes_for_outcomes(failed_row2)
    cell3 = test_messenger._get_cell_indexes_for_outcomes(failed_row3)
    cell4 = test_messenger._get_cell_indexes_for_outcomes(failed_row4)

    assert cell1 == "E80"
    assert cell2 == "E70"
    assert cell3 == "G22"
    assert cell4 == "G23"


def test_get_cell_indexes_for_outcomes_throws_exception():
    test_messenger = TFMessenger()

    failed_row = pd.Series({"Start_Date": pd.to_datetime("2024-05-01 12:00:00")}, name=None)

    with pytest.raises(TypeError):
        test_messenger._get_cell_indexes_for_outcomes(failed_row)


def test_get_uk_financial_year_start():
    # Test case where start_date is in the same financial year
    start_date_1 = pd.to_datetime("2023-05-01 12:00:00")
    result_1 = TFMessenger._get_uk_financial_year_start(start_date_1)
    assert result_1 == 2023

    # Test case where start_date is in the previous financial year
    start_date_2 = pd.to_datetime("2022-10-01 12:00:00")
    result_2 = TFMessenger._get_uk_financial_year_start(start_date_2)
    assert result_2 == 2022

    # Test case where start_date is exactly on the financial year start
    start_date_3 = pd.to_datetime("2023-04-01 00:00:00")
    result_3 = TFMessenger._get_uk_financial_year_start(start_date_3)
    assert result_3 == 2023

    # Test case where start_date is before the financial year start
    start_date_4 = pd.to_datetime("2023-03-01 00:00:00")
    result_4 = TFMessenger._get_uk_financial_year_start(start_date_4)
    assert result_4 == 2022
