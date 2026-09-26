import os
import sys
import time
import shlex
import subprocess
from pathlib import Path
from typing import Dict, Any, Union, List, Optional
from backend.tools.workspace import resolve_workspace


def run_python(
    workspace: Union[str, Path],
    command: Union[str, List[str]],
    timeout: int = 10,
    env: Optional[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    Executes a Python command or script within the validated workspace directory.
    
    Args:
        workspace: Workspace identifier or path.
        command: Command string (e.g. "pytest", "python script.py") or list of command args.
        timeout: Maximum execution timeout in seconds.
        env: Optional environment variables dictionary to extend os.environ.
        
    Returns:
        Structured dictionary with success status, return code, stdout, stderr, duration, and timed_out flag.
    """
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

    # Format command into arguments list
    if isinstance(command, str):
        cmd_args = shlex.split(command)
    else:
        cmd_args = list(command)
        
    if not cmd_args:
        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": "Empty command provided",
            "duration": 0.0,
            "timed_out": False
        }
        
    # Standardize python / pytest executables to current environment Python
    executable = sys.executable
    if cmd_args[0] in ("python", "python3"):
        cmd_args[0] = executable
    elif cmd_args[0] == "pytest":
        cmd_args = [executable, "-m", "pytest"] + cmd_args[1:]

    # Prepare execution environment
    exec_env = os.environ.copy()
    if env:
        exec_env.update(env)

    start_time = time.time()
    
    try:
        proc = subprocess.run(
            cmd_args,
            cwd=str(ws_path),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            env=exec_env,
            shell=False
        )
        duration = round(time.time() - start_time, 4)
        stdout_str = proc.stdout.decode("utf-8", errors="replace")
        stderr_str = proc.stderr.decode("utf-8", errors="replace")
        
        return {
            "success": proc.returncode == 0,
            "return_code": proc.returncode,
            "stdout": stdout_str,
            "stderr": stderr_str,
            "duration": duration,
            "timed_out": False
        }
        
    except subprocess.TimeoutExpired as e:
        duration = round(time.time() - start_time, 4)
        stdout_str = e.stdout.decode("utf-8", errors="replace") if e.stdout else ""
        stderr_str = e.stderr.decode("utf-8", errors="replace") if e.stderr else f"Command timed out after {timeout} seconds"
        
        return {
            "success": False,
            "return_code": -1,
            "stdout": stdout_str,
            "stderr": stderr_str,
            "duration": duration,
            "timed_out": True
        }
        
    except FileNotFoundError:
        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": f"Command binary not found: '{cmd_args[0]}'",
            "duration": 0.0,
            "timed_out": False
        }
        
    except Exception as exc:
        duration = round(time.time() - start_time, 4)
        return {
            "success": False,
            "return_code": -1,
            "stdout": "",
            "stderr": f"Execution error: {str(exc)}",
            "duration": duration,
            "timed_out": False
        }
