from datetime import date
from pathlib import Path
import os
import sys

IS_RUNNING_TESTS = len(sys.argv) > 1 and sys.argv[1] == "test"


BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = "django-insecure-rm#p9c7f!%q1&=-l+m6lx^9=cl2f301=+d3eu0n3x^yfy1yg51"

BUTTONDOWN_API_KEY = os.environ.get("BUTTONDOWN_API_KEY")
MAILGUN_API_KEY = os.environ.get("MAILGUN_API_KEY")
DEBUG = bool(int(os.environ.get("DEBUG", "0")))
DEBUG_EMAILS = DEBUG  # Print emails instead of sending them

# When set to a (start_date, end_date) tuple, CustomerNotification emails sent
# on or between those dates use the "Vacation" variant of the template.
SEAMUS_VACATION: tuple | None = (date(2026, 8, 8), date(2026, 8, 18))

ssl_domain = os.environ.get("DOMAIN", "localhost")
services_domain = os.environ.get("SERVICES_DOMAIN", "services.localhost")

ALLOWED_HOSTS = [ssl_domain, services_domain]
CSRF_TRUSTED_ORIGINS = [f"https://{ssl_domain}", f"https://{services_domain}"]

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
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.security.SecurityMiddleware",
]

ROOT_URLCONF = "api.urls"
APPEND_SLASH = True


WSGI_APPLICATION = "api.wsgi.application"

DATABASE_BACKUPS_DIR = Path("/var/db-backups")
REMOTE_DATABASE_BACKUPS_DIR = os.environ.get("REMOTE_DB_BACKUPS_PATH")
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
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework.authentication.BasicAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ),
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
