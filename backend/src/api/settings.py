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
    "forum.apps.ForumConfig",  # Listed before allauth so forum's templates override allauth's defaults
    "allauth",
    "allauth.account",
    "forms.apps.FormsConfig",
    "insurance.apps.InsuranceConfig",
    "management.apps.ManagementConfig",
]

MIDDLEWARE = [
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.middleware.security.SecurityMiddleware",
    "allauth.account.middleware.AccountMiddleware",
]

AUTHENTICATION_BACKENDS = [
    "django.contrib.auth.backends.ModelBackend",
    "allauth.account.auth_backends.AuthenticationBackend",
]

ACCOUNT_SIGNUP_FIELDS = ["email*", "username*", "password1*", "password2*"]
ACCOUNT_EMAIL_VERIFICATION = "mandatory"
ACCOUNT_CONFIRM_EMAIL_ON_GET = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_GET = True
ACCOUNT_USERNAME_VALIDATORS = "forum.validators.username_validators"
ACCOUNT_ADAPTER = "forum.adapters.ForumAccountAdapter"
ACCOUNT_FORMS = {
    "login": "forum.forms.LoginForm",
    "signup": "forum.forms.SignupForm",
    "reset_password": "forum.forms.ResetPasswordForm",
    "reset_password_from_key": "forum.forms.ResetPasswordKeyForm",
}
LOGIN_REDIRECT_URL = "/forum"
LOGOUT_REDIRECT_URL = "/forum"
ACCOUNT_SIGNUP_REDIRECT_URL = "/forum/rules"

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

_template_loaders = [
    "django.template.loaders.filesystem.Loader",
    "django.template.loaders.app_directories.Loader",
]
if not DEBUG:
    _template_loaders = [("django.template.loaders.cached.Loader", _template_loaders)]

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [Path("/var/frontend-output")],
        "OPTIONS": {
            "loaders": _template_loaders,
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
