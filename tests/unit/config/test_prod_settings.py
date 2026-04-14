import pytest
from pydantic import ValidationError


def _base_env(**overrides):
    env = {
        "TWITCH_CLIENT_ID": "x",
        "TWITCH_CLIENT_SECRET": "y",
        "TWITCH_REDIRECT_URI": "https://example.com/cb",
        "MONGODB_URL": "mongodb://mongo:27017",
        "REDIS_URL": "redis://redis:6379",
        "SESSION_SECRET_KEY": "a" * 40,
        "ALLOWED_ORIGINS": '["https://example.com"]',
    }
    env.update(overrides)
    return env


def _instantiate(monkeypatch, **overrides):
    for k, v in _base_env(**overrides).items():
        monkeypatch.setenv(k, v)
    monkeypatch.setenv("ENVIRONMENT", "prod")
    from backend.app.config.prod import ProdSettings
    return ProdSettings(_env_file=None)


def test_valid_prod_settings(monkeypatch):
    s = _instantiate(monkeypatch)
    assert s.SESSION_SECRET_KEY == "a" * 40
    assert s.ALLOWED_ORIGINS == ["https://example.com"]


def test_reject_placeholder_session_secret(monkeypatch):
    with pytest.raises(ValidationError, match="placeholder"):
        _instantiate(monkeypatch, SESSION_SECRET_KEY="dev-secret-key")


def test_reject_short_session_secret(monkeypatch):
    with pytest.raises(ValidationError, match="32 characters"):
        _instantiate(monkeypatch, SESSION_SECRET_KEY="short")


def test_reject_empty_allowed_origins(monkeypatch):
    with pytest.raises(ValidationError, match="ALLOWED_ORIGINS"):
        _instantiate(monkeypatch, ALLOWED_ORIGINS="[]")


def test_missing_required_field_fails_fast(monkeypatch):
    for k, v in _base_env().items():
        if k == "MONGODB_URL":
            continue
        monkeypatch.setenv(k, v)
    monkeypatch.setenv("ENVIRONMENT", "prod")
    monkeypatch.delenv("MONGODB_URL", raising=False)
    from backend.app.config.prod import ProdSettings
    with pytest.raises(ValidationError, match="MONGODB_URL"):
        ProdSettings(_env_file=None)
