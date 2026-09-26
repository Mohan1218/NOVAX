from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Union


class DebugRequest(BaseModel):
    bug_report: str = Field(..., min_length=1)
    workspace: str = "workspace/demo_project"


class DebugResponse(BaseModel):
    job_id: str
    status: str
    message: str


class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int = 0
    current_step: str = ""
    logs: List[Any] = []
    result: Optional[Dict[str, Any]] = None


# Execution Engine API Schemas
class WriteFileRequest(BaseModel):
    content: str


class RunPythonRequest(BaseModel):
    command: Union[str, List[str]]
    timeout: int = Field(default=10, ge=1, le=300)


class RunTestsRequest(BaseModel):
    timeout: int = Field(default=30, ge=1, le=300)


class ApplyChangeRequest(BaseModel):
    content: str


class RollbackRequest(BaseModel):
    backup_content: Optional[str] = None


class ToolExecutionRequest(BaseModel):
    workspace: Optional[str] = None
    kwargs: Dict[str, Any] = Field(default_factory=dict)


# Job Management API Schemas
class CreateJobRequest(BaseModel):
    workspace: str = "demo_project"
    bug_report: Optional[str] = ""


class AddLogRequest(BaseModel):
    message: str
    level: str = "info"


class SetProgressRequest(BaseModel):
    progress: int = Field(..., ge=0, le=100)
    current_step: Optional[str] = None


class CompleteJobRequest(BaseModel):
    result: Optional[Dict[str, Any]] = None


class FailJobRequest(BaseModel):
    error: str


class JobLogEntry(BaseModel):
    timestamp: str
    level: str = "info"
    message: str


class JobResponse(BaseModel):
    job_id: str
    workspace: str
    status: str
    current_step: str = "waiting"
    progress: int = Field(default=0, ge=0, le=100)
    logs: List[Any] = []
    created_at: str
    updated_at: str
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
