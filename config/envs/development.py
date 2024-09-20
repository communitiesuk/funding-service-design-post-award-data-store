import os
from os import getenv

from botocore.config import Config
from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class DevelopmentConfig(DefaultConfig):
    AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")
    AWS_ENDPOINT_OVERRIDE = getenv("AWS_ENDPOINT_OVERRIDE")
    AWS_CONFIG = Config(retries={"max_attempts": 1, "mode": "standard"})
    SQLALCHEMY_ECHO = getenv("SQLALCHEMY_ECHO", "false") in {"true", "yes", "1"}

    # RSA 256 KEYS
    if not hasattr(DefaultConfig, "RSA256_PUBLIC_KEY"):
        _test_public_key_path = DefaultConfig.FLASK_ROOT / "tests" / "keys" / "rsa256" / "public.pem"
        with open(_test_public_key_path, mode="r") as public_key_file:
            RSA256_PUBLIC_KEY = public_key_file.read()

    DEBUG_USER_ROLE = os.environ.get("DEBUG_USER_ROLE", "PF_MONITORING_RETURN_SUBMITTER")
    DEBUG_USER_ON = True
    DEBUG_USER = {
        "full_name": "Development User",
        "email": "dev@communities.gov.uk",
        "roles": ["PF_MONITORING_RETURN_SUBMITTER", "TF_MONITORING_RETURN_SUBMITTER", "FSD_ADMIN"],
        "highest_role_map": {},
    }
    DEBUG_USER_ACCOUNT_ID = "00000000-0000-0000-0000-000000000000"
    AUTO_BUILD_ASSETS = False

    # -------------- Submit config: start --------------

    # devs can submit for these LAs and places
    TF_ADDITIONAL_EMAIL_LOOKUPS = {
        "communities.gov.uk": (
            ("Sunderland City Council", "Worcester City Council"),
            ("Sunderland City Centre", "Blackfriars - Northern City Centre", "Worcester"),
            ("Town_Deal", "Future_High_Street_Fund"),
        ),
        "test.communities.gov.uk": (
            ("Sunderland City Council", "Worcester City Council"),
            ("Sunderland City Centre", "Blackfriars - Northern City Centre", "Worcester"),
            ("Town_Deal", "Future_High_Street_Fund"),
        ),
    }

    PF_ADDITIONAL_EMAIL_LOOKUPS = {
        domain: (("Rotherham Metropolitan Borough Council", "Bolton Council", "Wirral Council"),)
        for domain in ("communities.gov.uk", "test.communities.gov.uk")
    }

    # do not attempt to send confirmation email if development and no key is set
    SEND_CONFIRMATION_EMAILS = True if DefaultConfig.NOTIFY_API_KEY else False
    ENABLE_TF_R5 = True
    ENABLE_PF_R2 = True
    # -------------- Submit config: end ----------------
