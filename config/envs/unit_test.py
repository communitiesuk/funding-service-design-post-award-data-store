from botocore.config import Config
from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class UnitTestConfig(DefaultConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:password@localhost:5432/data_store_test"
    AWS_REGION = "eu-central-1"
    AWS_ACCESS_KEY_ID = "test"
    AWS_SECRET_ACCESS_KEY = "test"
    AWS_ENDPOINT_OVERRIDE = "http://127.0.0.1:4566/"
    AWS_S3_BUCKET_FAILED_FILES = "data-store-failed-files-unit-tests"
    AWS_S3_BUCKET_SUCCESSFUL_FILES = "data-store-successful-files-unit-tests"
    AWS_S3_BUCKET_FIND_DOWNLOAD_FILES = "data-store-find-download-files-unit-tests"
    AWS_CONFIG = Config(retries={"max_attempts": 1, "mode": "standard"})
    FIND_SERVICE_BASE_URL = "http://localhost:4002"
    WTF_CSRF_ENABLED = False

    # RSA 256 KEYS
    if not hasattr(DefaultConfig, "RSA256_PUBLIC_KEY"):
        _test_public_key_path = DefaultConfig.FLASK_ROOT / "tests" / "keys" / "rsa256" / "public.pem"
        with open(_test_public_key_path, mode="r") as public_key_file:
            RSA256_PUBLIC_KEY = public_key_file.read()

    # -------------- Submit config: start --------------
    EXAMPLE_INGEST_WRONG_FORMAT = (
        DefaultConfig.FLASK_ROOT / "tests" / "submit_tests" / "resources" / "wrong_format_test_file.txt"
    )
    EXAMPLE_INGEST_DATA_PATH = (
        DefaultConfig.FLASK_ROOT / "tests" / "submit_tests" / "resources" / "Pre_ingest_EXAMPLE_data.xlsx"
    )
    TF_ADDITIONAL_EMAIL_LOOKUPS = {
        "multiple_orgs@contractor.com": (
            (
                "Rotherham Metropolitan Borough Council",
                "Another Council",
            ),
            ("Rotherham",),
            ("Town_Deal",),
        ),
    }

    PF_ADDITIONAL_EMAIL_LOOKUPS = {
        "multiple_orgs@contractor.com": (("Rotherham Metropolitan Borough Council",),),
    }

    # notify client passes init with this key and is then mocked
    NOTIFY_API_KEY = "fake_key-0ab1234a-12a3-12ab-12a3-a1b2cd3e4f5g-a123b456-1a23-1abv-a1bc-123a45678910"
    AUTO_BUILD_ASSETS = True
    # -------------- Submit config: end ------------

    # When running tests, don't try to send celery tasks to a worker - instead just run them as if they were
    # direct synchronous calls. Otherwise we'd have to manage a celery worker/message broker during pytest runs.
    # Which is overkill for now. 28/06/2024.
    CELERY = DefaultConfig.CELERY
    CELERY["task_always_eager"] = True
