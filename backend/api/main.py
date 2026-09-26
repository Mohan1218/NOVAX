from fastapi import FastAPI, HTTPException, BackgroundTasks, Body
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, Optional

from backend.models.schemas import DebugRequest, DebugResponse, JobStatus
from backend.services import job_manager
from backend.api.execution import router as execution_router
from backend.api.jobs import router as jobs_router
from backend.agent.orchestrator import AutonomousDebuggerAgent


app = FastAPI(
    title="BugHunter AI",
    description="Autonomous Software QA & Debugger Agent",
    version="0.1.0",
)


# Allow React frontend to communicate with FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(execution_router)
app.include_router(jobs_router)


def _run_agent_background(job_id: str, workspace: str, bug_report: str):
    """
    Background worker function executing the autonomous debugger agent for a job.
    """
    agent = AutonomousDebuggerAgent()
    agent.run_debug_job(job_id, workspace, bug_report)


@app.get("/")
def root():
    return {
        "name": "BugHunter AI",
        "status": "online",
        "role": "Autonomous Software QA & Debugger Agent",
    }


@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "BugHunter AI API",
    }


@app.post("/api/debug/run")
def run_autonomous_debug_run(request: DebugRequest, background_tasks: BackgroundTasks):
    """
    Starts an autonomous AI debugging run in the background.
    """
    ws = request.workspace or "demo_project"
    job_id = job_manager.create_job(
        workspace=ws,
        bug_report=request.bug_report,
    )

    background_tasks.add_task(_run_agent_background, job_id, ws, request.bug_report)

    return {
        "success": True,
        "job_id": job_id,
        "message": "Autonomous debugging run initiated in background"
    }


@app.post("/api/debug", response_model=DebugResponse)
def start_debug(request: DebugRequest, background_tasks: BackgroundTasks):
    """
    Legacy debug route launching background agent run.
    """
    ws = request.workspace or "demo_project"
    job_id = job_manager.create_job(
        bug_report=request.bug_report,
        workspace=ws,
    )

    background_tasks.add_task(_run_agent_background, job_id, ws, request.bug_report)

    return DebugResponse(
        job_id=job_id,
        status="queued",
        message="Debugging job created successfully",
    )


@app.get("/api/debug/{job_id}", response_model=JobStatus)
def debug_status(job_id: str):
    job = job_manager.get_job(job_id)

    if job is None:
        raise HTTPException(
            status_code=404,
            detail="Debug job not found",
        )

    return JobStatus(
        job_id=job["job_id"],
        status=job["status"],
        progress=job["progress"],
        current_step=job["current_step"],
        logs=job["logs"],
        result=job["result"],
    )
