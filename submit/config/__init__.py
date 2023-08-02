# flake8: noqa
import os

FLASK_ENV = os.getenv("FLASK_ENV")

if not FLASK_ENV:
    raise KeyError("FLASK_ENV does not exist in environ")

match FLASK_ENV:
    case _:
        from config.envs.default import DefaultConfig as Config

try:
    Config.pretty_print()
except AttributeError:
    print({"msg": "Config doesn't have pretty_print function."})

__all__ = [Config]
