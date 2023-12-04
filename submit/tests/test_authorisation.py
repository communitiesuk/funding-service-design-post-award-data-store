import pytest

from app.main.authorisation import (
    AuthBase,
    AuthMapping,
    TFAuth,
    _auth_class_factory,
    build_auth_mapping,
    validate_auth_args,
)


@pytest.fixture
def mock_mapping():
    mapping = {
        "wizard1@hogwarts.magic.uk": (("Hogwarts",), ("Professor Albus Dumbledore",)),
        "hogwarts.magic.uk": (("Hogwarts",), ("Harry Potter", "Ron Weasley")),
        "wizardWITHCAPSINMAPPING@charingcross.magic.uk": (("Diagon Alley",), ("Snape",)),
    }
    return mapping


@pytest.fixture
def mock_auth_class():
    class WizardAuth(AuthBase):
        def __init__(self, schools, wizards):
            self.schools = schools
            self.wizards = wizards

        def get_organisations(self) -> tuple[str, ...]:
            return self.schools

        def get_auth_dict(self) -> dict:
            return {"Wizards": self.wizards}

    return WizardAuth


@pytest.fixture
def mock_auth_mapping(mock_auth_class, mock_mapping):
    return AuthMapping(mock_auth_class, mock_mapping)


def test_auth_mapping_email_match(mock_auth_mapping, mock_auth_class):
    """
    GIVEN a valid AuthMapping object
    WHEN an email address is passed to it that DOES match an exact email AND a domain
    THEN it should return the correct mapping for that exact email
    """
    auth = mock_auth_mapping.get_auth("wizard1@hogwarts.magic.uk")

    assert isinstance(auth, mock_auth_class)
    assert auth.get_organisations() == ("Hogwarts",)
    assert auth.get_auth_dict() == {"Wizards": ("Professor Albus Dumbledore",)}


def test_auth_mapping_email_match_case_insensitive(mock_auth_mapping, mock_auth_class):
    """
    GIVEN a valid AuthMapping object
    WHEN an email address is passed to it that DOES match an email by content but NOT case
    THEN it should return the mapping for that email regardless of case
    """
    auth = mock_auth_mapping.get_auth("WIZARD1@hogwarts.magic.uk")

    assert isinstance(auth, mock_auth_class)
    assert auth.get_organisations() == ("Hogwarts",)
    assert auth.get_auth_dict() == {"Wizards": ("Professor Albus Dumbledore",)}


def test_auth_mapping_email_match_case_insensitive_from_mapping(mock_auth_mapping, mock_auth_class):
    """
    GIVEN a valid AuthMapping object
    WHEN an email address is passed to it that contained caps in the original mapping
    THEN it should return the mapping for that email regardless of case
    """
    auth = mock_auth_mapping.get_auth("wizardwithcapsinmapping@charingcross.magic.uk")

    assert isinstance(auth, mock_auth_class)
    assert auth.get_organisations() == ("Diagon Alley",)
    assert auth.get_auth_dict() == {"Wizards": ("Snape",)}


def test_auth_mapping_domain_match(mock_auth_mapping, mock_auth_class):
    """
    GIVEN a valid AuthMapping object
    WHEN an email address is passed to it that DOES NOT match an exact email BUT DOES match a domain
    THEN it should return the correct mapping for that domain
    """
    auth = mock_auth_mapping.get_auth("anotherwizard@hogwarts.magic.uk")

    assert isinstance(auth, mock_auth_class)
    assert auth.get_organisations() == ("Hogwarts",)
    assert auth.get_auth_dict() == {"Wizards": ("Harry Potter", "Ron Weasley")}


def test_auth_mapping_no_match(mock_auth_mapping, mock_auth_class):
    """
    GIVEN a valid AuthMapping object
    WHEN an email address is passed to it that DOES NOT match an exact email OR a domain
    THEN it should None
    """
    auth = mock_auth_mapping.get_auth("wizard@azkaban.magic.uk")

    assert auth is None


def test_auth_class_factory_valid_fund():
    """
    GIVEN a valid Fund
    WHEN it is passed to _auth_class_factory
    THEN it should return the correct Auth class
    """
    auth_class = _auth_class_factory("Towns Fund")
    assert issubclass(auth_class, AuthBase)
    assert auth_class == TFAuth


def test_auth_class_factory_unknown_fund():
    """
    GIVEN an unknown Fund
    WHEN it is passed to _auth_class_factory
    THEN it should raise a ValueError
    """
    with pytest.raises(ValueError) as error:
        _auth_class_factory("New Fund")
    assert error.value.args[0] == "Unknown Fund"


def test_build_auth_mapping(mocker, mock_auth_class, mock_mapping):
    """
    GIVEN a mapping and a mocked out _auth_class_factory
    WHEN I pass the mapping to build_auth_mapping
    THEN it should return a valid AuthMapping of that data
    """
    mocker.patch("app.main.authorisation._auth_class_factory", return_value=mock_auth_class)

    auth_mapping = build_auth_mapping("Fund", mock_mapping)

    assert isinstance(auth_mapping, AuthMapping)
    assert auth_mapping.get_auth(list(mock_mapping.keys())[0]), "Mapping does not map to source data"


def test_validate_auth_args_valid(mock_auth_class):
    @validate_auth_args
    def dummy_func(*args):
        pass

    mock_auth_class_instance = mock_auth_class(("Hogwarts",), ("Professor Albus Dumbledore",))

    # test with valid arguments
    dummy_func(mock_auth_class_instance, ("arg1", "arg2"), ("arg3", "arg4"))


def test_validate_auth_args_invalid_type():
    @validate_auth_args
    def dummy_func(*args):
        pass

    # test with invalid argument type
    with pytest.raises(ValueError) as excinfo:
        dummy_func(("arg1", "arg2"), ["arg3", "arg4"])
    assert str(excinfo.value) == "Expected a tuple, but got list in args: (('arg1', 'arg2'), ['arg3', 'arg4'])"


def test_validate_auth_args_invalid_element():
    @validate_auth_args
    def dummy_func(*args):
        pass

    # test with invalid tuple element
    with pytest.raises(ValueError) as excinfo:
        dummy_func(("arg1", "arg2"), ("arg3", 123))
    assert str(excinfo.value) == "All elements in the tuple must be strings in args: (('arg1', 'arg2'), ('arg3', 123))"
