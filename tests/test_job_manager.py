import pytest
from backend.services import job_manager


def test_create_and_get_job():
    job_id = job_manager.create_job(workspace="demo_project", bug_report="Test report")
    assert isinstance(job_id, str)
    assert len(job_id) > 0

    job = job_manager.get_job(job_id)
    assert job is not None
    assert job["job_id"] == job_id
    assert job["workspace"] == "demo_project"
    assert job["status"] == "queued"
    assert job["progress"] == 0
    assert job["current_step"] == "waiting"
    assert len(job["logs"]) > 0
    assert "created_at" in job
    assert "updated_at" in job


def test_update_status():
    job_id = job_manager.create_job("demo_project")
    ok = job_manager.update_job(job_id, status="running")
    assert ok is True
    job = job_manager.get_job(job_id)
    assert job["status"] == "running"

    with pytest.raises(ValueError):
        job_manager.update_job(job_id, status="invalid_status_code")


def test_update_progress():
    job_id = job_manager.create_job("demo_project")
    ok = job_manager.set_progress(job_id, 45, "analyzing_logs")
    assert ok is True
    job = job_manager.get_job(job_id)
    assert job["progress"] == 45
    assert job["current_step"] == "analyzing_logs"

    with pytest.raises(ValueError):
        job_manager.set_progress(job_id, 150)

    with pytest.raises(ValueError):
        job_manager.set_progress(job_id, -10)


def test_add_log():
    job_id = job_manager.create_job("demo_project")
    ok = job_manager.add_log(job_id, "Running pytest execution", level="info")
    assert ok is True
    job = job_manager.get_job(job_id)
    messages = [l["message"] for l in job["logs"] if isinstance(l, dict)]
    assert "Running pytest execution" in messages


def test_complete_job():
    job_id = job_manager.create_job("demo_project")
    ok = job_manager.complete_job(job_id, result={"passed": True})
    assert ok is True
    job = job_manager.get_job(job_id)
    assert job["status"] == "completed"
    assert job["progress"] == 100
    assert job["result"] == {"passed": True}


def test_fail_job():
    job_id = job_manager.create_job("demo_project")
    ok = job_manager.fail_job(job_id, error="Test execution timed out")
    assert ok is True
    job = job_manager.get_job(job_id)
    assert job["status"] == "failed"
    assert job["error"] == "Test execution timed out"


def test_cancel_job():
    job_id = job_manager.create_job("demo_project")
    ok = job_manager.cancel_job(job_id)
    assert ok is True
    job = job_manager.get_job(job_id)
    assert job["status"] == "cancelled"


def test_invalid_job_id():
    assert job_manager.get_job("invalid_job_9999") is None
    assert job_manager.add_log("invalid_job_9999", "msg") is False
    assert job_manager.complete_job("invalid_job_9999") is False
    assert job_manager.fail_job("invalid_job_9999", "err") is False
    assert job_manager.cancel_job("invalid_job_9999") is False


def test_timestamp_updates():
    job_id = job_manager.create_job("demo_project")
    job1 = job_manager.get_job(job_id)
    t1 = job1["updated_at"]

    job_manager.add_log(job_id, "New update log")
    job2 = job_manager.get_job(job_id)
    t2 = job2["updated_at"]

    assert t2 >= t1
