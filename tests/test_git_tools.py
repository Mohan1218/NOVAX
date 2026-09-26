import shutil
import subprocess
import pytest
from pathlib import Path
from backend.tools import (
    get_workspace_root,
    write_file,
    git_status,
    git_diff,
)


@pytest.fixture
def temp_git_workspace(tmp_path):
    """Fixture providing a temporary workspace directory initialized as a Git repository."""
    ws_root = get_workspace_root()
    ws_name = f"test_git_env_{tmp_path.name}"
    ws_dir = ws_root / ws_name
    ws_dir.mkdir(parents=True, exist_ok=True)

    # Initialize git inside the temporary workspace
    subprocess.run(["git", "init"], cwd=str(ws_dir), stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    subprocess.run(["git", "config", "user.name", "Test User"], cwd=str(ws_dir), check=True)
    subprocess.run(["git", "config", "user.email", "test@example.com"], cwd=str(ws_dir), check=True)

    yield ws_name

    if ws_dir.exists():
        shutil.rmtree(ws_dir, ignore_errors=True)


@pytest.fixture
def temp_nongit_workspace(tmp_path):
    """Fixture providing a temporary workspace directory without a Git repository."""
    ws_root = get_workspace_root()
    ws_name = f"test_nongit_env_{tmp_path.name}"
    ws_dir = ws_root / ws_name
    ws_dir.mkdir(parents=True, exist_ok=True)

    yield ws_name

    if ws_dir.exists():
        shutil.rmtree(ws_dir, ignore_errors=True)


def test_nongit_workspace(temp_nongit_workspace):
    res_status = git_status(temp_nongit_workspace)
    assert res_status["success"] is False
    assert "not a Git repository" in res_status["message"]

    res_diff = git_diff(temp_nongit_workspace)
    assert res_diff["success"] is False
    assert "not a Git repository" in res_diff["message"]


def test_git_status_and_diff(temp_git_workspace):
    # Create initial file & commit
    write_file(temp_git_workspace, "sample.py", "print('initial')\n")
    ws_path = get_workspace_root() / temp_git_workspace
    subprocess.run(["git", "add", "sample.py"], cwd=str(ws_path), check=True)
    subprocess.run(["git", "commit", "-m", "Initial commit"], cwd=str(ws_path), check=True)

    # Modify file
    write_file(temp_git_workspace, "sample.py", "print('modified')\n")

    # Check status
    res_status = git_status(temp_git_workspace)
    assert res_status["success"] is True
    assert "sample.py" in res_status["files_changed"]

    # Check diff
    res_diff = git_diff(temp_git_workspace)
    assert res_diff["success"] is True
    assert "sample.py" in res_diff["files_changed"]
    assert "-print('initial')" in res_diff["diff"]
    assert "+print('modified')" in res_diff["diff"]


def test_path_traversal_protection():
    res_status = git_status("../../etc")
    assert res_status["success"] is False
    assert "Workspace error" in res_status["message"] or "outside workspace root" in res_status["message"]

    res_diff = git_diff("../../etc")
    assert res_diff["success"] is False
    assert "Workspace error" in res_diff["message"] or "outside workspace root" in res_diff["message"]
