from pathlib import Path
from typing import BinaryIO, Generator

import pytest


@pytest.fixture()
def pathfinders_round_1_file_success_different_postcodes() -> Generator[BinaryIO, None, None]:
    """An example spreadsheet for reporting round 1 of Pathfinders with different project postcodes to the fixture above
    that should ingest without validation errors."""
    with open(Path(__file__).parent / "mock_pf_returns" / "PF_Round_1_Success_Different_Postcodes.xlsx", "rb") as file:
        yield file


@pytest.fixture(scope="function")
def towns_fund_round_4_round_agnostic_failures() -> Generator[BinaryIO, None, None]:
    """An example spreadsheet for reporting round 4 of Towns Fund that should raise TF round agnostic failures"""
    with open(Path(__file__).parent / "mock_tf_returns" / "TF_Round_4_Round_Agnostic_Failures.xlsx", "rb") as file:
        yield file
