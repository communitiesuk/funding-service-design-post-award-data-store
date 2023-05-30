import tempfile
from os import environ
from pathlib import Path

from fsd_utils import configclass


@configclass
class DefaultConfig(object):
    FLASK_ROOT = str(Path(__file__).parent.parent.parent)

    SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL", f"sqlite:///{tempfile.gettempdir()}/sqlite.db")
