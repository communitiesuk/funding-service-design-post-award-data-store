from pathlib import Path
from typing import BinaryIO

import pytest

from config.envs.default import DefaultConfig

resources = Path(__file__).parent / "resources"


@pytest.fixture(scope="function")
def example_data_model_file() -> BinaryIO:
    """An example spreadsheet in towns-fund schema format."""
    with open(DefaultConfig.EXAMPLE_DATA_MODEL_PATH, "rb") as file:
        yield file


@pytest.fixture(scope="function")
def example_round_one_file() -> BinaryIO:
    """An example spreadsheet in Round One format."""
    with open(DefaultConfig.EXAMPLE_ROUND_ONE_PATH, "rb") as file:
        yield file
