from core.messaging import Message, MessengerBase
from core.messaging.tf_messaging import SharedMessages as msgs
from core.messaging.tf_messaging import TFMessenger
from core.validation.towns_fund.failures.user import UserValidationFailure


def group_validation_messages(validation_messages: list[Message]) -> list[Message]:
    """Groups validation messages by concatenating the cell indexes together on identical sheet, section description

    :param validation_messages: a list of message objects
    :return: grouped validation messages
    """
    grouped_dict: dict = {}
    for message in validation_messages:
        key = (
            message.sheet,
            message.section,
            message.description,
            message.error_type,
        )  # use sheet, section, description and error_type as the key
        if key in grouped_dict:
            grouped_dict[key].combine(message)  # combine cells with already existing message
        else:
            grouped_dict[key] = message

    grouped_messages = list(grouped_dict.values())
    return grouped_messages


def remove_errors_already_caught_by_null_failure(error_messages: list[Message]) -> list[Message]:
    """
    Removes errors from the list that have already been caught by null failures based on their sheet, and
    cell index, and keeps only those present in null_failures. Additionally, includes all null_failures and errors
    not present in null_failures or any part of the cell index is not already captured by a null failure.

    :param error_messages: List of error Messages.
    :return: Filtered list of errors, including all null_failures and errors not present in null_failures or any part
    of the cell index is not already captured by a null failure.
    """

    null_descriptions = [
        msgs.BLANK,
        msgs.BLANK_ZERO,
        msgs.BLANK_PSI,
        msgs.BLANK_UNIT_OF_MEASUREMENT,
    ]

    cells_covered_by_null_failures = [
        (message.sheet, cell_index)
        for message in error_messages
        if message.description in null_descriptions
        for cell_index in message.cell_indexes
    ]

    filtered_errors = [
        message
        for message in error_messages
        if not any(
            ((message.sheet, cell_index) in cells_covered_by_null_failures) for cell_index in message.cell_indexes
        )
        or message.description in null_descriptions
    ]

    return filtered_errors


def failures_to_messages(validation_failures: list[UserValidationFailure], messenger: MessengerBase) -> list[Message]:
    """Serialises failures into messages, removing any duplicates, and groups them by sheet and section.
    :param validation_failures: validation failure objects
    :param messenger: messenger object for the relevant fund type

    :return: validation failure messages grouped by sheet and section
    """
    # filter and convert to error messages
    error_messages = [messenger.to_message(failure) for failure in validation_failures]
    # remove duplicates resulting from melted rows where we are unable to remove duplicates at time of validation
    error_messages = sorted(list(set(error_messages)))
    # filter out composite key errors that are already picked up by null failures
    error_messages = remove_errors_already_caught_by_null_failure(error_messages)
    # group cells by sheet, section and desc
    error_messages = group_validation_messages(error_messages)
    return error_messages


def messaging_class_factory(fund: str) -> MessengerBase:
    """Given a fund, returns the associated messaging class.
    :param fund: Fund Name
    :return: associated messaging class
    :raises ValueError:
    """
    match fund:
        case "Towns Fund":
            return TFMessenger()
        case _:
            raise ValueError("Unknown Fund")
