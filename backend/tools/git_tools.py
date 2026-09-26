import subprocess
from pathlib import Path
from typing import Dict, Any, List, Union
from backend.tools.workspace import resolve_workspace, WorkspaceError


def git_status(workspace: Union[str, Path]) -> Dict[str, Any]:
    """
    Retrieves Git status for a validated workspace directory.
    Only operates on workspaces containing their own .git repository.
    
    Args:
        workspace: Workspace identifier or path.
        
    Returns:
        Structured dictionary containing status success, list of changed/untracked files, stdout, stderr, message.
    """
    try:
        ws_path = resolve_workspace(workspace)
        git_dir = ws_path / ".git"
        
        if not git_dir.exists():
            return {
                "success": False,
                "files_changed": [],
                "stdout": "",
                "stderr": "Workspace is not a Git repository",
                "message": "Workspace is not a Git repository"
            }
            
        proc = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=str(ws_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )
        
        stdout_str = proc.stdout.decode("utf-8", errors="replace")
        stderr_str = proc.stderr.decode("utf-8", errors="replace")
        
        files_changed: List[str] = []
        for line in stdout_str.splitlines():
            line = line.strip()
            if len(line) > 3:
                # Format: XY filename -> extract filename after status codes
                filename = line[2:].strip()
                files_changed.append(filename)
                
        return {
            "success": proc.returncode == 0,
            "files_changed": files_changed,
            "stdout": stdout_str,
            "stderr": stderr_str,
            "message": "Git status retrieved successfully" if proc.returncode == 0 else "Git status failed"
        }
        
    except WorkspaceError as e:
        return {
            "success": False,
            "files_changed": [],
            "stdout": "",
            "stderr": f"Workspace error: {str(e)}",
            "message": f"Workspace error: {str(e)}"
        }
    except Exception as exc:
        return {
            "success": False,
            "files_changed": [],
            "stdout": "",
            "stderr": f"Git status error: {str(exc)}",
            "message": f"Git status error: {str(exc)}"
        }


def git_diff(workspace: Union[str, Path]) -> Dict[str, Any]:
    """
    Generates Git diff output for modified files in a validated workspace.
    Only operates on workspaces containing their own .git repository.
    
    Args:
        workspace: Workspace identifier or path.
        
    Returns:
        Structured dictionary containing success boolean, diff string, files_changed list, stderr, message.
    """
    try:
        ws_path = resolve_workspace(workspace)
        git_dir = ws_path / ".git"
        
        if not git_dir.exists():
            return {
                "success": False,
                "diff": "",
                "files_changed": [],
                "stderr": "Workspace is not a Git repository",
                "message": "Workspace is not a Git repository"
            }
            
        # First try git diff HEAD, fallback to git diff if HEAD doesn't exist yet
        proc = subprocess.run(
            ["git", "diff", "HEAD"],
            cwd=str(ws_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )
        
        if proc.returncode != 0:
            proc = subprocess.run(
                ["git", "diff"],
                cwd=str(ws_path),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                shell=False
            )
            
        diff_str = proc.stdout.decode("utf-8", errors="replace")
        stderr_str = proc.stderr.decode("utf-8", errors="replace")
        
        # Get list of changed file names
        proc_names = subprocess.run(
            ["git", "diff", "--name-only"],
            cwd=str(ws_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=False
        )
        
        names_str = proc_names.stdout.decode("utf-8", errors="replace")
        files_changed = [f.strip() for f in names_str.splitlines() if f.strip()]
        
        return {
            "success": proc.returncode == 0,
            "diff": diff_str,
            "files_changed": files_changed,
            "stderr": stderr_str,
            "message": "Git diff generated successfully" if proc.returncode == 0 else "Git diff failed"
        }
        
    except WorkspaceError as e:
        return {
            "success": False,
            "diff": "",
            "files_changed": [],
            "stderr": f"Workspace error: {str(e)}",
            "message": f"Workspace error: {str(e)}"
        }
    except Exception as exc:
        return {
            "success": False,
            "diff": "",
            "files_changed": [],
            "stderr": f"Git diff error: {str(exc)}",
            "message": f"Git diff error: {str(exc)}"
        }
