# flake8: noqa
import os

FLASK_ENV = os.getenv("FLASK_ENV")

if not FLASK_ENV:
    raise KeyError("FLASK_ENV does not exist in environ")

match FLASK_ENV:
    case "unit_test":
        from config.envs.unit_test import UnitTestConfig as Config
    case "development":
        from config.envs.development import DevelopmentConfig as Config  # type: ignore # TODO: fixme
    case "dev" | "test" | "prod":
        from config.envs.aws import AwsConfig as Config  # type: ignore # TODO: fixme
    case _:
        from config.envs.default import DefaultConfig as Config  # type: ignore # TODO: fixme

try:
    Config.pretty_print()  # type: ignore # TODO: fixme
except AttributeError:
    print({"msg": "Config doesn't have pretty_print function."})

__all__ = ["Config"]
