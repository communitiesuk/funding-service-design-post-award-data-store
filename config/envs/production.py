"""Flask Production Environment Configuration."""
from config.envs.default import DefaultConfig
from fsd_utils import configclass


@configclass
class ProductionConfig(DefaultConfig):
    pass
