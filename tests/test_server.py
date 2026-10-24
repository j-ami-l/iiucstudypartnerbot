"""Tests for unified server.py (Feature D1 single-service deployment)."""

import pytest
from starlette.testclient import TestClient

from server import app


@pytest.fixture
def client():
    # Use with client context to avoid running full lifespan bot polling in unit tests
    return TestClient(app, raise_server_exceptions=False)


def test_healthz_endpoint(client):
    """GET /healthz must return 200 and {'status': 'ok'} without touching DB or AI."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_api_unknown_route_returns_404(client):
    """GET /api/nonexistent should return 404 and not fall back to SPA HTML."""
    response = client.get("/api/nonexistent")
    assert response.status_code == 404


def test_spa_fallback_serves_html_or_placeholder(client):
    """Non-API routes should serve index.html or build placeholder."""
    response = client.get("/dashboard")
    assert response.status_code == 200
    assert "html" in response.headers.get("content-type", "").lower()
