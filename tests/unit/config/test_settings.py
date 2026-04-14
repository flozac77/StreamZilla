import pytest
import os
import sys
import importlib.util
from unittest.mock import patch, mock_open
from pydantic import ValidationError


def load_settings_class():
    """Load Settings class directly without triggering __init__.py"""
    spec = importlib.util.spec_from_file_location(
        "base_config",
        "/srv/13Perso_projet/StreamZilla/backend/app/config/base.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.Settings


def test_session_secret_key_must_be_from_env(tmp_path):
    """SESSION_SECRET_KEY must be provided via .env or environment, never generated"""
    # Create a temporary .env file WITHOUT SESSION_SECRET_KEY
    env_file = tmp_path / ".env"
    env_file.write_text(
        "ENVIRONMENT=test\n"
        "TWITCH_CLIENT_ID=test-id\n"
        "TWITCH_CLIENT_SECRET=test-secret\n"
        "TWITCH_REDIRECT_URI=http://localhost:8000/callback\n"
        "MONGODB_URL=mongodb://test\n"
        "REDIS_URL=redis://test\n"
    )

    # Patch the SettingsConfigDict to use our temp env file
    with patch.dict(os.environ, {}, clear=False):
        os.environ.pop("SESSION_SECRET_KEY", None)
        os.environ.pop("ENVIRONMENT", None)
        os.environ.pop("TWITCH_CLIENT_ID", None)
        os.environ.pop("TWITCH_CLIENT_SECRET", None)
        os.environ.pop("TWITCH_REDIRECT_URI", None)
        os.environ.pop("MONGODB_URL", None)
        os.environ.pop("REDIS_URL", None)

        # Patch the base settings to read from our temp env file
        from pydantic_settings import SettingsConfigDict

        original_init_subclass = None

        # Load Settings class
        spec = importlib.util.spec_from_file_location(
            "base_config",
            "/srv/13Perso_projet/StreamZilla/backend/app/config/base.py"
        )
        module = importlib.util.module_from_spec(spec)

        # Temporarily change the working directory to where our temp .env is
        original_cwd = os.getcwd()
        os.chdir(str(tmp_path))

        try:
            spec.loader.exec_module(module)
            Settings = module.Settings

            with pytest.raises(ValidationError) as exc_info:
                Settings()

            # Verify SESSION_SECRET_KEY is among the missing fields
            assert "SESSION_SECRET_KEY" in str(exc_info.value)
        finally:
            os.chdir(original_cwd)


def test_session_secret_key_can_be_provided(tmp_path):
    """SESSION_SECRET_KEY can be provided via environment variable"""
    test_secret = "test-secret-key-12345"

    # Create a temporary .env file WITH SESSION_SECRET_KEY
    env_file = tmp_path / ".env"
    env_file.write_text(
        f"SESSION_SECRET_KEY={test_secret}\n"
        "TWITCH_CLIENT_ID=test-id\n"
        "TWITCH_CLIENT_SECRET=test-secret\n"
        "TWITCH_REDIRECT_URI=http://localhost:8000/callback\n"
        "MONGODB_URL=mongodb://test\n"
        "REDIS_URL=redis://test\n"
    )

    # Change to temp directory and load settings
    original_cwd = os.getcwd()
    os.chdir(str(tmp_path))

    try:
        spec = importlib.util.spec_from_file_location(
            "base_config2",
            "/srv/13Perso_projet/StreamZilla/backend/app/config/base.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        Settings = module.Settings

        settings = Settings()
        assert settings.SESSION_SECRET_KEY == test_secret
    finally:
        os.chdir(original_cwd)
