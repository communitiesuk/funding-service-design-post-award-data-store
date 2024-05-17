import logging
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
        with open(_test_public_key_path, mode="rb") as public_key_file:
            RSA256_PUBLIC_KEY = public_key_file.read()
    FSD_LOG_LEVEL = logging.DEBUG

    DEBUG_USER_ON = True
    DEBUG_USER = {
        "full_name": "Development User",
        "email": "dev@communities.gov.uk",
        "roles": [],
        "highest_role_map": {},
    }
