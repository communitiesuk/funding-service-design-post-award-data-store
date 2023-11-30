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


class TFAuth(AuthBase):
    """A Towns Fund Auth Class"""

    local_authorities: tuple[str, ...]
    place_names: tuple[str, ...]
    fund_types: tuple[str, ...]

    @validate_auth_args
    def __init__(self, local_authorities: tuple[str, ...], place_names: tuple[str, ...], fund_types: tuple[str, ...]):
        self.local_authorities = local_authorities
        self.place_names = place_names
        self.fund_types = fund_types

    def get_organisations(self) -> tuple[str, ...]:
        return self.local_authorities

    def get_auth_dict(self) -> dict:
        return {"Place Names": self.place_names, "Fund Types": self.fund_types}


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
        self._mapping = {email: auth_class(*auth_details) for email, auth_details in mapping.items()}

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


def _auth_class_factory(fund: str) -> type[AuthBase]:
    """Given a fund, returns the associated auth class.

    :param fund: Fund Name
    :return: associated Auth class
    :raises ValueError:
    """
    match fund:
        case "Towns Fund":
            return TFAuth
        case _:
            raise ValueError("Unknown Fund")


def build_auth_mapping(fund_name: str, mapping: dict[str, tuple[tuple[str, ...], ...]]) -> AuthMapping:
    """Given a fund and a set of email mappings, return an auth mapping object.

    :param fund_name: the fund associated with this mapping
    :param mapping: a mapping of email/domains -> (organisation, *other_auth_details)
    :return: an AuthMapping
    """
    auth_class: type[AuthBase] = _auth_class_factory(fund_name)
    auth_mapping = AuthMapping(auth_class, mapping)
    return auth_mapping
