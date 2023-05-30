from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class UnitTestConfig(DefaultConfig):
    TESTING = True

    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
