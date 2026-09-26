from pathlib import Path
from typing import Union

class WorkspaceError(Exception):
    """Base exception for workspace errors."""
    pass

class InvalidWorkspaceError(WorkspaceError):
    """Raised when a workspace path is invalid or outside the workspace root."""
    pass

class InvalidPathError(WorkspaceError):
    """Raised when a file or directory path is invalid."""
    pass

class PathTraversalError(InvalidPathError):
    """Raised when a path traversal attempt is detected."""
    pass


def get_workspace_root() -> Path:
    """
    Returns the absolute canonical path to the allowed workspace root directory.
    Ensures the directory exists.
    """
    root = (Path(__file__).resolve().parent.parent.parent / "workspace").resolve()
    root.mkdir(parents=True, exist_ok=True)
    return root


def resolve_workspace(workspace: Union[str, Path]) -> Path:
    """
    Resolves and validates a workspace path relative to the workspace root.
    
    Args:
        workspace: Relative workspace directory name/path or absolute path.
        
    Returns:
        Canonical absolute Path object for the workspace directory.
        
    Raises:
        InvalidWorkspaceError: If workspace is empty or outside workspace root.
    """
    if not workspace:
        raise InvalidWorkspaceError("Workspace parameter cannot be empty")
        
    root = get_workspace_root()
    ws_path = Path(workspace)
    
    if not ws_path.is_absolute():
        resolved_ws = (root / ws_path).resolve()
    else:
        resolved_ws = ws_path.resolve()
        
    if resolved_ws != root and root not in resolved_ws.parents:
        raise InvalidWorkspaceError(
            f"Workspace '{workspace}' resolves to '{resolved_ws}', which is outside workspace root '{root}'"
        )
        
    return resolved_ws


def resolve_path(workspace: Union[str, Path], relative_path: Union[str, Path]) -> Path:
    """
    Resolves a file path relative to a validated workspace.
    
    Args:
        workspace: Workspace identifier or path.
        relative_path: Relative or absolute target file path.
        
    Returns:
        Canonical absolute Path object.
    """
    ws_path = resolve_workspace(workspace)
    
    if not relative_path:
        return ws_path
        
    rel = Path(relative_path)
    if rel.is_absolute():
        target = rel.resolve()
    else:
        target = (ws_path / rel).resolve()
        
    return target


def validate_path(workspace: Union[str, Path], relative_path: Union[str, Path]) -> Path:
    """
    Validates that relative_path stays strictly within the validated workspace directory.
    
    Args:
        workspace: Workspace identifier or path.
        relative_path: Relative or absolute path to validate.
        
    Returns:
        Validated canonical absolute Path object.
        
    Raises:
        PathTraversalError: If path escapes the workspace directory boundary.
    """
    ws_path = resolve_workspace(workspace)
    target = resolve_path(workspace, relative_path)
    
    if target != ws_path and ws_path not in target.parents:
        raise PathTraversalError(
            f"Path '{relative_path}' escapes workspace boundary '{ws_path}' (resolved to '{target}')"
        )
        
    return target
