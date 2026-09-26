from typing import Dict, Any, Optional, List, Union
from backend.services.execution_service import ExecutionService
from backend.services import job_manager


class AgentBackendInterface:
    """
    Unified integration contract for Member 1 Agent layer.
    Exposes single-point access to JobManager state and ExecutionService tool engine.
    """

    def __init__(self, execution_service: Optional[ExecutionService] = None):
        self.execution_service = execution_service or ExecutionService()

    def create_job(self, workspace: str = "demo_project") -> Dict[str, Any]:
        """
        Creates a new debugging job and returns its initial structured state.
        """
        job_id = job_manager.create_job(workspace=workspace)
        job = job_manager.get_job(job_id)
        return job or {}

    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieves current state and logs of a job.
        """
        return job_manager.get_job(job_id)

    def log(self, job_id: str, message: str, level: str = "info") -> bool:
        """
        Appends a timestamped log entry to the specified job.
        """
        return job_manager.add_log(job_id, message, level=level)

    def progress(self, job_id: str, progress: int, current_step: Optional[str] = None) -> bool:
        """
        Updates progress percentage (0-100) and current step for a job.
        """
        return job_manager.set_progress(job_id, progress, current_step=current_step)

    def execute_tool(self, tool_name: str, **kwargs) -> Any:
        """
        Invokes an execution tool by name through ExecutionService.
        """
        return self.execution_service.execute_tool(tool_name, **kwargs)

    def complete(self, job_id: str, result: Optional[Dict[str, Any]] = None) -> bool:
        """
        Marks job as completed with optional result payload.
        """
        return job_manager.complete_job(job_id, result=result)

    def fail(self, job_id: str, error: str) -> bool:
        """
        Marks job as failed with error message.
        """
        return job_manager.fail_job(job_id, error=error)

    def get_tool_descriptions(self) -> List[Dict[str, Any]]:
        """
        Returns metadata descriptions for all registered workspace execution tools.
        """
        return self.execution_service.get_tool_descriptions()
