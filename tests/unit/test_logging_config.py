import logging
import importlib


def test_root_logger_level_defaults_to_info(monkeypatch):
    monkeypatch.delenv("LOG_LEVEL", raising=False)
    from backend.app.config import logging_config
    importlib.reload(logging_config)
    logging_config.setup_logging()
    assert logging.getLogger().level == logging.INFO


def test_root_logger_level_respects_env(monkeypatch):
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    from backend.app.config import logging_config
    importlib.reload(logging_config)
    logging_config.setup_logging()
    assert logging.getLogger().level == logging.DEBUG
