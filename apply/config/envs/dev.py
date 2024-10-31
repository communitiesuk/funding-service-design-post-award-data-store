"""Flask Dev Pipeline Environment Configuration."""
import logging
from os import getenv

from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class DevConfig(DefaultConfig):

    FSD_LOGGING_LEVEL = logging.INFO
    SESSION_COOKIE_DOMAIN = getenv("SESSION_COOKIE_DOMAIN")
