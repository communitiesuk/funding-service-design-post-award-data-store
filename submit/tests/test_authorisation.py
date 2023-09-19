import pytest
from flask import g
from fsd_utils.authentication.models import User
from werkzeug.exceptions import Unauthorized

from app.main.authorisation import check_authorised, get_local_authority_and_place_names


def test_custom_las_and_place_names(flask_test_client):
    """Check that custom domains/emails are being added to the mapping used by authorization."""
    assert "contractor@contractor.com" in flask_test_client.application.config["EMAIL_TO_LA_AND_PLACE_NAMES"]


def test_check_authorized_success(flask_test_client):
    valid_user = User(full_name="Test", roles=[], highest_role_map={}, email="user@wigan.gov.uk")

    with flask_test_client.application.app_context():
        g.user = valid_user
        local_authorities, places = check_authorised()
    assert local_authorities
    assert places


def test_check_authorized_failure(flask_test_client):
    invalid_user = User(full_name="Test", roles=[], highest_role_map={}, email="unknown_user@unknown.gov.uk")

    with pytest.raises(Unauthorized):
        with flask_test_client.application.app_context():
            g.user = invalid_user
            check_authorised()


def test_get_local_authority_place_names(flask_test_client):
    with flask_test_client.application.app_context():
        # tests mapping the email domain
        domain_mapping_1 = get_local_authority_and_place_names("user@bolton.gov.uk")
        domain_mapping_2 = get_local_authority_and_place_names("user@newcastle-staffs.gov.uk")
        domain_mapping_3 = get_local_authority_and_place_names("user@wigan.gov.uk")
        # tests mapping the whole email address
        email_mapping = get_local_authority_and_place_names("contractor@contractor.com")
        # no mapping exists
        no_mapping = get_local_authority_and_place_names("user@wmadeup.gov.uk")

    assert domain_mapping_1 == (
        ("Bolton Metropolitan Borough Council",),
        (
            "Farnworth",
            "Bolton",
        ),
    )
    assert domain_mapping_2 == (
        ("Newcastle-under-Lyme District Council",),
        ("Newcastle-Under-Lyme Town Centre", "Kidsgrove", "Newcastle-under-Lyme", "Newcastle-under-Lyme Town Centre"),
    )
    assert domain_mapping_3 == (("Wigan Metropolitan Borough Council",), ("Wigan",))
    assert email_mapping == (("Amber Valley Borough Council",), ("Heanor",))
    assert no_mapping == (None, None)
