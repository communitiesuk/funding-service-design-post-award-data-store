from abc import ABC, abstractmethod


def validate_auth_args(func):
    """Validates that all args passed to the decorated function are tuples of strings.

    :param func: the decorated function
    :raises ValueError: if the args are invalid
    """

    def wrapper(*args):
        for arg in args:
            if isinstance(arg, AuthBase):
                continue  # don't validate self
            if not isinstance(arg, tuple):
                raise ValueError(f"Expected a tuple, but got {type(arg).__name__} in args: {args}")
            if not all(isinstance(item, str) for item in arg):
                raise ValueError(f"All elements in the tuple must be strings in args: {args}")
        return func(*args)

    return wrapper


class AuthBase(ABC):
    """Auth class ABC. Classes that inherit must implement a constructor, organisations and auth_dict methods."""

    @abstractmethod
    def __init__(self, *args):
        pass

    @abstractmethod
    def get_organisations(self) -> tuple[str, ...]:
        """Return organisations associated with this level of authorisation."""
        pass

    @abstractmethod
    def get_auth_dict(self) -> dict:
        """Return other details associated with this authorisation."""
        pass


class AuthMapping:
    """Encapsulates an email mapping dictionary. Allows lookup of an email address."""

    _auth_class: type[AuthBase]
    _mapping: dict[str, AuthBase]

    def __init__(self, auth_class: type[AuthBase], mapping: dict[str, tuple[tuple[str, ...], ...]]):
        """Instantiates an AuthMapping from an Auth class and a set of dictionary mappings.

        :param auth_class: the Auth class implementation that this AuthMapping will store
        :param mapping: a dictionary mapping emails to a set of auth details that are held within Auth objects
        """
        self._auth_class = auth_class
        # for each item in the dictionary, encapsulate the auth details values in an instance of the auth_class
        self._mapping = {email.lower(): auth_class(*auth_details) for email, auth_details in mapping.items()}

    def get_auth(self, email: str) -> AuthBase | None:
        """Get the authorisation information associated with the given email address.

        This lookup is case-insensitive.

        Lookup hierarchy:
        1. Full Email
        2. Email Domain

        :param email: email address
        :return: the associated Auth
        """
        domain = email.split("@")[1]
        # first match on full email, then try domain
        auth = self._mapping.get(email.lower()) or self._mapping.get(domain.lower())
        return auth


class ReadOnlyAuthMappings:
    """Read-only dictionary wrapper for storing authorisation mappings."""

    def __init__(self, fund_to_auth_mappings: dict[str, AuthMapping]):
        self._auth_mappings = fund_to_auth_mappings

    def get(self, fund: str) -> AuthMapping:
        """Retrieves the authentication mapping for a given fund.

        :param fund: A fund name.
        :return: The authentication mapping corresponding to the given fund.
        :raises ValueError: If the given fund is not found in the authentication mappings.
        """
        auth_mapping = self._auth_mappings.get(fund)
        if not auth_mapping:
            raise ValueError(f"Cannot find auth mapping for fund: {fund}")
        return auth_mapping


class TFAuth(AuthBase):
    """A Towns Fund Auth Class"""

    _local_authorities: tuple[str, ...]
    _place_names: tuple[str, ...]
    _fund_types: tuple[str, ...]

    @validate_auth_args
    def __init__(self, local_authorities: tuple[str, ...], place_names: tuple[str, ...], fund_types: tuple[str, ...]):
        """Initialises a TFAuth.

        Applies input validation to prevent downstream errors. This is to mitigate against the dangers of storing the
        Auth state in code, where it can be easily changed.

        :param local_authorities: a tuple of local authorities
        :param place_names: a tuple of places
        :param fund_types: a tuple of fund types
        """
        self._local_authorities = local_authorities
        self._place_names = place_names
        self._fund_types = fund_types

    def get_organisations(self) -> tuple[str, ...]:
        """Returns the local authorities for this TFAuth class.

        :return: a tuple local authorities.
        """
        return self._local_authorities

    def get_auth_dict(self) -> dict[str, tuple[str, ...]]:
        """Returns the auth dictionary for this TFAuth class.

        :return: a dictionary of place names and fund types.
        """
        return {"Place Names": self._place_names, "Fund Types": self._fund_types}
