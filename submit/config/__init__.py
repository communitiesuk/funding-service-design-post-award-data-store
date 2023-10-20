# flake8: noqa
import os

FLASK_ENV = os.getenv("FLASK_ENV")

if not FLASK_ENV:
    raise KeyError("FLASK_ENV does not exist in environ")

match FLASK_ENV:
    case "unit_test":
        from config.envs.unit_test import UnitTestConfig as Config
    case "development":
        from config.envs.development import DevelopmentConfig as Config
    case "dev" | "test" | "production":
        from config.envs.aws import AwsConfig as Config
    case _:
        from config.envs.default import DefaultConfig as Config

try:
    Config.pretty_print()
except AttributeError:
    print({"msg": "Config doesn't have pretty_print function."})

__all__ = [Config]
