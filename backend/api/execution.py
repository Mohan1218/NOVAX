from typing import Dict, Any, Optional, List
from fastapi import APIRouter, HTTPException, Query, Body, Path as APIPath

from backend.services.execution_service import ExecutionService
from backend.models.schemas import (
    WriteFileRequest,
    RunPythonRequest,
    RunTestsRequest,
    ApplyChangeRequest,
    RollbackRequest,
)
from backend.tools.workspace import WorkspaceError, PathTraversalError

router = APIRouter(prefix="/api/execution", tags=["execution"])
execution_service = ExecutionService()


@router.get("/tools")
def list_available_tools():
    """
    Returns available tool descriptions and parameters for Member 1 agent and frontend UI.
    """
    return {
        "tools": execution_service.get_tool_descriptions()
    }


@router.get("/files/{workspace}")
def list_workspace_files(workspace: str):
    """
    Recursively list source files inside a workspace.
    """
    try:
        files = execution_service.list_files(workspace)
        return {
            "success": True,
            "workspace": workspace,
            "files": files
        }
    except (PathTraversalError, WorkspaceError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/file/{workspace}/{file_path:path}")
def read_workspace_file(workspace: str, file_path: str = APIPath(...)):
    """
    Read the content of a file inside the workspace.
    """
    try:
        content = execution_service.read_file(workspace, file_path)
        return {
            "success": True,
            "workspace": workspace,
            "file_path": file_path,
            "content": content
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except (PathTraversalError, WorkspaceError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/file/{workspace}/{file_path:path}")
def write_workspace_file(workspace: str, file_path: str = APIPath(...), body: WriteFileRequest = Body(...)):
    """
    Write text content to a file inside the workspace.
    """
    try:
        result = execution_service.write_file(workspace, file_path, body.content)
        return result
    except (PathTraversalError, WorkspaceError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search/{workspace}")
def search_workspace_code(workspace: str, q: str = Query(..., min_length=1)):
    """
    Case-insensitive text/code search across files in the workspace.
    """
    try:
        results = execution_service.search_code(workspace, q)
        return {
            "success": True,
            "workspace": workspace,
            "query": q,
            "results": results
        }
    except WorkspaceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/run-python/{workspace}")
def execute_python_command(workspace: str, body: RunPythonRequest):
    """
    Execute a Python script or command inside the workspace.
    """
    try:
        return execution_service.run_python(workspace, body.command, timeout=body.timeout)
    except WorkspaceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/test/{workspace}")
def execute_pytest_suite(workspace: str, body: Optional[RunTestsRequest] = Body(default=None)):
    """
    Execute pytest suite inside the workspace and return structured results.
    """
    timeout = body.timeout if body else 30
    try:
        return execution_service.run_tests(workspace, timeout=timeout)
    except WorkspaceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/apply-change/{workspace}/{file_path:path}")
def apply_workspace_file_change(workspace: str, file_path: str = APIPath(...), body: ApplyChangeRequest = Body(...)):
    """
    Apply a code modification to a file and generate backup for rollback.
    """
    try:
        return execution_service.apply_file_change(workspace, file_path, body.content)
    except (PathTraversalError, WorkspaceError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/rollback/{workspace}/{file_path:path}")
def rollback_workspace_file_change(workspace: str, file_path: str = APIPath(...), body: RollbackRequest = Body(...)):
    """
    Roll back a file change using the original backup content.
    """
    try:
        return execution_service.rollback_change(workspace, file_path, body.backup_content)
    except (PathTraversalError, WorkspaceError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/git-status/{workspace}")
def get_workspace_git_status(workspace: str):
    """
    Retrieve Git status (modified/untracked files) for a workspace repository.
    """
    try:
        return execution_service.git_status(workspace)
    except WorkspaceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/git-diff/{workspace}")
def get_workspace_git_diff(workspace: str):
    """
    Generate Git diff output showing modifications in the workspace repository.
    """
    try:
        return execution_service.git_diff(workspace)
    except WorkspaceError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/tool/{tool_name}")
def execute_generic_tool(tool_name: str, payload: Dict[str, Any] = Body(default={})):
    """
    Generic execution endpoint for dynamic tool calls from Member 1 agent.
    """
    kwargs = payload.copy()
    if "kwargs" in kwargs and isinstance(kwargs["kwargs"], dict):
        nested = kwargs.pop("kwargs")
        kwargs.update(nested)

    try:
        result = execution_service.execute_tool(tool_name, **kwargs)
        if isinstance(result, dict) and result.get("success") is False and "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        return result
    except TypeError as te:
        raise HTTPException(status_code=400, detail=f"Invalid parameters for tool '{tool_name}': {str(te)}")
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except (PathTraversalError, WorkspaceError) as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
