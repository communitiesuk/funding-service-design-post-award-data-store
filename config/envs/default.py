import os
from os import environ
from pathlib import Path

from fsd_utils import CommonConfig, configclass


@configclass
class DefaultConfig(object):
    FLASK_ROOT = Path(__file__).parent.parent.parent
    FLASK_ENV = CommonConfig.FLASK_ENV

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL", "postgresql://postgres:password@localhost:5432/data_store")
    EXAMPLE_DATA_MODEL_PATH = FLASK_ROOT / "tests" / "resources" / "Post_transform_EXAMPLE_data.xlsx"
    ENABLE_PROFILER = os.getenv("ENABLE_PROFILER")

    AWS_REGION = os.getenv("AWS_REGION")
    AWS_S3_BUCKET_FAILED_FILES = os.getenv("AWS_S3_BUCKET_FAILED_FILES")
    AWS_S3_BUCKET_SUCCESSFUL_FILES = os.getenv("AWS_S3_BUCKET_SUCCESSFUL_FILES")
