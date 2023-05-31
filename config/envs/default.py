import tempfile
from copy import deepcopy
from os import environ
from pathlib import Path

from fsd_utils import configclass

from core.validation.schema import parse_schema
from core.validation_schema import SCHEMA


@configclass
class DefaultConfig(object):
    FLASK_ROOT = str(Path(__file__).parent.parent.parent)

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL", f"sqlite:///{tempfile.gettempdir()}/sqlite.db")
    VALIDATION_SCHEMA = parse_schema(deepcopy(SCHEMA))
