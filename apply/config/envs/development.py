"""Flask Local Development Environment Configuration."""
import logging
from os import getenv

from config.envs.default import DefaultConfig
from distutils.util import strtobool
from fsd_utils import configclass


@configclass
class DevelopmentConfig(DefaultConfig):
    FSD_LOGGING_LEVEL = logging.DEBUG
    USE_LOCAL_DATA = strtobool(getenv("USE_LOCAL_DATA", "True"))
    SESSION_COOKIE_SECURE = False

    SESSION_COOKIE_DOMAIN = getenv("SESSION_COOKIE_DOMAIN")

    # RSA 256 KEYS
    if not hasattr(DefaultConfig, "RSA256_PUBLIC_KEY"):
        _test_public_key_path = DefaultConfig.FLASK_ROOT + "/tests/keys/rsa256/public.pem"
        with open(_test_public_key_path, mode="rb") as public_key_file:
            RSA256_PUBLIC_KEY = public_key_file.read()

    # LRU cache settings
    LRU_CACHE_TIME = 1  # in seconds
    SECRET_KEY = "dev"  # pragma: allowlist secret
