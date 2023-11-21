import pytest
from flask import g
from fsd_utils.authentication.models import User
from werkzeug.exceptions import Unauthorized

from app.main.authorisation import (
    check_authorised,
    get_local_authority_and_place_names_and_fund_types,
)


def test_custom_las_and_place_names(flask_test_client):
    """Check that custom domains/emails are being added to the mapping used by authorization."""
    assert (
        "contractor@contractor.com"
        in flask_test_client.application.config[("EMAIL_TO_LA_AND_PLACE_NAMES_AND_FUND_TYPES")]
    )


def test_check_authorized_success(flask_test_client):
    valid_user = User(full_name="Test", roles=[], highest_role_map={}, email="user@wigan.gov.uk")

    with flask_test_client.application.app_context():
        g.user = valid_user
        local_authorities, auth = check_authorised()
    assert local_authorities
    assert auth["Place Names"] == ("Wigan",)
    assert auth["Fund Types"] == ("Town_Deal", "Future_High_Street_Fund")


def test_check_authorized_failure(flask_test_client):
    invalid_user = User(full_name="Test", roles=[], highest_role_map={}, email="unknown_user@unknown.gov.uk")

    with pytest.raises(Unauthorized):
        with flask_test_client.application.app_context():
            g.user = invalid_user
            check_authorised()


def test_get_local_authority_place_names_and_fund_types(flask_test_client):
    with flask_test_client.application.app_context():
        # tests mapping the email domain
        domain_mapping_1 = get_local_authority_and_place_names_and_fund_types("user@bolton.gov.uk")
        domain_mapping_2 = get_local_authority_and_place_names_and_fund_types("user@newcastle-staffs.gov.uk")
        domain_mapping_3 = get_local_authority_and_place_names_and_fund_types("user@wigan.gov.uk")
        domain_mapping_4 = get_local_authority_and_place_names_and_fund_types("user@cumberland.gov.uk")
        # tests mapping the whole email address
        email_mapping = get_local_authority_and_place_names_and_fund_types("contractor@contractor.com")
        # test mapping of case-insensitive e-mail
        case_insensitive_mapping = get_local_authority_and_place_names_and_fund_types("Contractor@contractor.com")
        # no mapping exists
        no_mapping = get_local_authority_and_place_names_and_fund_types("user@wmadeup.gov.uk")
        # only authorised for TD and not HS
        only_td_mapping = get_local_authority_and_place_names_and_fund_types("td_only@contractor.com")

    assert domain_mapping_1 == (
        ("Bolton Metropolitan Borough Council",),
        (
            "Farnworth",
            "Bolton",
        ),
        ("Town_Deal", "Future_High_Street_Fund"),
    )
    assert domain_mapping_2 == (
        ("Newcastle-under-Lyme Borough Council",),
        ("Newcastle-Under-Lyme Town Centre", "Kidsgrove", "Newcastle-under-Lyme", "Newcastle-under-Lyme Town Centre"),
        ("Town_Deal", "Future_High_Street_Fund"),
    )
    assert domain_mapping_3 == (("Wigan Council",), ("Wigan",), ("Town_Deal", "Future_High_Street_Fund"))
    assert domain_mapping_4 == (
        ("Cumberland Council",),
        ("Workington", "Cleator Moor", "Millom", "Carlisle", "Carlisle City Centre", "Maryport Town Centre"),
        ("Town_Deal", "Future_High_Street_Fund"),
    )
    assert email_mapping == (("Amber Valley Borough Council",), ("Heanor",), ("Town_Deal", "Future_High_Street_Fund"))
    assert case_insensitive_mapping == (
        ("Amber Valley Borough Council",),
        ("Heanor",),
        ("Town_Deal", "Future_High_Street_Fund"),
    )
    assert no_mapping == (None, None, None)
    assert only_td_mapping == (("Rotherham Metropolitan Borough Council",), ("Rotherham",), ("Town_Deal",))
