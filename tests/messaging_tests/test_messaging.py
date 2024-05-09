import pytest

from core.messaging import MessengerBase
from core.messaging.messaging import (
    Message,
    failures_to_messages,
    group_validation_messages,
    messaging_class_factory,
    remove_errors_already_caught_by_null_failure,
)
from core.messaging.tf_messaging import TFMessenger
from core.validation.towns_fund.failures import ValidationFailureBase
from core.validation.towns_fund.failures.user import GenericFailure


@pytest.fixture(scope="module")
def test_messenger():
    class TestMessenger(MessengerBase):
        """Mock messenger class to be used in testing functions that require a messenger object"""

        def __init__(self, messages_to_return: list[Message]):
            """construct the object wih a set of dummy messages to return when to_message is called"""
            self.messages = messages_to_return
            self.count = 0

        def to_message(self, validation_failure: ValidationFailureBase):
            """returns next message in messages looping back to the start if the whole list has been returned"""
            message_to_return = self.messages[self.count % len(self.messages)]
            self.count += 1
            return message_to_return

    return TestMessenger


def test_group_validation_messages():
    data = [
        # A - combine these
        Message("Project Admin", "Project Details", ("A1",), "You left cells blank.", "GenericFailure"),
        Message("Project Admin", "Project Details", ("A2",), "You left cells blank.", "GenericFailure"),
        # B - combine these
        Message("Project Admin", "Programme Details", ("D4",), "You left cells blank.", "GenericFailure"),
        Message(
            "Project Admin",
            "Programme Details",
            ("D4", "D5", "D7"),
            "You left cells blank.",
            "GenericFailure",
        ),
        # C - do not combine these due to different sections
        Message(
            "Risk Register", "Project Risks - Project 1", ("G24",), "Select from the dropdown.", "WrongInputFailure"
        ),
        Message(
            "Risk Register", "Project Risks - Project 2", ("G43",), "Select from the dropdown.", "WrongInputFailure"
        ),
        # D - do not combine these due to different descriptions
        Message("Outcomes", "Programme-level Outcomes", ("E5",), "You left cells blank.", "WrongInputFailure"),
        Message("Outcomes", "Programme-level Outcomes", ("E7",), "Select from the dropdown.", "WrongInputFailure"),
    ]

    grouped = group_validation_messages(data)

    assert grouped == [
        Message("Project Admin", "Project Details", ("A1", "A2"), "You left cells blank.", "GenericFailure"),
        Message(
            "Project Admin",
            "Programme Details",
            ("D4", "D4", "D5", "D7"),
            "You left cells blank.",
            "GenericFailure",
        ),
        Message(
            "Risk Register", "Project Risks - Project 1", ("G24",), "Select from the dropdown.", "WrongInputFailure"
        ),
        Message(
            "Risk Register", "Project Risks - Project 2", ("G43",), "Select from the dropdown.", "WrongInputFailure"
        ),
        Message("Outcomes", "Programme-level Outcomes", ("E5",), "You left cells blank.", "WrongInputFailure"),
        Message("Outcomes", "Programme-level Outcomes", ("E7",), "Select from the dropdown.", "WrongInputFailure"),
    ]


def test_remove_errors_already_caught_by_null_failure():
    errors = [
        Message("Tab 1", "Sheet 1", ("C7",), "The cell is blank but is required.", "NonNullableConstraintFailure"),
        Message(
            "Tab 1",
            "Sheet 1",
            ("C8",),
            "The cell is blank but is required. Enter a value, even if it’s zero.",
            "NonNullableConstraintFailure",
        ),
        Message("Tab 1", "Sheet 1", ("C7",), "Some other message", "NonUniqueCompositeKeyFailure"),
    ]

    errors = remove_errors_already_caught_by_null_failure(errors)

    assert errors == [
        Message("Tab 1", "Sheet 1", ("C7",), "The cell is blank but is required.", "NonNullableConstraintFailure"),
        Message(
            "Tab 1",
            "Sheet 1",
            ("C8",),
            "The cell is blank but is required. Enter a value, even if it’s zero.",
            "NonNullableConstraintFailure",
        ),
    ]


def test_remove_errors_already_caught_by_null_failure_complex():
    errors = [
        Message(
            "Tab 1", "Sheet 1", ("C7", "C8", "C9"), "The cell is blank but is required.", "NonNullableConstraintFailure"
        ),
        Message("Tab 1", "Sheet 1", ("C7",), "Some other message", "SomeOtherInputFailure"),
    ]

    errors = remove_errors_already_caught_by_null_failure(errors)

    assert errors == [
        Message(
            "Tab 1", "Sheet 1", ("C7", "C8", "C9"), "The cell is blank but is required.", "NonNullableConstraintFailure"
        )
    ]


def test_remove_errors_already_caught_by_null_failure_risks():
    errors = [
        Message(
            "Tab 1",
            "Programme / Project Risks",
            ("C12", "C13", "C17"),
            "The cell is blank but is required.",
            "GenericFailure",
        ),
        Message("Tab 1", "Programme Risks", ("C12",), "Some other message", "GenericFailure"),
        Message("Tab 1", "Project Risks - Project 1", ("C13",), "Some other message", "SomeOtherInputFailure"),
        Message("Tab 1", "Project Risks - Project 2", ("C17",), "Some other message", "SomeOtherInputFailure"),
        Message("Tab 1", "Project Risks - Project 2", ("C19",), "Some other message", "SomeOtherInputFailure"),
    ]

    errors = remove_errors_already_caught_by_null_failure(errors)

    assert errors == [
        Message(
            "Tab 1",
            "Programme / Project Risks",
            ("C12", "C13", "C17"),
            "The cell is blank but is required.",
            "GenericFailure",
        ),
        Message("Tab 1", "Project Risks - Project 2", ("C19",), "Some other message", "SomeOtherInputFailure"),
    ]


def test_messaging_class_factory():
    messenger = messaging_class_factory("Towns Fund")

    assert isinstance(messenger, TFMessenger)


def test_compare_Messages():
    # equal comparison
    assert Message("Tab A", "Section A", ("A1",), "Some message", "SomeInputFailure") == Message(
        "Tab A", "Section A", ("A1",), "Some message", "SomeInputFailure"
    )

    # compare sheet
    assert Message("Tab A", "Section B", ("A2",), "Some message", "SomeInputFailure") < Message(
        "Tab B", "Section A", ("A1",), "Some message", "SomeInputFailure"
    )

    # compare section
    assert Message("Tab A", "Section A", ("A2",), "Some message", "SomeInputFailure") < Message(
        "Tab A", "Section B", ("A1",), "Some message", "SomeInputFailure"
    )

    # compare cell
    assert Message("Tab A", "Section A", ("A1",), "Some message", "SomeInputFailure") < Message(
        "Tab A", "Section A", ("A2",), "Some message", "SomeInputFailure"
    )

    # compare message
    assert Message("Tab A", "Section A", ("A1",), "Some message about something", "SomeInputFailure") < Message(
        "Tab A", "Section A", ("A1",), "Some message because something", "SomeInputFailure"
    )


def test_sort_Messages():
    sorted_messages = sorted(
        [
            Message("Tab D", "Section A", ("A1",), "Some message", "SomeInputFailure"),
            Message("Tab A", "Section A", ("A1",), "Some message", "SomeInputFailure"),
            Message("Tab C", "Section A", ("A1",), "A message", "SomeInputFailure"),
            Message("Tab D", "Section A", ("A1",), "Some message", "SomeInputFailure"),
            Message("Tab B", "Section A", ("A2",), "Some message", "SomeInputFailure"),
            Message("Tab C", "Section A", ("A1",), "b message", "SomeInputFailure"),
            Message("Tab B", "Section A", ("A1",), "Some message", "SomeInputFailure"),
            Message("Tab A", "Section B", ("A1",), "Some message", "SomeInputFailure"),
        ]
    )

    assert sorted_messages == [
        Message("Tab A", "Section A", ("A1",), "Some message", "SomeInputFailure"),
        Message("Tab A", "Section B", ("A1",), "Some message", "SomeInputFailure"),
        Message("Tab B", "Section A", ("A1",), "Some message", "SomeInputFailure"),
        Message("Tab B", "Section A", ("A2",), "Some message", "SomeInputFailure"),
        Message("Tab C", "Section A", ("A1",), "A message", "SomeInputFailure"),
        Message("Tab C", "Section A", ("A1",), "b message", "SomeInputFailure"),
        Message("Tab D", "Section A", ("A1",), "Some message", "SomeInputFailure"),
        Message("Tab D", "Section A", ("A1",), "Some message", "SomeInputFailure"),
    ]


def test_combine_Message():
    message_1 = Message("Tab 1", "Project Risks - Project 1", ("C13",), "Some other message", "SomeInputFailure")
    message_2 = Message("Tab 1", "Project Risks - Project 1", ("C17",), "Some other message", "SomeInputFailure")

    message_1.combine(message_2)

    assert message_1 == Message(
        "Tab 1", "Project Risks - Project 1", ("C13", "C17"), "Some other message", "SomeInputFailure"
    )


def test_failures_to_message(test_messenger):
    messages_to_return = [
        Message("Tab A", "Section A", ("A1",), "Some message", "SomeInputFailure"),
        Message("Tab B", "Section A", ("A1",), "Some message", "SomeInputFailure"),
        Message("Tab C", "Section A", ("A1",), "Some message", "SomeInputFailure"),
    ]

    error_messages = failures_to_messages([GenericFailure("_", "_", "_", "_")] * 3, test_messenger(messages_to_return))

    assert error_messages == [
        Message("Tab A", "Section A", ("A1",), "Some message", "SomeInputFailure"),
        Message("Tab B", "Section A", ("A1",), "Some message", "SomeInputFailure"),
        Message("Tab C", "Section A", ("A1",), "Some message", "SomeInputFailure"),
    ]


def test_failures_to_message_remove(test_messenger):
    messages_to_return = [
        Message(
            "Tab B", "Section A", ("A1", "A2"), "The cell is blank but is required.", "NonNullableConstraintFailure"
        ),
        Message("Tab B", "Section A", ("A1",), "removed message", "SomeInputFailure"),
        Message("Tab B", "Section A", ("A2",), "removed message", "SomeInputFailure"),
        Message("Tab B", "Section A", ("A3",), "not removed message", "SomeInputFailure"),
    ]

    error_messages = failures_to_messages([GenericFailure("_", "_", "_", "_")] * 4, test_messenger(messages_to_return))

    assert error_messages == [
        Message(
            "Tab B", "Section A", ("A1", "A2"), "The cell is blank but is required.", "NonNullableConstraintFailure"
        ),
        Message("Tab B", "Section A", ("A3",), "not removed message", "SomeInputFailure"),
    ]


def test_failures_to_message_group(test_messenger):
    messages_to_return = [
        Message("Tab A", "Section A", ("A321",), "grouped message", "SomeInputFailure"),
        Message("Tab A", "Section A", ("A456",), "grouped message", "SomeInputFailure"),
        Message("Tab A", "Section A", ("A123",), "grouped message", "SomeInputFailure"),
    ]

    error_messages = failures_to_messages([GenericFailure("_", "_", "_", "_")] * 3, test_messenger(messages_to_return))

    assert error_messages == [
        Message("Tab A", "Section A", ("A123", "A321", "A456"), "grouped message", "SomeInputFailure")
    ]


@pytest.mark.parametrize(
    "input_cell_indexes, expected_cell_indexes",
    (
        (("A1",), ("A1",)),
        (("B1", "A1"), ("A1", "B1")),  # Sorts by column correctly
        (("A2", "A1"), ("A1", "A2")),  # Sorts by row correctly
        (("A2", "B1", "A1"), ("A1", "A2", "B1")),  # Sorts both correctly
        (("A1", "B20", "B4", "A10"), ("A1", "A10", "B4", "B20")),  # Sorts row numbers numerically not lexicographically
        (("A1", "AA1", "Z1"), ("A1", "Z1", "AA1")),  # Sorts all 2-letter columns after all 1-letter columns
        (("A1", "AA1", "B"), ("A1", "B", "AA1")),  # Can handle column-only cell indexes
        (("B1", "B"), ("B", "B1")),  # Sorts column-only before column-with-row
        (
            ("B2", "A3 to B3", "A1"),
            ("A1", "A3 to B3", "B2"),
        ),  # Sorts column ranges based on the first part of the range
        (("B2", "A3 or B3", "A4"), ("A3 or B3", "A4", "B2")),  # Can handle "or" as well as "to"
    ),
)
def test_message_cell_indexes_sort_as_expected(input_cell_indexes, expected_cell_indexes):
    assert (
        Message("Tab A", "Section A", input_cell_indexes, "grouped message", "SomeInputFailure").cell_indexes
        == expected_cell_indexes
    )


def test_message_cell_indexes_remove_duplicates_automatically():
    assert Message("Tab A", "Section A", ("A1", "A1"), "grouped message", "SomeInputFailure").cell_indexes == ("A1",)


def test_combined_messages_removes_duplicates():
    m1 = Message("Tab A", "Section A", ("A1", "A2"), "grouped message", "SomeInputFailure")
    m2 = Message("Tab A", "Section A", ("A1", "A3"), "grouped message", "SomeInputFailure")

    m1.combine(m2)

    assert m1.cell_indexes == ("A1", "A2", "A3")


def test_combined_messages_errors_on_lowercase_cell_indexes():
    with pytest.raises(ValueError):
        assert Message("Tab A", "Section A", ("a1", "ab1", "Abc"), "grouped message", "SomeInputFailure")


def test_errors_if_initialising_with_none_cell_index():
    with pytest.raises(ValueError):
        Message("Tab A", "Section A", (None,), "grouped message", "SomeInputFailure")


def test_errors_if_combining_with_non_message():
    with pytest.raises(ValueError):
        Message("Tab A", "Section A", ("A1",), "grouped message", "SomeInputFailure").combine(1)


def test_errors_if_combining_with_no_cell_reference_message():
    with pytest.raises(ValueError):
        Message("Tab A", "Section A", ("A1",), "grouped message", "SomeInputFailure").combine(
            Message("Tab A", "Section A", None, "grouped message", "SomeInputFailure")
        )
