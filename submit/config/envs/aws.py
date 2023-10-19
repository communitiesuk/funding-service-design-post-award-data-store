import os

from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class AwsConfig(DefaultConfig):
    NOTIFY_API_KEY = os.environ["NOTIFY_API_KEY"]  # fail if not present
