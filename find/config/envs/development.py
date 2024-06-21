import logging

from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class DevelopmentConfig(DefaultConfig):
    # RSA 256 KEYS
    if not hasattr(DefaultConfig, "RSA256_PUBLIC_KEY"):
        _test_public_key_path = DefaultConfig.FLASK_ROOT + "/tests/keys/rsa256/public.pem"
        with open(_test_public_key_path, mode="r") as public_key_file:
            RSA256_PUBLIC_KEY = public_key_file.read()
    FSD_LOG_LEVEL = logging.DEBUG

    DEBUG_USER_ON = True
    DEBUG_USER = {
        "full_name": "Development User",
        "email": "dev@communities.gov.uk",
        "roles": [],
        "highest_role_map": {},
    }
    AUTO_BUILD_ASSETS = True
