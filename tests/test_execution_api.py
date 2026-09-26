import pytest
from fastapi.testclient import TestClient
from backend.api.main import app
from backend.tools import read_file, write_file

client = TestClient(app)


@pytest.fixture(autouse=True)
def ensure_demo_project_clean():
    """Fixture ensuring workspace/demo_project starts and ends in initial buggy state."""
    buggy_code = (
        'def calculate_discount(price, discount_percent):\n'
        '    """Calculate final price after percentage discount."""\n'
        '    return price - discount_percent\n'
    )
    # Restore before test
    write_file("demo_project", "calculator.py", buggy_code)
    yield
    # Restore after test
    write_file("demo_project", "calculator.py", buggy_code)


def test_get_tools():
    response = client.get("/api/execution/tools")
    assert response.status_code == 200
    data = response.json()
    assert "tools" in data
    names = [t["name"] for t in data["tools"]]
    assert "list_files" in names
    assert "run_tests" in names
    assert "git_diff" in names


def test_get_files():
    response = client.get("/api/execution/files/demo_project")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "calculator.py" in data["files"]


def test_get_file():
    response = client.get("/api/execution/file/demo_project/calculator.py")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "calculate_discount" in data["content"]


def test_search_code():
    response = client.get("/api/execution/search/demo_project?q=discount")
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert len(data["results"]) > 0
    assert data["results"][0]["file"] == "calculator.py"


def test_run_tests():
    response = client.post("/api/execution/test/demo_project", json={"timeout": 30})
    assert response.status_code == 200
    data = response.json()
    # Demo project initially fails
    assert data["success"] is False
    assert data["return_code"] == 1
    assert "assert 990 == 900" in data["stdout"] or "990" in data["stdout"]


def test_run_python():
    response = client.post("/api/execution/run-python/demo_project", json={"command": "python -c \"print('API_RUN_OK')\"", "timeout": 10})
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert "API_RUN_OK" in data["stdout"]


def test_git_status():
    response = client.get("/api/execution/git-status/demo_project")
    assert response.status_code == 200
    data = response.json()
    assert "success" in data


def test_git_diff():
    response = client.get("/api/execution/git-diff/demo_project")
    assert response.status_code == 200
    data = response.json()
    assert "diff" in data


def test_apply_change_and_rollback():
    fixed_code = (
        'def calculate_discount(price, discount_percent):\n'
        '    """Calculate final price after percentage discount."""\n'
        '    discount_amount = price * discount_percent / 100\n'
        '    return price - discount_amount\n'
    )
    
    # 1. Apply fix
    res_apply = client.post("/api/execution/apply-change/demo_project/calculator.py", json={"content": fixed_code})
    assert res_apply.status_code == 200
    data_apply = res_apply.json()
    assert data_apply["success"] is True
    assert data_apply["backup_content"] is not None

    # 2. Verify test passes with fix
    res_test = client.post("/api/execution/test/demo_project")
    assert res_test.status_code == 200
    assert res_test.json()["success"] is True

    # 3. Rollback change
    res_rollback = client.post("/api/execution/rollback/demo_project/calculator.py", json={"backup_content": data_apply["backup_content"]})
    assert res_rollback.status_code == 200
    assert res_rollback.json()["success"] is True

    # 4. Verify test fails again after rollback
    res_test_again = client.post("/api/execution/test/demo_project")
    assert res_test_again.status_code == 200
    assert res_test_again.json()["success"] is False


def test_generic_tool_execution():
    # Test valid tool
    response = client.post("/api/execution/tool/read_file", json={"workspace": "demo_project", "file_path": "calculator.py"})
    assert response.status_code == 200
    assert "calculate_discount" in response.json()

    # Test unknown tool
    response_unknown = client.post("/api/execution/tool/invalid_unknown_tool", json={"workspace": "demo_project"})
    assert response_unknown.status_code == 400
    assert "Unknown tool" in response_unknown.json()["detail"]


def test_path_traversal_rejection():
    # Test path traversal via generic tool API
    response = client.post("/api/execution/tool/read_file", json={"workspace": "demo_project", "file_path": "../../etc/passwd"})
    assert response.status_code == 400
    assert "escapes workspace boundary" in response.json()["detail"] or "Workspace error" in response.json()["detail"]
