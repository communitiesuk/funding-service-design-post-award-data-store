"""Flask Local Development Environment Configuration."""
from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class UnitTestConfig(DefaultConfig):
    DefaultConfig.TALISMAN_SETTINGS["force_https"] = False
    USE_LOCAL_DATA = "True"
    SESSION_COOKIE_SECURE = False

    # RSA 256 KEYS
    _test_public_key_path = DefaultConfig.FLASK_ROOT + "/tests/keys/rsa256/public.pem"
    with open(_test_public_key_path, mode="rb") as public_key_file:
        RSA256_PUBLIC_KEY = public_key_file.read()

    WTF_CSRF_ENABLED = False

    # Redis Configuration for Feature Flags
    TOGGLES_URL = "redis://localhost:6379/0"
