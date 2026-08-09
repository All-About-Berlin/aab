import os

_DOMAIN = os.environ["DOMAIN"]

SECRET_KEY = os.environ["SECRET_KEY"]

TIME_ZONE = "Europe/Berlin"

DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "misago",
        "USER": "misago",
        "HOST": "forum-postgres",
        "PORT": 5432,
    }
}

CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.redis.RedisCache",
        "LOCATION": "redis://forum-redis/1",
    }
}

CELERY_BROKER_URL = "redis://forum-redis/0"

FORCE_SCRIPT_NAME = "/forum"
STATIC_URL = "/forum/static/"
MEDIA_URL = "/forum/media/"

SESSION_COOKIE_PATH = "/forum"
SESSION_COOKIE_NAME = "misago_sessionid"
CSRF_COOKIE_PATH = "/forum"
CSRF_COOKIE_NAME = "misago_csrftoken"

SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
USE_X_FORWARDED_HOST = True

ALLOWED_HOSTS = [_DOMAIN]
CSRF_TRUSTED_ORIGINS = [f"https://{_DOMAIN}"]

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
        },
    },
    "root": {
        "handlers": ["console"],
        "level": "INFO",
    },
}
