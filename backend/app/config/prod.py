from pydantic import field_validator

from backend.app.config.base import Settings

# Known placeholder values that must never make it to production.
_WEAK_SECRETS = {
    "",
    "dev-secret-key",
    "dev-secret-key-12345-changeme-in-production",
    "changeme",
    "secret",
}


class ProdSettings(Settings):
    ENVIRONMENT: str = "prod"
    DEBUG: bool = False
    LOG_LEVEL: str = "INFO"

    # Production must explicitly set allowed origins via .env.
    ALLOWED_ORIGINS: list[str] = []

    @field_validator("SESSION_SECRET_KEY")
    @classmethod
    def _session_secret_strong(cls, v: str) -> str:
        if v in _WEAK_SECRETS:
            raise ValueError(
                "SESSION_SECRET_KEY is a known placeholder; set a strong value in .env"
            )
        if len(v) < 32:
            raise ValueError("SESSION_SECRET_KEY must be at least 32 characters long")
        return v

    @field_validator("ALLOWED_ORIGINS")
    @classmethod
    def _origins_not_empty(cls, v: list[str]) -> list[str]:
        if not v:
            raise ValueError(
                "ALLOWED_ORIGINS must be set in production (comma-separated JSON list)"
            )
        return v
