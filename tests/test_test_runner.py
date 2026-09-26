import pytest
import shutil
from pathlib import Path
from backend.tools import (
    get_workspace_root,
    write_file,
    run_tests,
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Fixture creating a temporary workspace directory inside workspace root."""
    ws_root = get_workspace_root()
    ws_name = f"test_runner_env_{tmp_path.name}"
    ws_dir = ws_root / ws_name
    ws_dir.mkdir(parents=True, exist_ok=True)
    yield ws_name
    if ws_dir.exists():
        shutil.rmtree(ws_dir, ignore_errors=True)


def test_passing_pytest_project(temp_workspace):
    write_file(temp_workspace, "math_utils.py", "def add(a, b):\n    return a + b\n")
    write_file(temp_workspace, "test_math_utils.py", "from math_utils import add\ndef test_add():\n    assert add(2, 3) == 5\n")
    
    res = run_tests(temp_workspace)
    assert res["success"] is True
    assert res["return_code"] == 0
    assert res["timed_out"] is False


def test_failing_pytest_project(temp_workspace):
    write_file(temp_workspace, "math_utils.py", "def add(a, b):\n    return a - b\n")
    write_file(temp_workspace, "test_math_utils.py", "from math_utils import add\ndef test_add():\n    assert add(2, 3) == 5\n")
    
    res = run_tests(temp_workspace)
    assert res["success"] is False
    assert res["return_code"] == 1
    assert "assert -1 == 5" in res["stdout"] or "assert" in res["stdout"]


def test_missing_test_or_project(temp_workspace):
    # No test files in workspace
    res = run_tests(temp_workspace)
    assert res["success"] is False
    assert res["return_code"] in (5, -1)  # pytest exit code 5 means no tests collected


def test_invalid_workspace():
    res = run_tests("non_existent_workspace_12345")
    assert res["success"] is False
    assert "does not exist" in res["stderr"]

    res_traversal = run_tests("../../etc")
    assert res_traversal["success"] is False
    assert "Workspace error" in res_traversal["stderr"] or "outside workspace root" in res_traversal["stderr"]


def test_timeout(temp_workspace):
    write_file(temp_workspace, "test_slow.py", "import time\ndef test_sleep():\n    time.sleep(5)\n")
    res = run_tests(temp_workspace, timeout=1)
    assert res["success"] is False
    assert res["timed_out"] is True
    assert res["return_code"] == -1


def test_demo_project_real_failure():
    res = run_tests("demo_project")
    assert res["success"] is False
    assert res["return_code"] == 1
    assert "assert 990 == 900" in res["stdout"] or "990" in res["stdout"]
