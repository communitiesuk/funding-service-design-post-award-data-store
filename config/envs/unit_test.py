from botocore.config import Config
from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class UnitTestConfig(DefaultConfig):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    AWS_REGION = "eu-central-1"
    AWS_ACCESS_KEY_ID = "test"
    AWS_SECRET_ACCESS_KEY = "test"
    AWS_ENDPOINT_OVERRIDE = "http://127.0.0.1:4566/"
    AWS_S3_BUCKET_FAILED_FILES = "data-store-failed-files-dev"
    AWS_CONFIG = Config(retries={"max_attempts": 1, "mode": "standard"})
