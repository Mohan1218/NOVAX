from pathlib import Path
from typing import Dict, Any, Optional, Union
from backend.tools.workspace import resolve_workspace, validate_path
from backend.tools.file_ops import read_file, write_file


def create_backup(
    workspace: Union[str, Path],
    file_path: Union[str, Path]
) -> Dict[str, Any]:
    """
    Saves and returns the original content of a file prior to modification.
    
    Args:
        workspace: Workspace identifier or path.
        file_path: Relative file path inside workspace.
        
    Returns:
        Structured dictionary containing backup content and file metadata.
    """
    target = validate_path(workspace, file_path)
    ws_path = resolve_workspace(workspace)
    rel_file = str(target.relative_to(ws_path))
    
    existed = target.exists() and target.is_file()
    backup_content: Optional[str] = None
    
    if existed:
        backup_content = read_file(workspace, rel_file)
        
    return {
        "success": True,
        "file": rel_file,
        "existed": existed,
        "backup_content": backup_content,
        "message": f"Backup created for file '{rel_file}'"
    }


def apply_file_change(
    workspace: Union[str, Path],
    file_path: Union[str, Path],
    new_content: str
) -> Dict[str, Any]:
    """
    Applies a code change to a file within the validated workspace while capturing backup content.
    
    Args:
        workspace: Workspace identifier or path.
        file_path: Relative file path to modify.
        new_content: Replacement text content.
        
    Returns:
        Structured dictionary with modification result, file path, existed flag, and backup_content.
    """
    backup_info = create_backup(workspace, file_path)
    target = validate_path(workspace, file_path)
    ws_path = resolve_workspace(workspace)
    rel_file = str(target.relative_to(ws_path))
    
    write_res = write_file(workspace, rel_file, new_content)
    
    return {
        "success": write_res.get("success", True),
        "file": rel_file,
        "existed": backup_info["existed"],
        "backup_content": backup_info["backup_content"],
        "message": f"Successfully applied changes to file '{rel_file}'"
    }


def rollback_change(
    workspace: Union[str, Path],
    file_path: Union[str, Path],
    backup_content: Optional[str]
) -> Dict[str, Any]:
    """
    Rolls back a file change by restoring original backup content or removing the file if newly created.
    
    Args:
        workspace: Workspace identifier or path.
        file_path: Relative file path to restore.
        backup_content: Original string content, or None if the file did not exist prior to change.
        
    Returns:
        Structured dictionary confirming restoration.
    """
    target = validate_path(workspace, file_path)
    ws_path = resolve_workspace(workspace)
    rel_file = str(target.relative_to(ws_path))
    
    if backup_content is None:
        if target.exists() and target.is_file():
            target.unlink()
        return {
            "success": True,
            "file": rel_file,
            "message": "Change rolled back successfully"
        }
    else:
        write_res = write_file(workspace, rel_file, backup_content)
        return {
            "success": write_res.get("success", True),
            "file": rel_file,
            "message": "Change rolled back successfully"
        }


def restore_file_change(
    workspace: Union[str, Path],
    file_path: Union[str, Path],
    backup_content: Optional[str]
) -> Dict[str, Any]:
    """
    Backward-compatible alias for rollback_change.
    """
    return rollback_change(workspace, file_path, backup_content)
