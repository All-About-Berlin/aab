import logging
import secrets

from pydantic import SecretStr, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

logger = logging.getLogger(__name__)

PLACEHOLDER_VALUES = frozenset({"...", "your-secret-key-here", "changeme", "secret", ""})
MIN_SECRET_KEY_LENGTH = 32


def _validate_secret(value: SecretStr | None, name: str) -> str | None:
    """Validate a secret key value. Returns the stripped value or None if not set/placeholder."""
    if value is None:
        return None
    stripped = value.get_secret_value().strip()
    if not stripped or stripped in PLACEHOLDER_VALUES:
        return None
    # Reject Django's own insecure key convention — catches old hardcoded keys from git history
    if stripped.startswith("django-insecure"):
        return None
    if len(stripped) < MIN_SECRET_KEY_LENGTH:
        raise ValueError(
            f"{name} is too short (got {len(stripped)}, min {MIN_SECRET_KEY_LENGTH} chars). "
            "Generate a real key with: python -c "
            '"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"'
        )
    return stripped


class ServiceConfig(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    django_secret_key: SecretStr | None = None
    django_secret_key_previous: SecretStr | None = None
    buttondown_api_key: SecretStr | None = None
    mailgun_api_key: SecretStr | None = None
    remote_db_backups_path: str | None = None
    debug: bool = False

    @model_validator(mode="after")
    def ensure_secret_keys(self):
        key_value = _validate_secret(self.django_secret_key, "DJANGO_SECRET_KEY")

        # Normalize whitespace: write back the stripped value so get_secret_value() returns clean data
        if key_value:
            self.django_secret_key = SecretStr(key_value)

        # Validate fallback key with the same rules — a placeholder or weak fallback
        # is worse than no fallback because it keeps the trust boundary open.
        prev_value = _validate_secret(self.django_secret_key_previous, "DJANGO_SECRET_KEY_PREVIOUS")
        if self.django_secret_key_previous and prev_value is None:
            logger.warning("DJANGO_SECRET_KEY_PREVIOUS is set to a placeholder or insecure value — ignoring it")
            self.django_secret_key_previous = None
        elif prev_value:
            self.django_secret_key_previous = SecretStr(prev_value)

        if key_value:
            return self

        if not self.debug:
            raise ValueError(
                "DJANGO_SECRET_KEY is required when DEBUG is not enabled. "
                "Generate one with: python -c "
                '"from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"'
            )

        # Development only: generate an ephemeral key that changes on every restart.
        # Sessions won't persist across restarts — this is intentional to make it
        # obvious that a real key must be set for production.
        self.django_secret_key = SecretStr(f"django-insecure-dev-{secrets.token_urlsafe(32)}")
        logger.warning(
            "DJANGO_SECRET_KEY not set or placeholder — using auto-generated ephemeral key (development only)"
        )
        return self


config = ServiceConfig()
