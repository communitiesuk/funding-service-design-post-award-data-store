# flake8: noqa
from os import getenv

FLASK_ENV = getenv("FLASK_ENV")

match FLASK_ENV:
    case "development":
        from config.envs.development import DevelopmentConfig as Config
    case "dev":
        from config.envs.dev import DevConfig as Config
    case "test":
        from config.envs.test import TestConfig as Config
    case "unit_test":
        from config.envs.unit_test import UnitTestConfig as Config
    case "uat" | "production":
        from config.envs.production import ProductionConfig as Config
    case _:
        from config.envs.default import DefaultConfig as Config

try:
    Config.pretty_print()
except AttributeError:
    print({"msg": "Config doesn't have pretty_print function."})

__all__ = [Config]
