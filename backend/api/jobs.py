from typing import Dict, Any, Optional
from fastapi import APIRouter, HTTPException, Body, Path as APIPath

from backend.services import job_manager
from backend.models.schemas import (
    CreateJobRequest,
    AddLogRequest,
    SetProgressRequest,
    CompleteJobRequest,
    FailJobRequest,
)

router = APIRouter(prefix="/api/jobs", tags=["jobs"])


@router.post("")
@router.post("/")
def create_new_job(body: Optional[CreateJobRequest] = Body(default=None)):
    """
    Creates a new debugging job entry.
    """
    workspace = body.workspace if body and body.workspace else "demo_project"
    bug_report = body.bug_report if body and body.bug_report else ""

    job_id = job_manager.create_job(workspace=workspace, bug_report=bug_report)
    job = job_manager.get_job(job_id)

    return {
        "success": True,
        "job": job
    }


@router.get("/{job_id}")
def get_job_status(job_id: str = APIPath(...)):
    """
    Retrieves the current state and logs of a job.
    """
    job = job_manager.get_job(job_id)
    if job is None:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    return {
        "success": True,
        "job": job
    }


@router.post("/{job_id}/log")
def append_job_log(job_id: str = APIPath(...), body: AddLogRequest = Body(...)):
    """
    Appends a log message to a job.
    """
    ok = job_manager.add_log(job_id, body.message, body.level)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    return {
        "success": True,
        "job": job_manager.get_job(job_id)
    }


@router.post("/{job_id}/progress")
def update_job_progress(job_id: str = APIPath(...), body: SetProgressRequest = Body(...)):
    """
    Updates progress percentage (0 to 100) and current step for a job.
    """
    try:
        ok = job_manager.set_progress(job_id, body.progress, body.current_step)
        if not ok:
            raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

        return {
            "success": True,
            "job": job_manager.get_job(job_id)
        }
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))


@router.post("/{job_id}/complete")
def mark_job_completed(job_id: str = APIPath(...), body: Optional[CompleteJobRequest] = Body(default=None)):
    """
    Marks a job as completed with optional result payload.
    """
    result = body.result if body else None
    ok = job_manager.complete_job(job_id, result=result)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    return {
        "success": True,
        "job": job_manager.get_job(job_id)
    }


@router.post("/{job_id}/fail")
def mark_job_failed(job_id: str = APIPath(...), body: FailJobRequest = Body(...)):
    """
    Marks a job as failed with an error message.
    """
    ok = job_manager.fail_job(job_id, body.error)
    if not ok:
        raise HTTPException(status_code=404, detail=f"Job '{job_id}' not found")

    return {
        "success": True,
        "job": job_manager.get_job(job_id)
    }
