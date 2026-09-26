from typing import Dict, Any, List, Optional
from backend.services.agent_interface import AgentBackendInterface


class CoderAgent:
    """
    Agent sub-component responsible for applying code changes, capturing backups, rolling back, and generating diffs.
    Must operate ONLY through AgentBackendInterface.
    """

    def __init__(self, interface: AgentBackendInterface):
        self.interface = interface

    def apply_patch(self, workspace: str, file_path: str, new_content: str) -> Dict[str, Any]:
        """
        Applies a candidate code modification to a file inside the workspace and returns backup metadata.
        """
        return self.interface.execute_tool(
            "apply_file_change",
            workspace=workspace,
            file_path=file_path,
            new_content=new_content
        )

    def rollback(self, workspace: str, file_path: str, backup_content: Optional[str]) -> Dict[str, Any]:
        """
        Restores a file to its pre-patch state using backup content.
        """
        return self.interface.execute_tool(
            "rollback_change",
            workspace=workspace,
            file_path=file_path,
            backup_content=backup_content
        )

    def get_diff(self, workspace: str) -> Dict[str, Any]:
        """
        Retrieves the unified git diff for modifications inside the workspace.
        """
        return self.interface.execute_tool("git_diff", workspace=workspace)
