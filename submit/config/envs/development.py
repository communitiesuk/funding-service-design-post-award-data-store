from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class DevelopmentConfig(DefaultConfig):
    # RSA 256 KEYS
    if not hasattr(DefaultConfig, "RSA256_PUBLIC_KEY"):
        _test_public_key_path = DefaultConfig.FLASK_ROOT + "/tests/keys/rsa256/public.pem"
        with open(_test_public_key_path, mode="rb") as public_key_file:
            RSA256_PUBLIC_KEY = public_key_file.read()

    # devs can submit for these LAs and places
    ADDITIONAL_EMAIL_LOOKUPS = {
        "version1.com": (
            ("Sunderland City Council", "Worcester City Council"),
            ("Sunderland City Centre", "Blackfriars - Northern City Centre", "Worcester"),
        ),
        "communities.gov.uk": (
            ("Sunderland City Council", "Worcester City Council"),
            ("Sunderland City Centre", "Blackfriars - Northern City Centre", "Worcester"),
        ),
    }
