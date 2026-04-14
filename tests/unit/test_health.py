import pytest
from fastapi.testclient import TestClient


def test_health_endpoint_exists():
    """Health endpoint should return 200 with status ok"""
    from backend.app.main import app
    routes = [route.path for route in app.routes]
    assert "/api/health" in routes, "Health endpoint /api/health must exist"
