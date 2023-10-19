from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class UnitTestConfig(DefaultConfig):
    TESTING = True
    # RSA 256 KEYS
    if not hasattr(DefaultConfig, "RSA256_PUBLIC_KEY"):
        _test_public_key_path = DefaultConfig.FLASK_ROOT + "/tests/keys/rsa256/public.pem"
        with open(_test_public_key_path, mode="rb") as public_key_file:
            RSA256_PUBLIC_KEY = public_key_file.read()

    EXAMPLE_INGEST_WRONG_FORMAT = DefaultConfig.FLASK_ROOT + "/tests/resources/wrong_format_test_file.txt"
    EXAMPLE_INGEST_DATA_PATH = DefaultConfig.FLASK_ROOT + "/tests/resources/Pre_ingest_EXAMPLE_data.xlsx"
    DATA_STORE_API_HOST = "http://data-store"
    ADDITIONAL_EMAIL_LOOKUPS = {
        "contractor@contractor.com": (("Amber Valley Borough Council",), ("Heanor",)),
    }

    # notify client passes init with this key and is then mocked
    NOTIFY_API_KEY = "fake_key-0ab1234a-12a3-12ab-12a3-a1b2cd3e4f5g-a123b456-1a23-1abv-a1bc-123a45678910"
