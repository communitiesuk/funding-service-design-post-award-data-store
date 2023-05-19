import os
from pathlib import Path


class Config(object):
    FLASK_ROOT = str(Path(__file__).parent)

    CONTACT_EMAIL = os.environ.get("CONTACT_EMAIL", "dev@dev.com")
    CONTACT_PHONE = os.environ.get("CONTACT_PHONE", "12345678910")
    DEPARTMENT_NAME = os.environ.get("DEPARTMENT_NAME", "dev-dept-name")
    DEPARTMENT_URL = os.environ.get("DEPARTMENT_URL", "dev-dept-url")
    SERVICE_NAME = os.environ.get("SERVICE_NAME", "post-award-frontend")
    SERVICE_PHASE = os.environ.get("SERVICE_PHASE", "dev-service-phase")
    SERVICE_URL = os.environ.get("SERVICE_URL", "dev-service-url")
    SESSION_COOKIE_SECURE = True
    API_HOSTNAME = os.environ.get("API_HOSTNAME")

    # Funding Service Design Post Award
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    AUTHENTICATOR_HOST = os.environ.get("AUTHENTICATOR_HOST", "authenticator")
    SESSION_COOKIE_DOMAIN = os.environ.get("SESSION_COOKIE_DOMAIN")
    COOKIE_DOMAIN = os.environ.get("COOKIE_DOMAIN", None)
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")

    # RSA 256 KEYS
    _test_public_key_path = FLASK_ROOT + "/tests/keys/rsa256/public.pem"
    with open(_test_public_key_path, mode="rb") as public_key_file:
        RSA256_PUBLIC_KEY = public_key_file.read()
