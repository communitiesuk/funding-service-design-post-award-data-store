from pathlib import Path
from typing import BinaryIO

import pytest

resources = Path(__file__).parent / "resources"


@pytest.fixture(scope="function")
def example_file() -> BinaryIO:
    """An example spreadsheet in towns-fund schema format."""
    return (resources / "DLUCH_Data_Model_V3.4_EXAMPLE.xlsx").open("rb")
