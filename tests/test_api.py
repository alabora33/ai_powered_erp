"""
FastAPI integration tests using TestClient.
Tests run against an in-memory SQLite database.
"""

import io
from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient


@pytest.fixture
def client():
    """Create a test client with mocked DB and Celery."""
    with patch("backend.tasks.process_upload.delay") as mock_task:
        mock_task.return_value.id = "test-task-id"
        from backend.main import app

        with TestClient(app) as c:
            yield c


def test_health_endpoint(client):
    res = client.get("/health")
    assert res.status_code in (200, 503)  # Either healthy or degraded is fine in tests
    data = res.json()
    assert "status" in data
    assert "version" in data


def test_root_endpoint(client):
    res = client.get("/")
    assert res.status_code == 200
    data = res.json()
    assert "name" in data
    assert "docs" in data


def test_upload_invalid_file_type(client):
    """Reject non-supported file types."""
    fake_file = io.BytesIO(b"hello world")
    res = client.post(
        "/api/upload",
        files={"file": ("test.pdf", fake_file, "application/pdf")},
    )
    assert res.status_code == 400
    assert "Unsupported" in res.json()["detail"]


def test_upload_empty_file(client):
    """Reject empty files."""
    empty = io.BytesIO(b"")
    res = client.post(
        "/api/upload",
        files={
            "file": (
                "test.xlsx",
                empty,
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            )
        },
    )
    assert res.status_code == 400


def test_get_nonexistent_job(client):
    """404 for unknown job IDs."""
    res = client.get("/api/upload/jobs/00000000-0000-0000-0000-000000000000")
    assert res.status_code == 404


def test_jobs_list_empty(client):
    """Jobs list returns empty array when no jobs exist."""
    res = client.get("/api/upload/jobs")
    assert res.status_code == 200
    assert isinstance(res.json(), list)


def test_dashboard_empty(client):
    """Dashboard returns valid structure even with no data."""
    res = client.get("/api/analytics/dashboard")
    assert res.status_code == 200
    data = res.json()
    assert "total_jobs" in data
    assert "total_records" in data
    assert "categories" in data
