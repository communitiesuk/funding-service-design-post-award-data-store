from pathlib import Path
from typing import BinaryIO

import pytest

resources = Path(__file__).parent / "resources"


@pytest.fixture(scope="function")
def example_data_model_file() -> BinaryIO:
    """An example spreadsheet in towns-fund schema format."""
    with open(resources / "Data_Model_v3.7_EXAMPLE.xlsx", "rb") as file:
        yield file
