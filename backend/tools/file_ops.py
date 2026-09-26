from pathlib import Path
from typing import List, Dict, Any, Union
from backend.tools.workspace import resolve_workspace, validate_path

IGNORED_DIRS = {".git", ".venv", "__pycache__", "node_modules", ".pytest_cache"}


def list_files(workspace: Union[str, Path]) -> List[str]:
    """
    Recursively list all files in the given workspace, skipping ignored directories.
    
    Args:
        workspace: Workspace identifier or path.
        
    Returns:
        List of file path strings relative to the workspace root.
    """
    ws_path = resolve_workspace(workspace)
    if not ws_path.exists() or not ws_path.is_dir():
        return []
        
    file_list: List[str] = []
    
    for path in ws_path.rglob("*"):
        # Skip if any path component relative to ws_path is in IGNORED_DIRS
        rel_parts = path.relative_to(ws_path).parts
        if any(part in IGNORED_DIRS for part in rel_parts):
            continue
            
        if path.is_file():
            file_list.append(str(path.relative_to(ws_path)))
            
    file_list.sort()
    return file_list


def read_file(workspace: Union[str, Path], file_path: Union[str, Path]) -> str:
    """
    Reads the content of a file within the validated workspace using UTF-8 encoding.
    
    Args:
        workspace: Workspace identifier or path.
        file_path: Relative or absolute file path inside workspace.
        
    Returns:
        File content string.
        
    Raises:
        FileNotFoundError: If the file does not exist or is a directory.
        PathTraversalError: If path attempts to escape the workspace.
    """
    target = validate_path(workspace, file_path)
    
    if not target.exists():
        raise FileNotFoundError(f"File not found: '{file_path}' in workspace '{workspace}'")
        
    if not target.is_file():
        raise FileNotFoundError(f"Path is not a file: '{file_path}'")
        
    return target.read_text(encoding="utf-8")


def write_file(
    workspace: Union[str, Path],
    file_path: Union[str, Path],
    content: str
) -> Dict[str, Any]:
    """
    Writes text content to a file within the validated workspace using UTF-8 encoding.
    Creates parent directories if they do not exist.
    
    Args:
        workspace: Workspace identifier or path.
        file_path: Relative or absolute file path inside workspace.
        content: Text content to write.
        
    Returns:
        Structured dictionary describing operation result.
    """
    target = validate_path(workspace, file_path)
    ws_path = resolve_workspace(workspace)
    
    target.parent.mkdir(parents=True, exist_ok=True)
    
    content_bytes = content.encode("utf-8")
    target.write_bytes(content_bytes)
    
    rel_file = str(target.relative_to(ws_path))
    return {
        "success": True,
        "file": rel_file,
        "bytes_written": len(content_bytes),
        "message": f"Successfully wrote {len(content_bytes)} bytes to '{rel_file}'"
    }
