import uuid
import threading
from datetime import datetime
from typing import Dict, Any, Optional, List

# In-memory thread-safe jobs repository
jobs: Dict[str, Dict[str, Any]] = {}
_lock = threading.Lock()

ALLOWED_STATUSES = {"queued", "running", "completed", "failed", "cancelled"}


def _get_iso_timestamp() -> str:
    return datetime.now().isoformat()


def create_job(workspace: str = "demo_project", bug_report: str = "") -> str:
    """
    Creates a new debugging job entry in memory.
    
    Args:
        workspace: Target workspace identifier.
        bug_report: Optional initial bug report text.
        
    Returns:
        Generated job_id string.
    """
    job_id = str(uuid.uuid4())[:8]
    now = _get_iso_timestamp()

    job_data = {
        "job_id": job_id,
        "workspace": workspace,
        "status": "queued",
        "current_step": "waiting",
        "progress": 0,
        "logs": [
            {
                "timestamp": now,
                "level": "info",
                "message": "Debug job created"
            }
        ],
        "created_at": now,
        "updated_at": now,
        "bug_report": bug_report,
        "result": None,
        "error": None,
    }

    with _lock:
        jobs[job_id] = job_data

    return job_id


def get_job(job_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves a job object by its job_id.
    """
    with _lock:
        job = jobs.get(job_id)
        if job is None:
            return None
        # Return a copy to avoid mutation outside lock
        return dict(job)


def add_log(job_id: str, message: str, level: str = "info") -> bool:
    """
    Appends a log entry to a job.
    """
    with _lock:
        if job_id not in jobs:
            return False
        
        now = _get_iso_timestamp()
        log_entry = {
            "timestamp": now,
            "level": level,
            "message": message
        }
        jobs[job_id]["logs"].append(log_entry)
        jobs[job_id]["updated_at"] = now
        return True


def set_progress(job_id: str, progress: int, current_step: Optional[str] = None) -> bool:
    """
    Updates progress percentage (0 to 100) and current step.
    """
    if not (0 <= progress <= 100):
        raise ValueError(f"Progress must be between 0 and 100, got {progress}")

    with _lock:
        if job_id not in jobs:
            return False

        now = _get_iso_timestamp()
        jobs[job_id]["progress"] = progress
        if current_step is not None:
            jobs[job_id]["current_step"] = current_step
        jobs[job_id]["updated_at"] = now
        return True


def update_job(
    job_id: str,
    status: Optional[str] = None,
    progress: Optional[int] = None,
    current_step: Optional[str] = None,
    result: Any = None,
    error: Optional[str] = None,
) -> bool:
    """
    Updates arbitrary properties of a job.
    """
    if status is not None and status not in ALLOWED_STATUSES:
        raise ValueError(f"Invalid status '{status}'. Allowed: {ALLOWED_STATUSES}")

    if progress is not None and not (0 <= progress <= 100):
        raise ValueError(f"Progress must be between 0 and 100, got {progress}")

    with _lock:
        if job_id not in jobs:
            return False

        now = _get_iso_timestamp()
        if status is not None:
            jobs[job_id]["status"] = status
        if progress is not None:
            jobs[job_id]["progress"] = progress
        if current_step is not None:
            jobs[job_id]["current_step"] = current_step
        if result is not None:
            jobs[job_id]["result"] = result
        if error is not None:
            jobs[job_id]["error"] = error

        jobs[job_id]["updated_at"] = now
        return True


def complete_job(job_id: str, result: Any = None) -> bool:
    """
    Marks a job as completed.
    """
    with _lock:
        if job_id not in jobs:
            return False

        now = _get_iso_timestamp()
        jobs[job_id]["status"] = "completed"
        jobs[job_id]["progress"] = 100
        jobs[job_id]["current_step"] = "completed"
        if result is not None:
            jobs[job_id]["result"] = result
        jobs[job_id]["updated_at"] = now
        
        # Add log
        jobs[job_id]["logs"].append({
            "timestamp": now,
            "level": "info",
            "message": "Job completed successfully"
        })
        return True


def fail_job(job_id: str, error: str) -> bool:
    """
    Marks a job as failed with an error message.
    """
    with _lock:
        if job_id not in jobs:
            return False

        now = _get_iso_timestamp()
        jobs[job_id]["status"] = "failed"
        jobs[job_id]["current_step"] = "failed"
        jobs[job_id]["error"] = error
        jobs[job_id]["updated_at"] = now

        jobs[job_id]["logs"].append({
            "timestamp": now,
            "level": "error",
            "message": f"Job failed: {error}"
        })
        return True


def cancel_job(job_id: str) -> bool:
    """
    Marks a job as cancelled.
    """
    with _lock:
        if job_id not in jobs:
            return False

        now = _get_iso_timestamp()
        jobs[job_id]["status"] = "cancelled"
        jobs[job_id]["current_step"] = "cancelled"
        jobs[job_id]["updated_at"] = now

        jobs[job_id]["logs"].append({
            "timestamp": now,
            "level": "warning",
            "message": "Job cancelled"
        })
        return True
