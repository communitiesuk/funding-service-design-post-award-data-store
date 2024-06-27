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

    # Config variables for sending FIND-emails
    NOTIFY_FIND_API_KEY = os.getenv("NOTIFY_FIND_API_KEY")
    NOTIFY_FIND_REPORT_DOWNLOAD_TEMPLATE_ID = "62124580-5d5e-4975-ab84-76d14be2a9ad"
    AWS_S3_BUCKET_FIND_DATA_FILES = os.getenv("AWS_S3_BUCKET_FIND_DATA_FILES")
    FIND_SERVICE_BASE_URL = os.getenv("FIND_SERVICE_BASE_URL")

    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")

    CELERY = dict(
        broker_url=REDIS_URL,
        result_backend=REDIS_URL,
        task_ignore_result=False,
    )
