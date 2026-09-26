import sys
from pathlib import Path
from typing import Dict, Any, Union
from backend.tools.workspace import resolve_workspace, WorkspaceError
from backend.tools.executor import run_python


def run_tests(workspace: Union[str, Path], timeout: int = 30) -> Dict[str, Any]:
    """
    Executes pytest runner on the target workspace directory.
    
    Args:
        workspace: Workspace identifier or path.
        timeout: Maximum test execution time in seconds.
        
    Returns:
        Structured dictionary containing:
        - success (bool): True if return_code == 0 and not timed_out
        - return_code (int): Exit status code from pytest
        - stdout (str): Standard output text
        - stderr (str): Standard error text
        - duration (float): Execution duration in seconds
        - timed_out (bool): True if process timed out
    """
    try:
        ws_path = resolve_workspace(workspace)
        if not ws_path.exists() or not ws_path.is_dir():
            return {
                "success": False,
                "return_code": -1,
                "stdout": "",
                "stderr": f"Workspace directory '{ws_path}' does not exist",
                "duration": 0.0,
                "timed_out": False
            }
            
        cmd = [sys.executable, "-m", "pytest", "-q"]
        test_env = dict(sys.modules.get('os', __import__('os')).environ)
        test_env.update({
            "PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1",
            "PYTHONDONTWRITEBYTECODE": "1"
        })
        return run_python(ws_path, cmd, timeout=timeout, env=test_env)
        
    except WorkspaceError as e:
        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": f"Workspace error: {str(e)}",
            "duration": 0.0,
            "timed_out": False
        }
    except Exception as exc:
        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": f"Test execution error: {str(exc)}",
            "duration": 0.0,
            "timed_out": False
        }
