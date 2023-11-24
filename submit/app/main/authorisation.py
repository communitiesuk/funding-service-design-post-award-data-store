from flask import abort, current_app, g


def check_authorised() -> tuple[tuple[str], dict[str]]:
    """Checks that the user is authorized to submit.

    Returns any LAs, places, and fund types that the user is authorized to submit for, otherwise aborts and redirects
    to 401 (unauthorised) page.

    :return: the LAs as a tuple, and a dictionary with both the place_names and fund_types
    """
    local_authorities, place_names, fund_types = get_local_authority_and_place_names_and_fund_types(g.user.email)
    if local_authorities is None or place_names is None or fund_types is None:
        current_app.logger.error(
            f"User: {g.user.email} has not been assigned any local authorities and/or places and/or fund types"
        )
        abort(401)  # unauthorized
    current_app.logger.info(
        f"User: {g.user.email} from {', '.join(local_authorities)} is authorised for places: {', '.join(place_names)}"
        f"and fund types: {', '.join(fund_types)}"
    )
    return local_authorities, {"Place Names": place_names, "Fund Types": fund_types}


def get_local_authority_and_place_names_and_fund_types(
    user_email: str,
) -> tuple[tuple[str] | None, tuple[str] | None, tuple[str] | None]:
    """
    Get the local authority, place names, and fund types corresponding to a user's email.

    This function takes a user's email address and uses the domain part (after '@')
    to look up the corresponding place names and fund types the user can submit returns for.
    If the domain is not present in the look-up, the user may be a private contractor
    who cannot be verified by the domain alone, and so a look-up of the entire
    e-mail address is performed. Where this is not found, a tuple containing None
    will be returned.

    :param user_email: A string representing the user's email address.
    :return: A tuple of local authorities, place names, and fund types under their remit.
    """
    email_mapping = current_app.config["EMAIL_TO_LA_AND_PLACE_NAMES_AND_FUND_TYPES"]
    email_domain = user_email.split("@")[1]
    # if the domain is not present in the lookup, we will check with the whole e-mail
    la_and_place_names_and_fund_types = email_mapping.get(email_domain.lower()) or email_mapping.get(
        user_email.lower(), (None, None, None)
    )

    return la_and_place_names_and_fund_types
