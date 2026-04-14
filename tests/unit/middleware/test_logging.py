import pytest
import inspect
from backend.app.middleware.logging import RequestLoggingMiddleware


def test_logging_middleware_does_not_log_headers():
    """Logging middleware must not log dict(request.headers)"""
    source = inspect.getsource(RequestLoggingMiddleware.dispatch)
    assert 'dict(request.headers)' not in source, \
        "Middleware must not log dict(request.headers)"
    assert 'request.headers' not in source, \
        "Middleware must not log request.headers in any form"


def test_logging_middleware_logs_method_and_path():
    """Middleware should log request method and path"""
    source = inspect.getsource(RequestLoggingMiddleware.dispatch)
    assert 'request.method' in source, \
        "Middleware should log request method"
    assert 'request.url.path' in source, \
        "Middleware should log request path"
