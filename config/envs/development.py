from os import getenv

from botocore.config import Config
from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class DevelopmentConfig(DefaultConfig):
    AWS_ACCESS_KEY_ID = getenv("AWS_ACCESS_KEY_ID")
    AWS_SECRET_ACCESS_KEY = getenv("AWS_SECRET_ACCESS_KEY")
    AWS_ENDPOINT_OVERRIDE = getenv("AWS_ENDPOINT_OVERRIDE")
    AWS_CONFIG = Config(retries={"max_attempts": 1, "mode": "standard"})
