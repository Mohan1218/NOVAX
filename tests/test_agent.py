import pytest
from backend.services.agent_interface import AgentBackendInterface
from backend.agent.analyzer import LLMAnalyzer, clean_json_text
from backend.agent.orchestrator import AutonomousDebuggerAgent, MAX_RETRIES
from backend.tools import write_file


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


def test_agent_initialization():
    interface = AgentBackendInterface()
    analyzer = LLMAnalyzer(mock_mode=True)
    agent = AutonomousDebuggerAgent(interface=interface, analyzer=analyzer)

    assert agent.interface is interface
    assert agent.analyzer.mock_mode is True


def test_clean_json_text():
    raw1 = "```json\n{\"key\": \"val\"}\n```"
    assert clean_json_text(raw1) == '{"key": "val"}'

    raw2 = "```\n{\"key\": \"val\"}\n```"
    assert clean_json_text(raw2) == '{"key": "val"}'


def test_analyzer_mock_mode():
    analyzer = LLMAnalyzer(mock_mode=True)
    sources = {"calculator.py": "def calculate_discount(price, percent): return price - percent"}
    res = analyzer.analyze_bug_and_generate_fix("Bug report", ["calculator.py"], "1 failed", "", sources)

    assert res["success"] is True
    assert "diagnosis" in res
    assert len(res["proposed_changes"]) == 1


def test_analyzer_missing_api_key(monkeypatch):
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("OPENAI_API_KEY", raising=False)

    analyzer = LLMAnalyzer(provider="gemini", mock_mode=False)
    res = analyzer.analyze_bug_and_generate_fix("Bug report", ["calc.py"], "fail", "", {})

    assert res["success"] is False
    assert "GEMINI_API_KEY environment variable is missing" in res["error"]


def test_agent_retry_limit_constant():
    assert MAX_RETRIES == 3
