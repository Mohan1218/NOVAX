import pytest
from pathlib import Path
from backend.tools import (
    get_workspace_root,
    resolve_workspace,
    resolve_path,
    validate_path,
    list_files,
    read_file,
    write_file,
    search_code,
    run_python,
    apply_file_change,
    restore_file_change,
    InvalidWorkspaceError,
    PathTraversalError,
)


@pytest.fixture
def temp_workspace(tmp_path):
    """Fixture providing a temporary workspace directory inside workspace root for tests."""
    ws_root = get_workspace_root()
    ws_name = f"test_env_{tmp_path.name}"
    ws_dir = ws_root / ws_name
    ws_dir.mkdir(parents=True, exist_ok=True)
    yield ws_name
    # Cleanup after test
    if ws_dir.exists():
        import shutil
        shutil.rmtree(ws_dir, ignore_errors=True)


def test_valid_workspace():
    ws_root = get_workspace_root()
    resolved = resolve_workspace("demo_project")
    assert resolved == ws_root / "demo_project"
    assert ws_root in resolved.parents or resolved == ws_root


def test_valid_file_path(temp_workspace):
    validated = validate_path(temp_workspace, "sub/file.py")
    expected = get_workspace_root() / temp_workspace / "sub" / "file.py"
    assert validated == expected.resolve()


def test_path_traversal_rejection(temp_workspace):
    with pytest.raises(PathTraversalError):
        validate_path(temp_workspace, "../../etc/passwd")

    with pytest.raises(PathTraversalError):
        validate_path(temp_workspace, "../other_dir/secret.txt")


def test_absolute_path_outside_workspace_rejection(temp_workspace):
    with pytest.raises(PathTraversalError):
        validate_path(temp_workspace, "/etc/passwd")

    with pytest.raises(InvalidWorkspaceError):
        resolve_workspace("/usr/local/bin")


def test_file_operations(temp_workspace):
    # Test write_file
    res = write_file(temp_workspace, "hello.txt", "Hello World\nBugHunter test")
    assert res["success"] is True
    assert res["file"] == "hello.txt"

    # Test read_file
    content = read_file(temp_workspace, "hello.txt")
    assert "Hello World" in content

    # Test list_files
    write_file(temp_workspace, "dir/nested.py", "print(1)")
    files = list_files(temp_workspace)
    assert "hello.txt" in files
    assert "dir/nested.py" in files


def test_code_search(temp_workspace):
    write_file(temp_workspace, "calc.py", "def add(a, b):\n    return a + b\n")
    results = search_code(temp_workspace, "def add")
    assert len(results) == 1
    assert results[0]["file"] == "calc.py"
    assert results[0]["line"] == 1
    assert "def add" in results[0]["text"]


def test_executor(temp_workspace):
    write_file(temp_workspace, "script.py", "print('EXEC_SUCCESS')")
    res = run_python(temp_workspace, "python3 script.py")
    assert res["success"] is True
    assert res["return_code"] == 0
    assert "EXEC_SUCCESS" in res["stdout"]


def test_patch_ops(temp_workspace):
    # Apply change on existing file
    write_file(temp_workspace, "app.py", "initial code")
    change_res = apply_file_change(temp_workspace, "app.py", "modified code")
    assert change_res["success"] is True
    assert change_res["backup_content"] == "initial code"
    assert read_file(temp_workspace, "app.py") == "modified code"

    # Restore file change
    restore_res = restore_file_change(temp_workspace, "app.py", change_res["backup_content"])
    assert restore_res["success"] is True
    assert read_file(temp_workspace, "app.py") == "initial code"
