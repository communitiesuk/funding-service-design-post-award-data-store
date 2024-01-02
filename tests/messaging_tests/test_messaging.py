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
from core.validation.failures import ValidationFailureBase
from core.validation.failures.user import GenericFailure, PreTransFormationFailure


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
        Message("Project Admin", "Project Details", "A1", "You left cells blank.", "GenericFailure"),
        Message("Project Admin", "Project Details", "A2", "You left cells blank.", "GenericFailure"),
        # B - combine these
        Message("Project Admin", "Programme Details", "D4", "You left cells blank.", "GenericFailure"),
        Message(
            "Project Admin",
            "Programme Details",
            "D4, D5, D7",
            "You left cells blank.",
            "GenericFailure",
        ),
        # C - do not combine these due to different sections
        Message("Risk Register", "Project Risks - Project 1", "G24", "Select from the dropdown.", "WrongInputFailure"),
        Message("Risk Register", "Project Risks - Project 2", "G43", "Select from the dropdown.", "WrongInputFailure"),
        # D - do not combine these due to different descriptions
        Message("Outcomes", "Programme-level Outcomes", "E5", "You left cells blank.", "WrongInputFailure"),
        Message("Outcomes", "Programme-level Outcomes", "E7", "Select from the dropdown.", "WrongInputFailure"),
    ]

    grouped = group_validation_messages(data)

    assert grouped == [
        Message("Project Admin", "Project Details", "A1, A2", "You left cells blank.", "GenericFailure"),
        Message(
            "Project Admin",
            "Programme Details",
            "D4, D4, D5, D7",
            "You left cells blank.",
            "GenericFailure",
        ),
        Message("Risk Register", "Project Risks - Project 1", "G24", "Select from the dropdown.", "WrongInputFailure"),
        Message("Risk Register", "Project Risks - Project 2", "G43", "Select from the dropdown.", "WrongInputFailure"),
        Message("Outcomes", "Programme-level Outcomes", "E5", "You left cells blank.", "WrongInputFailure"),
        Message("Outcomes", "Programme-level Outcomes", "E7", "Select from the dropdown.", "WrongInputFailure"),
    ]


def test_remove_errors_already_caught_by_null_failure():
    errors = [
        Message("Tab 1", "Sheet 1", "C7", "The cell is blank but is required.", "NonNullableConstraintFailure"),
        Message(
            "Tab 1",
            "Sheet 1",
            "C8",
            "The cell is blank but is required. Enter a value, even if it’s zero.",
            "NonNullableConstraintFailure",
        ),
        Message("Tab 1", "Sheet 1", "C7", "Some other message", "NonUniqueCompositeKeyFailure"),
    ]

    errors = remove_errors_already_caught_by_null_failure(errors)

    assert errors == [
        Message("Tab 1", "Sheet 1", "C7", "The cell is blank but is required.", "NonNullableConstraintFailure"),
        Message(
            "Tab 1",
            "Sheet 1",
            "C8",
            "The cell is blank but is required. Enter a value, even if it’s zero.",
            "NonNullableConstraintFailure",
        ),
    ]


def test_remove_errors_already_caught_by_null_failure_complex():
    errors = [
        Message("Tab 1", "Sheet 1", "C7, C8, C9", "The cell is blank but is required.", "NonNullableConstraintFailure"),
        Message("Tab 1", "Sheet 1", "C7", "Some other message", "SomeOtherInputFailure"),
    ]

    errors = remove_errors_already_caught_by_null_failure(errors)

    assert errors == [
        Message("Tab 1", "Sheet 1", "C7, C8, C9", "The cell is blank but is required.", "NonNullableConstraintFailure")
    ]


def test_remove_errors_already_caught_by_null_failure_risks():
    errors = [
        Message(
            "Tab 1",
            "Programme / Project Risks",
            "C12, C13, C17",
            "The cell is blank but is required.",
            "GenericFailure",
        ),
        Message("Tab 1", "Programme Risks", "C12", "Some other message", "GenericFailure"),
        Message("Tab 1", "Project Risks - Project 1", "C13", "Some other message", "SomeOtherInputFailure"),
        Message("Tab 1", "Project Risks - Project 2", "C17", "Some other message", "SomeOtherInputFailure"),
        Message("Tab 1", "Project Risks - Project 2", "C19", "Some other message", "SomeOtherInputFailure"),
    ]

    errors = remove_errors_already_caught_by_null_failure(errors)

    assert errors == [
        Message(
            "Tab 1",
            "Programme / Project Risks",
            "C12, C13, C17",
            "The cell is blank but is required.",
            "GenericFailure",
        ),
        Message("Tab 1", "Project Risks - Project 2", "C19", "Some other message", "SomeOtherInputFailure"),
    ]


def test_messaging_class_factory():
    messenger = messaging_class_factory("Towns Fund")

    assert isinstance(messenger, TFMessenger)


def test_compare_Messages():
    # equal comparison
    assert Message("Tab A", "Section A", "A1", "Some message", "SomeInputFailure") == Message(
        "Tab A", "Section A", "A1", "Some message", "SomeInputFailure"
    )

    # compare sheet
    assert Message("Tab A", "Section B", "A2", "Some message", "SomeInputFailure") < Message(
        "Tab B", "Section A", "A1", "Some message", "SomeInputFailure"
    )

    # compare section
    assert Message("Tab A", "Section A", "A2", "Some message", "SomeInputFailure") < Message(
        "Tab A", "Section B", "A1", "Some message", "SomeInputFailure"
    )

    # compare cell
    assert Message("Tab A", "Section A", "A1", "Some message", "SomeInputFailure") < Message(
        "Tab A", "Section A", "A2", "Some message", "SomeInputFailure"
    )

    # compare message
    assert Message("Tab A", "Section A", "A1", "Some message about something", "SomeInputFailure") < Message(
        "Tab A", "Section A", "A1", "Some message because something", "SomeInputFailure"
    )


def test_sort_Messages():
    sorted_messages = sorted(
        [
            Message("Tab D", "Section A", "A1", "Some message", "SomeInputFailure"),
            Message("Tab A", "Section A", "A1", "Some message", "SomeInputFailure"),
            Message("Tab C", "Section A", "A1", "A message", "SomeInputFailure"),
            Message("Tab D", "Section A", "A1", "Some message", "SomeInputFailure"),
            Message("Tab B", "Section A", "A2", "Some message", "SomeInputFailure"),
            Message("Tab C", "Section A", "A1", "b message", "SomeInputFailure"),
            Message("Tab B", "Section A", "A1", "Some message", "SomeInputFailure"),
            Message("Tab A", "Section B", "A1", "Some message", "SomeInputFailure"),
        ]
    )

    assert sorted_messages == [
        Message("Tab A", "Section A", "A1", "Some message", "SomeInputFailure"),
        Message("Tab A", "Section B", "A1", "Some message", "SomeInputFailure"),
        Message("Tab B", "Section A", "A1", "Some message", "SomeInputFailure"),
        Message("Tab B", "Section A", "A2", "Some message", "SomeInputFailure"),
        Message("Tab C", "Section A", "A1", "A message", "SomeInputFailure"),
        Message("Tab C", "Section A", "A1", "b message", "SomeInputFailure"),
        Message("Tab D", "Section A", "A1", "Some message", "SomeInputFailure"),
        Message("Tab D", "Section A", "A1", "Some message", "SomeInputFailure"),
    ]


def test_combine_Message():
    message_1 = Message("Tab 1", "Project Risks - Project 1", "C13", "Some other message", "SomeInputFailure")
    message_2 = Message("Tab 1", "Project Risks - Project 1", "C17", "Some other message", "SomeInputFailure")

    message_1.combine(message_2)

    assert message_1 == Message(
        "Tab 1", "Project Risks - Project 1", "C13, C17", "Some other message", "SomeInputFailure"
    )


def test_failures_to_message(test_messenger):
    messages_to_return = [
        Message("Tab A", "Section A", "A1", "Some message", "SomeInputFailure"),
        Message("Tab B", "Section A", "A1", "Some message", "SomeInputFailure"),
        Message("Tab C", "Section A", "A1", "Some message", "SomeInputFailure"),
    ]

    error_messages = failures_to_messages([GenericFailure("_", "_", "_", "_")] * 3, test_messenger(messages_to_return))

    assert error_messages == {
        "validation_errors": [
            {
                "cell_index": "A1",
                "description": "Some message",
                "error_type": "SomeInputFailure",
                "section": "Section A",
                "sheet": "Tab A",
            },
            {
                "cell_index": "A1",
                "description": "Some message",
                "error_type": "SomeInputFailure",
                "section": "Section A",
                "sheet": "Tab B",
            },
            {
                "cell_index": "A1",
                "description": "Some message",
                "error_type": "SomeInputFailure",
                "section": "Section A",
                "sheet": "Tab C",
            },
        ]
    }


def test_failures_to_message_pre_transformation(test_messenger):
    messages_to_return = [
        Message("_", "_", "_", "Pre-transformation error message", "PreTransFormationFailure"),
    ]

    error_messages = failures_to_messages([PreTransFormationFailure()], test_messenger(messages_to_return))

    assert error_messages == {"pre_transformation_errors": ["Pre-transformation error message"]}


def test_failures_to_message_remove(test_messenger):
    messages_to_return = [
        Message("Tab B", "Section A", "A1, A2", "The cell is blank but is required.", "NonNullableConstraintFailure"),
        Message("Tab B", "Section A", "A1", "removed message", "SomeInputFailure"),
        Message("Tab B", "Section A", "A2", "removed message", "SomeInputFailure"),
        Message("Tab B", "Section A", "A3", "not removed message", "SomeInputFailure"),
    ]

    error_messages = failures_to_messages([GenericFailure("_", "_", "_", "_")] * 4, test_messenger(messages_to_return))

    assert error_messages == {
        "validation_errors": [
            {
                "sheet": "Tab B",
                "section": "Section A",
                "cell_index": "A1, A2",
                "description": "The cell is blank but is required.",
                "error_type": "NonNullableConstraintFailure",
            },
            {
                "sheet": "Tab B",
                "section": "Section A",
                "cell_index": "A3",
                "description": "not removed message",
                "error_type": "SomeInputFailure",
            },
        ]
    }


def test_failures_to_message_group(test_messenger):
    messages_to_return = [
        Message("Tab A", "Section A", "A321", "grouped message", "SomeInputFailure"),
        Message("Tab A", "Section A", "A456", "grouped message", "SomeInputFailure"),
        Message("Tab A", "Section A", "A123", "grouped message", "SomeInputFailure"),
    ]

    error_messages = failures_to_messages([GenericFailure("_", "_", "_", "_")] * 3, test_messenger(messages_to_return))

    assert error_messages == {
        "validation_errors": [
            {
                "sheet": "Tab A",
                "section": "Section A",
                "cell_index": "A123, A321, A456",
                "description": "grouped message",
                "error_type": "SomeInputFailure",
            },
        ]
    }
