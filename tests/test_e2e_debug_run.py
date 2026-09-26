import time
import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.tools import write_file, read_file
from backend.agent.analyzer import LLMAnalyzer
from backend.agent.orchestrator import AutonomousDebuggerAgent

client = TestClient(app)


@pytest.fixture(autouse=True)
def clean_demo_project():
    buggy_code = (
        'def calculate_discount(price, discount_percent):\n'
        '    """Calculate final price after percentage discount."""\n'
        '    return price - discount_percent\n'
    )
    write_file("demo_project", "calculator.py", buggy_code)
    yield
    write_file("demo_project", "calculator.py", buggy_code)


def test_e2e_debug_run_mock_llm(monkeypatch):
    """
    End-to-end integration test verifying:
    1. POST /api/debug/run initiates background job.
    2. Background worker executes AutonomousDebuggerAgent with Mock LLM.
    3. GET /api/jobs/{job_id} reflects complete debugging flow to status=completed.
    """

    # Force mock mode on default agent background runner
    def mock_background_runner(job_id: str, workspace: str, bug_report: str):
        analyzer = LLMAnalyzer(mock_mode=True)
        agent = AutonomousDebuggerAgent(analyzer=analyzer)
        agent.run_debug_job(job_id, workspace, bug_report)

    monkeypatch.setattr("backend.api.main._run_agent_background", mock_background_runner)

    # 1. Post debug run request
    res = client.post("/api/debug/run", json={"workspace": "demo_project", "bug_report": "Discount bug"})
    assert res.status_code == 200
    data = res.json()
    assert data["success"] is True
    job_id = data["job_id"]

    # 2. Poll GET /api/jobs/{job_id} until completion (or max timeout)
    max_wait = 10
    start_time = time.time()
    job_state = None

    while time.time() - start_time < max_wait:
        res_job = client.get(f"/api/jobs/{job_id}")
        assert res_job.status_code == 200
        job_state = res_job.json()["job"]
        if job_state["status"] in ("completed", "failed"):
            break
        time.sleep(0.1)

    # 3. Assertions
    assert job_state is not None
    assert job_state["status"] == "completed"
    assert job_state["progress"] == 100
    assert job_state["result"]["verified"] is True
    assert job_state["result"]["tests_passed"] is True
