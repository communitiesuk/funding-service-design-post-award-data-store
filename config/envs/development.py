import copy
import os
from os import getenv

from botocore.config import Config as BotoConfig
from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class DevelopmentConfig(DefaultConfig):
    AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")
    AWS_ENDPOINT_OVERRIDE = getenv("AWS_ENDPOINT_OVERRIDE")
    AWS_CONFIG = BotoConfig(retries={"max_attempts": 1, "mode": "standard"})
    SQLALCHEMY_ECHO = getenv("SQLALCHEMY_ECHO", "false") in {"true", "yes", "1"}
    SQLALCHEMY_RECORD_QUERIES = True

    # Flask-DebugToolbar
    DEBUG_TB_ENABLED = True
    DEBUG_TB_INTERCEPT_REDIRECTS = False
    DEBUG_TB_ROUTES_HOST = "*"

    TALISMAN_CSP = copy.deepcopy(DefaultConfig.TALISMAN_CSP)

    # Flask-DebugToolbar scripts
    TALISMAN_CSP["script-src"].extend(
        [
            # `var DEBUG_TOOLBAR_STATIC_PATH = '/_debug_toolbar/static/'`
            "'sha256-zWl5GfUhAzM8qz2mveQVnvu/VPnCS6QL7Niu6uLmoWU='",
        ]
    )

    # Flask-DebugToolbar styles
    TALISMAN_CSP["style-src"].extend(
        [
            "'unsafe-hashes'",
            "'sha256-0EZqoz+oBhx7gF4nvY2bSqoGyy4zLjNF+SDQXGp/ZrY='",  # `display:none;`
            "'sha256-biLFinpqYMtWHmXfkA1BPeCY0/fNt46SAZ+BBk5YUog='",  # `display: none;`
            "'sha256-fQY5fP3hSW2gDBpf5aHxpgfqCUocwOYh6zrfhhLsenY='",  # `line-height: 125%;`
            "'sha256-1NkfmhNaD94k7thbpTCKG0dKnMcxprj9kdSKzKR6K/k='",  # `width:20%`
            "'sha256-9KTa3VNMmypk8vbtqjwun0pXQtx5+yn5QoD/WlzV4qM='",  # `background: #ffffff`
            "'sha256-nkkzfdJNt7CL+ndBaKoK92Q9v/iCjSBzw//k1r9jGxU='",  # `color: #bbbbbb`
            "'sha256-vTmCV6LqM520vOLtAZ7+WhSSsaFOONqhCgj+dmpjQak='",  # `color: #333333`
            "'sha256-30uhPRk8bIWOPPNKfIRLXY96DVXF/ZHnfIZz8OBS/eg='",  # `color: #008800; font-weight: bold`
            "'sha256-SAqGh+YBD7v4qJypLeMBSlsddU4Qd67qmTMVRroKuqk='",  # `color: #0000DD; font-weight: bold`
            "'sha256-rietEaLOHfqNF3pcuzajo55dYo9i4UtLS6HN0KrBhbg='",  # `color: #007020`
            "'sha256-Ut0gFM7k9Dr9sRq/kXKsPL4P6Rh8XX0Vt+tKzrdJo7A='",  # `user-select: none;`
        ]
    )

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
        domain: (("Rotherham Metropolitan Borough Council", "Bolton Council", "Wirral Council", "Test Council"),)
        for domain in ("communities.gov.uk", "test.communities.gov.uk")
    }

    # do not attempt to send confirmation email if development and no key is set
    SEND_CONFIRMATION_EMAILS = True if DefaultConfig.NOTIFY_API_KEY else False
    ENABLE_TF_R5 = True
    ENABLE_PF_R2 = True
    # -------------- Submit config: end ----------------
