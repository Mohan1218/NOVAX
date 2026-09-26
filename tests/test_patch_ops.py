import shutil
import pytest
from pathlib import Path
from backend.tools import (
    get_workspace_root,
    write_file,
    read_file,
    create_backup,
    apply_file_change,
    rollback_change,
    restore_file_change,
    PathTraversalError,
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Fixture providing a temporary workspace directory."""
    ws_root = get_workspace_root()
    ws_name = f"test_patch_env_{tmp_path.name}"
    ws_dir = ws_root / ws_name
    ws_dir.mkdir(parents=True, exist_ok=True)
    yield ws_name
    if ws_dir.exists():
        shutil.rmtree(ws_dir, ignore_errors=True)


def test_create_backup_and_apply_change(temp_workspace):
    write_file(temp_workspace, "code.py", "v1 content")
    backup_res = create_backup(temp_workspace, "code.py")
    assert backup_res["success"] is True
    assert backup_res["existed"] is True
    assert backup_res["backup_content"] == "v1 content"

    change_res = apply_file_change(temp_workspace, "code.py", "v2 content")
    assert change_res["success"] is True
    assert read_file(temp_workspace, "code.py") == "v2 content"


def test_rollback_change(temp_workspace):
    # Test rollback existing file
    write_file(temp_workspace, "code.py", "v1 content")
    change_res = apply_file_change(temp_workspace, "code.py", "v2 content")
    
    rollback_res = rollback_change(temp_workspace, "code.py", change_res["backup_content"])
    assert rollback_res["success"] is True
    assert read_file(temp_workspace, "code.py") == "v1 content"


def test_rollback_newly_created_file(temp_workspace):
    # Test rollback newly created file (backup_content is None)
    change_res = apply_file_change(temp_workspace, "new_file.py", "new content")
    assert change_res["existed"] is False
    assert change_res["backup_content"] is None

    rollback_res = rollback_change(temp_workspace, "new_file.py", change_res["backup_content"])
    assert rollback_res["success"] is True
    target = get_workspace_root() / temp_workspace / "new_file.py"
    assert not target.exists()


def test_patch_path_traversal_protection(temp_workspace):
    with pytest.raises(PathTraversalError):
        create_backup(temp_workspace, "../../etc/passwd")

    with pytest.raises(PathTraversalError):
        apply_file_change(temp_workspace, "../../etc/passwd", "malicious content")

    with pytest.raises(PathTraversalError):
        rollback_change(temp_workspace, "../../etc/passwd", "content")
