import base64
import logging
import os
from pathlib import Path

from fsd_utils import CommonConfig, configclass


@configclass
class DefaultConfig(object):
    FLASK_ROOT = str(Path(__file__).parent.parent.parent)
    FLASK_ENV = CommonConfig.FLASK_ENV
    FSD_LOG_LEVEL = logging.INFO

    MAINTENANCE_MODE: bool = os.getenv("MAINTENANCE_MODE", "false").lower() in {"1", "true", "yes", "y", "on"}
    MAINTENANCE_ENDS_FROM: str | None = os.getenv("MAINTENANCE_ENDS_FROM")

    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "fsd.support@levellingup.gov.uk").lower()
    CONTACT_PHONE = os.environ.get("CONTACT_PHONE", "12345678910")
    DEPARTMENT_NAME = os.environ.get("DEPARTMENT_NAME", "Department for Levelling Up, Housing and Communities")
    DEPARTMENT_URL = os.environ.get(
        "DEPARTMENT_URL",
        "https://www.gov.uk/government/organisations/department-for-levelling-up-housing-and-communities",
    )
    SERVICE_NAME = os.environ.get("SERVICE_NAME", "Find monitoring data")
    SERVICE_PHASE = os.environ.get("SERVICE_PHASE", "BETA")
    SERVICE_URL = os.environ.get("SERVICE_URL", "dev-service-url")
    SESSION_COOKIE_SECURE = True
    DATA_STORE_API_HOST = os.environ.get("DATA_STORE_API_HOST")

    # Funding Service Design Post Award
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    AUTHENTICATOR_HOST = os.environ.get("AUTHENTICATOR_HOST", "authenticator")
    COOKIE_DOMAIN = os.environ.get("COOKIE_DOMAIN", None)
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")

    # RSA 256 KEYS
    RSA256_PUBLIC_KEY_BASE64 = os.getenv("RSA256_PUBLIC_KEY_BASE64")
    if RSA256_PUBLIC_KEY_BASE64:
        RSA256_PUBLIC_KEY = base64.b64decode(RSA256_PUBLIC_KEY_BASE64).decode()

    AUTO_BUILD_ASSETS = False
