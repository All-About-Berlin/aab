from pathlib import Path
from api.config import config
import sys

IS_RUNNING_TESTS = len(sys.argv) > 1 and sys.argv[1] == "test"


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config.django_secret_key.get_secret_value()
# TODO: Remove DJANGO_SECRET_KEY_PREVIOUS from env and this fallback after the first deployment
# window (2+ weeks) once all sessions signed with the old key have expired.
SECRET_KEY_FALLBACKS = (
    [config.django_secret_key_previous.get_secret_value()] if config.django_secret_key_previous else []
)

BUTTONDOWN_API_KEY = config.buttondown_api_key.get_secret_value() if config.buttondown_api_key else None
MAILGUN_API_KEY = config.mailgun_api_key.get_secret_value() if config.mailgun_api_key else None
DEBUG = config.debug
DEBUG_EMAILS = DEBUG  # Print emails instead of sending them
SECURE_SSL_REDIRECT = not DEBUG
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https") if not DEBUG else None
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG

ALLOWED_HOSTS = ["allaboutberlin.com"] if not DEBUG else ["allaboutberlin.com", "localhost"]
CSRF_TRUSTED_ORIGINS = (
    ["https://allaboutberlin.com"] if not DEBUG else ["https://localhost", "https://allaboutberlin.com"]
)

INSTALLED_APPS = [
    "django.contrib.humanize",
    "management.apps.CustomAdminConfig",  # Replaces django.contrib.admin
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.messages",
    "django.contrib.sessions",
    "django.contrib.staticfiles",
    "forms.apps.FormsConfig",
    "insurance.apps.InsuranceConfig",
    "management.apps.ManagementConfig",
    "discussion.apps.DiscussionConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
]

ROOT_URLCONF = "api.urls"
APPEND_SLASH = True


WSGI_APPLICATION = "api.wsgi.application"

DATABASE_BACKUPS_DIR = Path("/var/db-backups")
REMOTE_DATABASE_BACKUPS_DIR = config.remote_db_backups_path
DATABASE_PATH = Path("/var/db/api.db")
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": DATABASE_PATH,
    }
}

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

BASE_URL = "https://allaboutberlin.com"
STATIC_ROOT = Path("/var/www/api/staticfiles")
STATIC_URL = "/admin/static/"

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {"format": "%(asctime)s %(levelname)s [%(name)s:%(lineno)d] %(message)s"},
    },
    "handlers": {
        "console": {
            "level": "CRITICAL" if IS_RUNNING_TESTS else "INFO",
            "class": "logging.StreamHandler",
            "formatter": "default",
        },
    },
    "loggers": {
        "": {
            "handlers": ["console"],
            "level": "CRITICAL" if IS_RUNNING_TESTS else "INFO",
            "propagate": True,
        },
        "django.request": {
            "level": "ERROR",
        },
        "gunicorn": {
            "handlers": ["console"],
            "level": "INFO",
            "propagate": True,
        },
    },
}

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": ("rest_framework.authentication.BasicAuthentication",),
    "DEFAULT_RENDERER_CLASSES": [
        "rest_framework.renderers.JSONRenderer",
    ],
    "EXCEPTION_HANDLER": "forms.views.exception_handler",
    "DEFAULT_PAGINATION_CLASS": "api.pagination.PageNumberPagination",
    "PAGE_SIZE": 10,
}

# Internationalization
LANGUAGE_CODE = "en-us"
TIME_ZONE = "Europe/Berlin"
USE_TZ = True
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
