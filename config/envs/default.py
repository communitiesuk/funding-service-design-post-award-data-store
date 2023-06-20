import os
import tempfile
from copy import deepcopy
from os import environ
from pathlib import Path

from fsd_utils import configclass

from core.validation.schema import parse_schema
from core.validation_schema import SCHEMA


@configclass
class DefaultConfig(object):
    FLASK_ROOT = Path(__file__).parent.parent.parent

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL", f"sqlite:///{tempfile.gettempdir()}/sqlite.db")
    VALIDATION_SCHEMA = parse_schema(deepcopy(SCHEMA))
    EXAMPLE_DATA_MODEL_PATH = (
        FLASK_ROOT / "tests" / "controller_tests" / "resources" / "Post_transform_EXAMPLE_data.xlsx"
    )
    ENABLE_PROFILER = os.getenv("ENABLE_PROFILER")
