import json
import os

from fsd_utils import configclass

from config.envs.default import DefaultConfig


def get_database_url() -> str:
    """get database params from env and convert into expected format
    :return: database url string
    """
    database_json = os.environ["DATASTORECLUSTER_SECRET"]
    db_dict = json.loads(database_json)
    return (
        f"postgresql://{db_dict['username']}:{db_dict['password']}@"
        f"{db_dict['host']}:{db_dict['port']}/{db_dict['dbname']}"
    )


@configclass
class AwsConfig(DefaultConfig):
    SQLALCHEMY_DATABASE_URI = get_database_url()

    # -------------- Submit config: start --------------
    # fail if these confirmation email requirements are not present
    NOTIFY_API_KEY = os.environ["NOTIFY_API_KEY"]
    TF_CONFIRMATION_EMAIL_ADDRESS = os.environ["TF_CONFIRMATION_EMAIL_ADDRESS"]
    # -------------- Submit config: end ----------------
