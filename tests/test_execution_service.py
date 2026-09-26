import pytest
import shutil
import subprocess
from pathlib import Path
from backend.tools import get_workspace_root
from backend.services.execution_service import ExecutionService


@pytest.fixture
def temp_workspace(tmp_path):
    """Fixture providing a temporary workspace directory."""
    ws_root = get_workspace_root()
    ws_name = f"test_svc_env_{tmp_path.name}"
    ws_dir = ws_root / ws_name
    ws_dir.mkdir(parents=True, exist_ok=True)
    yield ws_name
    if ws_dir.exists():
        shutil.rmtree(ws_dir, ignore_errors=True)


@pytest.fixture
def temp_git_workspace(tmp_path):
    """Fixture providing a temporary Git workspace directory."""
    ws_root = get_workspace_root()
    ws_name = f"test_svc_git_env_{tmp_path.name}"
    ws_dir = ws_root / ws_name
    ws_dir.mkdir(parents=True, exist_ok=True)

    subprocess.run(["git", "init"], cwd=str(ws_dir), check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(ws_dir), check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(ws_dir), check=True)

    yield ws_name

    if ws_dir.exists():
        shutil.rmtree(ws_dir, ignore_errors=True)


def test_execution_service_file_ops(temp_workspace):
    svc = ExecutionService()
    
    # write_file
    res_write = svc.write_file(temp_workspace, "sample.py", "x = 42\n")
    assert res_write["success"] is True

    # read_file
    content = svc.read_file(temp_workspace, "sample.py")
    assert content == "x = 42\n"

    # list_files
    files = svc.list_files(temp_workspace)
    assert "sample.py" in files


def test_execution_service_search_code(temp_workspace):
    svc = ExecutionService()
    svc.write_file(temp_workspace, "app.py", "def main():\n    print('hello')\n")
    results = svc.search_code(temp_workspace, "def main")
    assert len(results) == 1
    assert results[0]["file"] == "app.py"


def test_execution_service_run_python(temp_workspace):
    svc = ExecutionService()
    svc.write_file(temp_workspace, "run.py", "print('SERVICE_OK')")
    res = svc.run_python(temp_workspace, "python3 run.py")
    assert res["success"] is True
    assert "SERVICE_OK" in res["stdout"]


def test_execution_service_run_tests(temp_workspace):
    svc = ExecutionService()
    svc.write_file(temp_workspace, "test_sample.py", "def test_ok(): assert True")
    res = svc.run_tests(temp_workspace)
    assert res["success"] is True


def test_execution_service_patch_and_rollback(temp_workspace):
    svc = ExecutionService()
    svc.write_file(temp_workspace, "target.py", "original content")

    # apply_file_change
    patch_res = svc.apply_file_change(temp_workspace, "target.py", "modified content")
    assert patch_res["success"] is True
    assert svc.read_file(temp_workspace, "target.py") == "modified content"

    # rollback_change
    rollback_res = svc.rollback_change(temp_workspace, "target.py", patch_res["backup_content"])
    assert rollback_res["success"] is True
    assert svc.read_file(temp_workspace, "target.py") == "original content"


def test_execution_service_git_ops(temp_git_workspace):
    svc = ExecutionService()
    svc.write_file(temp_git_workspace, "repo.py", "initial")
    
    ws_dir = get_workspace_root() / temp_git_workspace
    subprocess.run(["git", "add", "."], cwd=str(ws_dir), check=True)
    subprocess.run(["git", "commit", "-m", "init"], cwd=str(ws_dir), check=True)

    svc.write_file(temp_git_workspace, "repo.py", "modified")

    status_res = svc.git_status(temp_git_workspace)
    assert status_res["success"] is True
    assert "repo.py" in status_res["files_changed"]

    diff_res = svc.git_diff(temp_git_workspace)
    assert diff_res["success"] is True
    assert "+modified" in diff_res["diff"]


def test_execution_service_execute_tool(temp_workspace):
    svc = ExecutionService()

    # Dynamic execute_tool call for write_file
    res_write = svc.execute_tool("write_file", workspace=temp_workspace, file_path="dynamic.txt", content="dyn_data")
    assert res_write["success"] is True

    # Dynamic execute_tool call for read_file
    res_read = svc.execute_tool("read_file", workspace=temp_workspace, file_path="dynamic.txt")
    assert res_read == "dyn_data"


def test_execution_service_unknown_tool():
    svc = ExecutionService()
    res = svc.execute_tool("non_existent_tool_123", workspace="demo_project")
    assert res["success"] is False
    assert "Unknown tool" in res["error"]


def test_execution_service_tool_descriptions():
    svc = ExecutionService()
    descs = svc.get_tool_descriptions()
    assert isinstance(descs, list)
    names = [d["name"] for d in descs]
    assert "list_files" in names
    assert "read_file" in names
    assert "run_tests" in names
    assert "git_diff" in names
