from typing import Dict, Any, Callable, List
from backend.tools.file_ops import list_files, read_file, write_file
from backend.tools.code_search import search_code
from backend.tools.executor import run_python
from backend.tools.test_runner import run_tests
from backend.tools.patch_ops import apply_file_change, rollback_change
from backend.tools.git_tools import git_status, git_diff

TOOL_REGISTRY: Dict[str, Callable] = {
    "list_files": list_files,
    "read_file": read_file,
    "write_file": write_file,
    "search_code": search_code,
    "run_python": run_python,
    "run_tests": run_tests,
    "apply_file_change": apply_file_change,
    "rollback_change": rollback_change,
    "git_status": git_status,
    "git_diff": git_diff,
}


def get_tool(name: str) -> Callable:
    """
    Look up a tool function by name from the registry.
    
    Args:
        name: Name of the tool function.
        
    Returns:
        Callable tool function.
        
    Raises:
        ValueError: If the tool name is not registered.
    """
    if name not in TOOL_REGISTRY:
        available = ", ".join(TOOL_REGISTRY.keys())
        raise ValueError(f"Unknown tool: '{name}'. Available tools: [{available}]")
    return TOOL_REGISTRY[name]


def list_tools() -> List[str]:
    """
    Returns a list of all registered tool names.
    """
    return list(TOOL_REGISTRY.keys())


def get_tool_descriptions() -> List[Dict[str, Any]]:
    """
    Returns structured metadata descriptions for all registered tools.
    """
    return [
        {
            "name": "list_files",
            "description": "Recursively list source files inside a workspace.",
            "parameters": {
                "workspace": "string (required)"
            }
        },
        {
            "name": "read_file",
            "description": "Read the text content of a file within the workspace.",
            "parameters": {
                "workspace": "string (required)",
                "file_path": "string (required)"
            }
        },
        {
            "name": "write_file",
            "description": "Write text content to a file inside the workspace.",
            "parameters": {
                "workspace": "string (required)",
                "file_path": "string (required)",
                "content": "string (required)"
            }
        },
        {
            "name": "search_code",
            "description": "Case-insensitive text/code search across files in the workspace.",
            "parameters": {
                "workspace": "string (required)",
                "query": "string (required)"
            }
        },
        {
            "name": "run_python",
            "description": "Execute a Python script or command within the workspace.",
            "parameters": {
                "workspace": "string (required)",
                "command": "string or list of strings (required)",
                "timeout": "integer (optional, default 10)"
            }
        },
        {
            "name": "run_tests",
            "description": "Run pytest suite inside the workspace and return structured results.",
            "parameters": {
                "workspace": "string (required)",
                "timeout": "integer (optional, default 30)"
            }
        },
        {
            "name": "apply_file_change",
            "description": "Modify a source file and generate a backup for potential rollback.",
            "parameters": {
                "workspace": "string (required)",
                "file_path": "string (required)",
                "new_content": "string (required)"
            }
        },
        {
            "name": "rollback_change",
            "description": "Roll back a file change using the original backup content.",
            "parameters": {
                "workspace": "string (required)",
                "file_path": "string (required)",
                "backup_content": "string or null (required)"
            }
        },
        {
            "name": "git_status",
            "description": "Get git status (modified/untracked files) for a workspace repository.",
            "parameters": {
                "workspace": "string (required)"
            }
        },
        {
            "name": "git_diff",
            "description": "Generate git diff output showing modifications in the workspace repository.",
            "parameters": {
                "workspace": "string (required)"
            }
        }
    ]
