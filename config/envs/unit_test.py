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
    AWS_S3_BUCKET_FIND_DATA_FILES = "data-store-find-data-unit-tests"
    AWS_CONFIG = Config(retries={"max_attempts": 1, "mode": "standard"})
    FIND_SERVICE_BASE_URL = "http://localhost:4002"

    # When running tests, don't try to send celery tasks to a worker - instead just run them as if they were
    # direct synchronous calls. Otherwise we'd have to manage a celery worker/message broker during pytest runs.
    # Which is overkill for now. 28/06/2024.
    CELERY = DefaultConfig.CELERY
    CELERY["task_always_eager"] = True
