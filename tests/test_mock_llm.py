import pytest
from typing import Dict, Any
from backend.services.agent_interface import AgentBackendInterface
from backend.agent.analyzer import LLMAnalyzer
from backend.agent.orchestrator import AutonomousDebuggerAgent
from backend.tools import write_file, read_file, get_workspace_root
import shutil


@pytest.fixture
def mock_interface():
    return AgentBackendInterface()


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


class CustomMockAnalyzer(LLMAnalyzer):
    """
    Configurable Mock LLM Analyzer to test specific scenario behaviors.
    """
    def __init__(self, responses: list):
        super().__init__(mock_mode=True)
        self.responses = responses
        self.call_count = 0

    def analyze_bug_and_generate_fix(self, *args, **kwargs) -> Dict[str, Any]:
        if self.call_count < len(self.responses):
            res = self.responses[self.call_count]
            self.call_count += 1
            return res
        return {"success": False, "error": "No more mock responses configured"}


def test_scenario_1_success_on_first_try(mock_interface):
    """Scenario 1: Bug -> diagnosis -> fix -> tests pass."""
    correct_fix = (
        'def calculate_discount(price, discount_percent):\n'
        '    """Calculate final price after percentage discount."""\n'
        '    discount_amount = price * discount_percent / 100\n'
        '    return price - discount_amount\n'
    )
    mock_responses = [
        {
            "success": True,
            "diagnosis": "Subtracted discount percent directly instead of percentage value.",
            "proposed_changes": [{"file": "calculator.py", "content": correct_fix}]
        }
    ]
    analyzer = CustomMockAnalyzer(mock_responses)
    agent = AutonomousDebuggerAgent(interface=mock_interface, analyzer=analyzer)

    job = mock_interface.create_job("demo_project")
    res = agent.run_debug_job(job["job_id"], "demo_project", "Discount bug")

    assert res["success"] is True
    assert res["result"]["verified"] is True
    assert res["result"]["retries"] == 1
    assert mock_interface.get_job(job["job_id"])["status"] == "completed"


def test_scenario_2_retry_then_success(mock_interface):
    """Scenario 2: Bug -> bad fix -> tests fail -> second fix -> tests pass."""
    bad_fix = "def calculate_discount(price, discount_percent):\n    return price * 99\n"
    good_fix = (
        'def calculate_discount(price, discount_percent):\n'
        '    """Calculate final price after percentage discount."""\n'
        '    discount_amount = price * discount_percent / 100\n'
        '    return price - discount_amount\n'
    )
    mock_responses = [
        {
            "success": True,
            "diagnosis": "Bad fix attempt 1.",
            "proposed_changes": [{"file": "calculator.py", "content": bad_fix}]
        },
        {
            "success": True,
            "diagnosis": "Good fix attempt 2.",
            "proposed_changes": [{"file": "calculator.py", "content": good_fix}]
        }
    ]
    analyzer = CustomMockAnalyzer(mock_responses)
    agent = AutonomousDebuggerAgent(interface=mock_interface, analyzer=analyzer)

    job = mock_interface.create_job("demo_project")
    res = agent.run_debug_job(job["job_id"], "demo_project", "Discount bug")

    assert res["success"] is True
    assert res["result"]["retries"] == 2
    assert mock_interface.get_job(job["job_id"])["status"] == "completed"


def test_scenario_3_max_retries_exceeded(mock_interface):
    """Scenario 3: Bug -> fix -> tests continue failing -> 3 retries -> FAILED."""
    bad_fix = "def calculate_discount(price, discount_percent):\n    return price * 0\n"
    mock_responses = [
        {"success": True, "diagnosis": "Bad 1", "proposed_changes": [{"file": "calculator.py", "content": bad_fix}]},
        {"success": True, "diagnosis": "Bad 2", "proposed_changes": [{"file": "calculator.py", "content": bad_fix}]},
        {"success": True, "diagnosis": "Bad 3", "proposed_changes": [{"file": "calculator.py", "content": bad_fix}]},
    ]
    analyzer = CustomMockAnalyzer(mock_responses)
    agent = AutonomousDebuggerAgent(interface=mock_interface, analyzer=analyzer)

    job = mock_interface.create_job("demo_project")
    res = agent.run_debug_job(job["job_id"], "demo_project", "Discount bug")

    assert res["success"] is False
    assert "maximum retry limit" in res["error"]
    assert mock_interface.get_job(job["job_id"])["status"] == "failed"


def test_scenario_4_malformed_llm_response(mock_interface):
    """Scenario 4: LLM returns malformed response -> clean failure."""
    mock_responses = [
        {"success": False, "error": "JSONDecodeError: Expecting value at line 1 column 1"}
    ]
    analyzer = CustomMockAnalyzer(mock_responses)
    agent = AutonomousDebuggerAgent(interface=mock_interface, analyzer=analyzer)

    job = mock_interface.create_job("demo_project")
    res = agent.run_debug_job(job["job_id"], "demo_project", "Discount bug")

    assert res["success"] is False
    assert "JSONDecodeError" in res["error"]
    assert mock_interface.get_job(job["job_id"])["status"] == "failed"


def test_scenario_5_tool_execution_error(mock_interface):
    """Scenario 5: Non-existent workspace -> clean error handling."""
    analyzer = LLMAnalyzer(mock_mode=True)
    agent = AutonomousDebuggerAgent(interface=mock_interface, analyzer=analyzer)

    ws_name = "non_existent_workspace_12345"
    job = mock_interface.create_job(ws_name)
    try:
        res = agent.run_debug_job(job["job_id"], ws_name, "Bug")
        assert res["success"] is False
        assert "error" in res
        assert mock_interface.get_job(job["job_id"])["status"] == "failed"
    finally:
        ws_path = get_workspace_root() / ws_name
        if ws_path.exists():
            shutil.rmtree(ws_path, ignore_errors=True)

