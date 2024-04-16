from pathlib import Path
from typing import BinaryIO
from unittest import mock

import pytest

from config import Config
from core.aws import _S3_CLIENT


def create_bucket(bucket: str):
    """Helper function that creates a specified bucket if it doesn't already exist."""
    if bucket not in {bucket_obj["Name"] for bucket_obj in _S3_CLIENT.list_buckets()["Buckets"]}:
        _S3_CLIENT.create_bucket(Bucket=bucket, CreateBucketConfiguration={"LocationConstraint": "eu-central-1"})


def delete_bucket(bucket: str):
    """Helper function that deletes all objects in a specified bucket and then deletes the bucket."""
    objects = _S3_CLIENT.list_objects_v2(Bucket=bucket)
    if objects := objects.get("Contents"):
        objects = list(map(lambda x: {"Key": x["Key"]}, objects))
        _S3_CLIENT.delete_objects(Bucket=bucket, Delete={"Objects": objects})
    _S3_CLIENT.delete_bucket(Bucket=bucket)


@pytest.fixture(scope="module")
def test_buckets():
    """Sets up and tears down buckets used by this module.
    On set up:
    - creates data-store-failed-files-unit-tests
    - creates data-store-successful-files-unit-tests

    On tear down, deletes all objects stored in the buckets and then the buckets themselves.
    """
    create_bucket(Config.AWS_S3_BUCKET_FAILED_FILES)
    create_bucket(Config.AWS_S3_BUCKET_SUCCESSFUL_FILES)
    yield
    delete_bucket(Config.AWS_S3_BUCKET_FAILED_FILES)
    delete_bucket(Config.AWS_S3_BUCKET_SUCCESSFUL_FILES)


@pytest.fixture()
def pathfinders_round_1_file_success() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should ingest without validation errors."""
    with open(Path(__file__).parent / "mock_pf_returns" / "PF_Round_1_Success.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_3_file_success() -> BinaryIO:
    """An example spreadsheet for reporting round 3 of Towns Fund that should ingest without validation errors."""
    with open(Path(__file__).parent / "mock_tf_returns" / "TF_Round_3_Success.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_file_success() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should ingest without validation errors."""
    with open(Path(__file__).parent / "mock_tf_returns" / "TF_Round_4_Success.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_round_agnostic_failures() -> BinaryIO:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise TF round agnostic failures"""
    with open(Path(__file__).parent / "mock_tf_returns" / "TF_Round_4_Round_Agnostic_Failures.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def mock_sentry_metrics():
    with mock.patch("core.metrics.sentry_sdk.metrics") as mock_sentry_metrics:
        yield mock_sentry_metrics
