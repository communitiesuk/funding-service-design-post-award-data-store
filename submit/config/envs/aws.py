import os

from fsd_utils import configclass

from config.envs.default import DefaultConfig


@configclass
class AwsConfig(DefaultConfig):
    # fail if these confirmation email requirements are not present
    NOTIFY_API_KEY = os.environ["NOTIFY_API_KEY"]
    TF_CONFIRMATION_EMAIL_ADDRESS = os.environ["TF_CONFIRMATION_EMAIL_ADDRESS"]
