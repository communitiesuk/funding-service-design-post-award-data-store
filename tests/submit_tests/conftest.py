from typing import Generator

import pytest
from werkzeug.datastructures import FileStorage

from config.envs.unit_test import UnitTestConfig


@pytest.fixture(scope="function")
def example_pre_ingest_data_file() -> Generator[FileStorage, None, None]:
    """An example pre ingest spreadsheet in towns-fund format."""
    with open(UnitTestConfig.EXAMPLE_INGEST_DATA_PATH, "rb") as file:
        yield FileStorage(file)


@pytest.fixture(scope="function")
def example_ingest_wrong_format() -> Generator[FileStorage, None, None]:
    """An example pre ingest spreadsheet in towns-fund format."""
    with open(UnitTestConfig.EXAMPLE_INGEST_WRONG_FORMAT, "rb") as file:
        yield FileStorage(file)
