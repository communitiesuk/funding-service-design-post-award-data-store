from app.const import EMAIL_DOMAIN_TO_PLACE_NAMES


def get_local_authority_place_names(user_email: str) -> None | list[str]:
    """
    Get the local authority place names corresponding to a user's email domain.

    This function takes a user's email address and uses the domain part (after '@')
    to look up the corresponding place names the user can submit returns for.

    :param user_email: A string representing the user's email address.
    :return: An array of place names or None if none are found.
    """
    email_domain = user_email.split("@")[1]

    return EMAIL_DOMAIN_TO_PLACE_NAMES.get(email_domain)
