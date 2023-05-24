import base64
import os
from pathlib import Path

from fsd_utils import configclass


@configclass
class DefaultConfig(object):
    FLASK_ROOT = str(Path(__file__).parent.parent.parent)

    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "dev@dev.com")
    CONTACT_PHONE = os.environ.get("CONTACT_PHONE", "12345678910")
    DEPARTMENT_NAME = os.environ.get("DEPARTMENT_NAME", "dev-dept-name")
    DEPARTMENT_URL = os.environ.get("DEPARTMENT_URL", "dev-dept-url")
    SERVICE_NAME = os.environ.get("SERVICE_NAME", "post-award-frontend")
    SERVICE_PHASE = os.environ.get("SERVICE_PHASE", "dev-service-phase")
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
