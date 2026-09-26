import pytest
from fastapi.testclient import TestClient
from backend.api.main import app

client = TestClient(app)


def test_create_job_api():
    response = client.post("/api/jobs", json={"workspace": "demo_project"})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "job" in data
    assert data["job"]["workspace"] == "demo_project"
    assert data["job"]["status"] == "queued"
    assert data["job"]["progress"] == 0


def test_get_job_api():
    res_create = client.post("/api/jobs", json={"workspace": "demo_project"})
    job_id = res_create.json()["job"]["job_id"]

    response = client.get(f"/api/jobs/{job_id}")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["job"]["job_id"] == job_id


def test_add_log_api():
    res_create = client.post("/api/jobs", json={"workspace": "demo_project"})
    job_id = res_create.json()["job"]["job_id"]

    response = client.post(f"/api/jobs/{job_id}/log", json={"message": "Starting debug run", "level": "info"})
    assert response.status_code == 200
    data = response.json()
    messages = [l["message"] for l in data["job"]["logs"] if isinstance(l, dict)]
    assert "Starting debug run" in messages


def test_update_progress_api():
    res_create = client.post("/api/jobs", json={"workspace": "demo_project"})
    job_id = res_create.json()["job"]["job_id"]

    response = client.post(f"/api/jobs/{job_id}/progress", json={"progress": 25, "current_step": "analyzing"})
    assert response.status_code == 200
    data = response.json()
    assert data["job"]["progress"] == 25
    assert data["job"]["current_step"] == "analyzing"


def test_complete_job_api():
    res_create = client.post("/api/jobs", json={"workspace": "demo_project"})
    job_id = res_create.json()["job"]["job_id"]

    response = client.post(f"/api/jobs/{job_id}/complete", json={"result": {"tests_passed": True}})
    assert response.status_code == 200
    data = response.json()
    assert data["job"]["status"] == "completed"
    assert data["job"]["progress"] == 100
    assert data["job"]["result"] == {"tests_passed": True}


def test_fail_job_api():
    res_create = client.post("/api/jobs", json={"workspace": "demo_project"})
    job_id = res_create.json()["job"]["job_id"]

    response = client.post(f"/api/jobs/{job_id}/fail", json={"error": "Maximum retries exceeded"})
    assert response.status_code == 200
    data = response.json()
    assert data["job"]["status"] == "failed"
    assert data["job"]["error"] == "Maximum retries exceeded"


def test_invalid_job_id_api():
    invalid_id = "non_existent_job_12345"
    assert client.get(f"/api/jobs/{invalid_id}").status_code == 404
    assert client.post(f"/api/jobs/{invalid_id}/log", json={"message": "x"}).status_code == 404
    assert client.post(f"/api/jobs/{invalid_id}/progress", json={"progress": 50}).status_code == 404
    assert client.post(f"/api/jobs/{invalid_id}/complete").status_code == 404
    assert client.post(f"/api/jobs/{invalid_id}/fail", json={"error": "err"}).status_code == 404
