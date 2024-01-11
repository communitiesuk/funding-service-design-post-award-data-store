import pytest

from app.main.authorisation import (
    AuthBase,
    AuthMapping,
    ReadOnlyAuthMappings,
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


@pytest.fixture
def mock_auth_mappings(mock_auth_mapping):
    return ReadOnlyAuthMappings(fund_to_auth_mappings={"Test Fund": mock_auth_mapping})


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


def test_get_auth_mapping_retrieves_auth_mapping(mock_auth_mappings, mock_auth_class):
    auth_mappings = mock_auth_mappings.get("Test Fund")

    assert auth_mappings
    assert auth_mappings._auth_class == mock_auth_class


def test_get_non_existent_auth_mapping_raises_value_error(mock_auth_mappings):
    with pytest.raises(ValueError):
        mock_auth_mappings.get("Non-existent Fund")


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
