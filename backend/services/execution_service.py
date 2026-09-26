from pathlib import Path
from typing import Dict, Any, List, Union, Optional
from backend.tools import (
    list_files as tool_list_files,
    read_file as tool_read_file,
    write_file as tool_write_file,
    search_code as tool_search_code,
    run_python as tool_run_python,
    run_tests as tool_run_tests,
    apply_file_change as tool_apply_file_change,
    rollback_change as tool_rollback_change,
    git_status as tool_git_status,
    git_diff as tool_git_diff,
    get_tool,
    list_tools,
    get_tool_descriptions as tool_get_descriptions,
)


class ExecutionService:
    """
    Service orchestration layer exposing execution engine tools to agents and API services.
    Delegates directly to validated tools in backend/tools.
    """

    def list_files(self, workspace: Union[str, Path]) -> List[str]:
        return tool_list_files(workspace)

    def read_file(self, workspace: Union[str, Path], file_path: Union[str, Path]) -> str:
        return tool_read_file(workspace, file_path)

    def write_file(self, workspace: Union[str, Path], file_path: Union[str, Path], content: str) -> Dict[str, Any]:
        return tool_write_file(workspace, file_path, content)

    def search_code(self, workspace: Union[str, Path], query: str) -> List[Dict[str, Any]]:
        return tool_search_code(workspace, query)

    def run_python(self, workspace: Union[str, Path], command: Union[str, List[str]], timeout: int = 10) -> Dict[str, Any]:
        return tool_run_python(workspace, command, timeout=timeout)

    def run_tests(self, workspace: Union[str, Path], timeout: int = 30) -> Dict[str, Any]:
        return tool_run_tests(workspace, timeout=timeout)

    def apply_file_change(self, workspace: Union[str, Path], file_path: Union[str, Path], new_content: str) -> Dict[str, Any]:
        return tool_apply_file_change(workspace, file_path, new_content)

    def rollback_change(self, workspace: Union[str, Path], file_path: Union[str, Path], backup_content: Optional[str]) -> Dict[str, Any]:
        return tool_rollback_change(workspace, file_path, backup_content)

    def git_status(self, workspace: Union[str, Path]) -> Dict[str, Any]:
        return tool_git_status(workspace)

    def git_diff(self, workspace: Union[str, Path]) -> Dict[str, Any]:
        return tool_git_diff(workspace)

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Main agent-facing interface to dynamically invoke registered workspace tools.
        
        Args:
            tool_name: Registered tool identifier string.
            **kwargs: Keyword arguments for the target tool.
            
        Returns:
            Structured output object from the executed tool.
        """
        try:
            tool_fn = get_tool(tool_name)
            return tool_fn(**kwargs)
        except ValueError as val_err:
            return {
                "success": False,
                "error": str(val_err)
            }
        except Exception as exc:
            return {
                "success": False,
                "error": f"Error executing tool '{tool_name}': {str(exc)}"
            }

    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        """
        Returns metadata descriptions for all available tools.
        """
        return tool_get_descriptions()
