"""Flask configuration."""
import base64
from os import environ
from os import getenv
from pathlib import Path

from distutils.util import strtobool
from fsd_utils import CommonConfig
from fsd_utils import configclass


@configclass
class DefaultConfig:
    # Application Config
    FLASK_ENV = environ.get("FLASK_ENV", "development")
    SECRET_KEY = CommonConfig.SECRET_KEY
    SESSION_COOKIE_NAME = environ.get("SESSION_COOKIE_NAME", "session_cookie")
    SESSION_COOKIE_SECURE = True
    WTF_CSRF_TIME_LIMIT = CommonConfig.WTF_CSRF_TIME_LIMIT
    MAINTENANCE_MODE = strtobool(getenv("MAINTENANCE_MODE", "False"))
    MAINTENANCE_END_TIME = getenv("MAINTENANCE_END_TIME", "18 December 2023 at 03:00pm")

    STATIC_FOLDER = "static"
    TEMPLATES_FOLDER = "templates"
    LOCAL_SERVICE_NAME = "local_flask"
    FLASK_ROOT = str(Path(__file__).parent.parent.parent)

    # Funding Service Design
    FSD_USER_TOKEN_COOKIE_NAME = "fsd_user_token"
    AUTHENTICATOR_HOST = environ.get("AUTHENTICATOR_HOST", "authenticator")
    ENTER_APPLICATION_URL = AUTHENTICATOR_HOST + "/service/magic-links/new"
    MAGIC_LINK_URL = (
        AUTHENTICATOR_HOST + "/service/magic-links/new?" + "fund={fund_short_name}&round={round_short_name}"
    )
    SESSION_COOKIE_DOMAIN = environ.get("SESSION_COOKIE_DOMAIN")
    COOKIE_DOMAIN = environ.get("COOKIE_DOMAIN", None)

    # RSA 256 KEYS
    RSA256_PUBLIC_KEY_BASE64 = environ.get("RSA256_PUBLIC_KEY_BASE64")
    if RSA256_PUBLIC_KEY_BASE64:
        RSA256_PUBLIC_KEY = base64.b64decode(RSA256_PUBLIC_KEY_BASE64).decode()

    # APIs Config
    TEST_APPLICATION_STORE_API_HOST = CommonConfig.TEST_APPLICATION_STORE_API_HOST
    TEST_FUND_STORE_API_HOST = CommonConfig.TEST_FUND_STORE_API_HOST
    TEST_ACCOUNT_STORE_API_HOST = CommonConfig.TEST_ACCOUNT_STORE_API_HOST

    ACCOUNT_STORE_API_HOST = environ.get("ACCOUNT_STORE_API_HOST", TEST_ACCOUNT_STORE_API_HOST)
    ACCOUNTS_ENDPOINT = "/accounts"
    APPLICATION_STORE_API_HOST = environ.get("APPLICATION_STORE_API_HOST", TEST_APPLICATION_STORE_API_HOST)
    GET_APPLICATION_ENDPOINT = APPLICATION_STORE_API_HOST + "/applications/{application_id}"
    SEARCH_APPLICATIONS_ENDPOINT = (
        APPLICATION_STORE_API_HOST + "/applications?order_by=last_edited&order_rev=1&{search_params}"
    )
    GET_APPLICATIONS_FOR_ACCOUNT_ENDPOINT = (
        APPLICATION_STORE_API_HOST + "/applications?account_id={account_id}" + "&order_by=last_edited&order_rev=1"
    )
    UPDATE_APPLICATION_FORM_ENDPOINT = APPLICATION_STORE_API_HOST + "/applications/forms"
    SUBMIT_APPLICATION_ENDPOINT = APPLICATION_STORE_API_HOST + "/applications/{application_id}/submit"
    FEEDBACK_ENDPOINT = APPLICATION_STORE_API_HOST + "/application/feedback"
    END_OF_APP_SURVEY_FEEDBACK_ENDPOINT = APPLICATION_STORE_API_HOST + "/application/end_of_application_survey_data"
    RESEARCH_SURVEY_ENDPOINT = APPLICATION_STORE_API_HOST + "/application/research"

    FUND_STORE_API_HOST = environ.get("FUND_STORE_API_HOST", TEST_FUND_STORE_API_HOST)
    GET_ALL_FUNDS_ENDPOINT = FUND_STORE_API_HOST + "/funds"
    GET_FUND_DATA_ENDPOINT = FUND_STORE_API_HOST + "/funds/{fund_id}"
    GET_ALL_ROUNDS_FOR_FUND_ENDPOINT = FUND_STORE_API_HOST + "/funds/{fund_id}/rounds"
    GET_ROUND_DATA_FOR_FUND_ENDPOINT = FUND_STORE_API_HOST + "/funds/{fund_id}/rounds/{round_id}"
    GET_FUND_DATA_BY_SHORT_NAME_ENDPOINT = FUND_STORE_API_HOST + "/funds/{fund_short_name}"
    GET_ROUND_DATA_BY_SHORT_NAME_ENDPOINT = FUND_STORE_API_HOST + "/funds/{fund_short_name}/rounds/{round_short_name}"

    GET_APPLICATION_DISPLAY_FOR_FUND_ENDPOINT = (
        FUND_STORE_API_HOST + "/funds/{fund_id}/rounds/{round_id}/sections/application?language={language}"
    )

    FORMS_TEST_HOST = "http://localhost:3009"
    FORMS_SERVICE_NAME = environ.get("FORMS_SERVICE_NAME", "xgov_forms_service")
    FORMS_SERVICE_PUBLIC_HOST = environ.get("FORMS_SERVICE_PUBLIC_HOST", FORMS_TEST_HOST)
    FORMS_SERVICE_PREVIEW_HOST = environ.get("FORMS_SERVICE_PREVIEW_HOST", FORMS_TEST_HOST)
    FORMS_SERVICE_JSONS_PATH = "form_jsons"

    FORMS_SERVICE_PRIVATE_HOST = getenv("FORMS_SERVICE_PRIVATE_HOST")

    FORM_GET_REHYDRATION_TOKEN_URL = (FORMS_SERVICE_PRIVATE_HOST or FORMS_SERVICE_PUBLIC_HOST) + "/session/{form_name}"

    FORM_REHYDRATION_URL = (FORMS_SERVICE_PRIVATE_HOST or FORMS_SERVICE_PUBLIC_HOST) + "/session/{rehydration_token}"

    # Content Security Policy
    SECURE_CSP = {
        "default-src": "'self'",
        "script-src": [
            "'self'",
            "'sha256-+6WnXIl4mbFTCARd8N3COQmT3bJJmo32N8q8ZSQAIcU='",
            "'sha256-l1eTVSK8DTnK8+yloud7wZUqFrI0atVo6VlC6PJvYaQ='",
            "'sha256-z+p4q2n8BOpGMK2/OMOXrTYmjbeEhWQQHC3SF/uMOyg='",
            "'sha256-RgdCrr7A9yqYVstE6QiM/9RNRj4bYipcUa2C2ywQT1A='",
            "https://tagmanager.google.com",
            "https://www.googletagmanager.com",
            "https://*.google-analytics.com",
        ],
        "connect-src": [
            "'self'",
            "https://*.google-analytics.com",
        ],  # APPLICATION_STORE_API_HOST_PUBLIC,
        "img-src": ["data:", "'self'", "https://ssl.gstatic.com"],
    }

    # Talisman Config
    FSD_REFERRER_POLICY = "strict-origin-when-cross-origin"
    FSD_SESSION_COOKIE_SAMESITE = "Strict"
    FSD_PERMISSIONS_POLICY = {"interest-cohort": "()"}
    FSD_DOCUMENT_POLICY = {}
    FSD_FEATURE_POLICY = {
        "microphone": "'none'",
        "camera": "'none'",
        "geolocation": "'none'",
    }

    DENY = "DENY"
    SAMEORIGIN = "SAMEORIGIN"
    ALLOW_FROM = "ALLOW-FROM"
    ONE_YEAR_IN_SECS = 31556926
    FORCE_HTTPS = False

    TALISMAN_SETTINGS = {
        "feature_policy": FSD_FEATURE_POLICY,
        "permissions_policy": FSD_PERMISSIONS_POLICY,
        "document_policy": FSD_DOCUMENT_POLICY,
        "force_https": FORCE_HTTPS,
        "force_https_permanent": False,
        "force_file_save": False,
        "frame_options": "SAMEORIGIN",
        "frame_options_allow_from": None,
        "strict_transport_security": True,
        "strict_transport_security_preload": True,
        "strict_transport_security_max_age": ONE_YEAR_IN_SECS,
        "strict_transport_security_include_subdomains": True,
        "content_security_policy": SECURE_CSP,
        "content_security_policy_report_uri": None,
        "content_security_policy_report_only": False,
        # "content_security_policy_nonce_in": None,
        "referrer_policy": FSD_REFERRER_POLICY,
        "session_cookie_secure": True,
        "session_cookie_http_only": True,
        "session_cookie_samesite": FSD_SESSION_COOKIE_SAMESITE,
        "x_content_type_options": True,
        "x_xss_protection": True,
        "content_security_policy_nonce_in": ["script-src"],
    }

    USE_LOCAL_DATA = strtobool(getenv("USE_LOCAL_DATA", "False"))

    # Redis Feature Toggle Configuration
    REDIS_INSTANCE_URI = getenv("REDIS_INSTANCE_URI", "redis://localhost:6379")
    TOGGLES_URL = REDIS_INSTANCE_URI + "/0"
    FEATURE_CONFIG = CommonConfig.dev_feature_configuration

    # LRU cache settings
    LRU_CACHE_TIME = int(environ.get("LRU_CACHE_TIME", 3600))  # in seconds

    MIGRATION_BANNER_ENABLED = getenv("MIGRATION_BANNER_ENABLED", False)
