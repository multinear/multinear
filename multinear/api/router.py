from fastapi import BackgroundTasks, HTTPException, APIRouter, Query
from typing import List, Dict, Any
from datetime import timezone
import os
from pathlib import Path
import yaml
import json
import hashlib

from ..api.schemas import (
    Project,
    JobDetails,
    FullRunDetails,
    TaskDetails,
    RecentRunsResponse,
)
from ..engine.run import run_experiment
from ..engine.storage import ProjectModel, JobModel, TaskModel, TaskStatus


def background_job(
    project_id: str,
    job_id: str,
    challenge_id: str | None = None,
    group_id: str | None = None,
):
    """
    Execute a background job to run an experiment for the specified project.

    This function performs the following steps:
    1. Retrieves the project and job details from the database.
    2. Runs the experiment and iterates through status updates.
    3. Updates the job status in the database based on experiment progress.
    4. Handles any exceptions by marking the job as failed.

    Args:
        project_id (str): The ID of the project.
        job_id (str): The ID of the job to execute.
        challenge_id (str | None): If provided, only run the task with this challenge ID.
        group_id (str | None): If provided, only run tasks from the specified group.
    """
    try:
        # Retrieve the project and job from the database
        project = ProjectModel.find(project_id)
        job = JobModel.find(job_id)

        # Get project config and add custom config file if specified in environment
        project_dict = project.to_dict()
        config_path = os.environ.get('MULTINEAR_CONFIG')
        if config_path:
            # Extract just the filename without path and .yaml extension
            config_file = Path(config_path).name
            project_dict["config_file"] = config_file

        # Run the experiment and handle status updates
        for update in run_experiment(project_dict, job, challenge_id, group_id):
            # Add status map from TaskModel to the update
            update["status_map"] = TaskModel.get_status_map(job_id)

            # Update job status in the database
            job.update(
                status=update["status"],
                total_tasks=update.get("total", 0),
                current_task=update.get("current"),
                details=update,
            )

        # Mark the job as finished upon successful completion
        job.finish()
    except Exception as e:
        # raise e
        # Handle exceptions and update the job as failed
        print(f"Error running experiment API: {e}")
        job = JobModel.find(job_id)
        job.update(
            status="failed",
            details={"error": str(e), "status_map": TaskModel.get_status_map(job_id)},
        )


# Create the FastAPI router for API endpoints with the prefix '/api'
api_router = APIRouter(prefix="/api")


@api_router.get("/projects", response_model=List[Project])
async def get_projects():
    """
    Retrieve the list of all available projects.

    Returns:
        List[Project]: A list of projects with their details.
    """
    return [
        Project(id=p.id, name=p.name, description=p.description)
        for p in ProjectModel.list()
    ]


@api_router.post("/jobs/{project_id}", response_model=JobDetails)
async def create_job(project_id: str, background_tasks: BackgroundTasks):
    """
    Create a new job for the specified project and initiate it in the background.

    Args:
        project_id (str): The ID of the project for which the job is to be created.
        background_tasks (BackgroundTasks): FastAPI BackgroundTasks for asynchronous
        execution.

    Returns:
        JobDetails: Details of the created job.

    Raises:
        HTTPException: If the specified project does not exist.
    """
    # Verify that the project exists
    if not ProjectModel.find(project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    # Start a new job and enqueue it as a background task
    job_id = JobModel.start(project_id)
    background_tasks.add_task(background_job, project_id, job_id)

    return JobDetails(
        project_id=project_id,
        job_id=job_id,
        status=TaskStatus.STARTING,
        total_tasks=0,
        task_status_map={},
        details={},
    )


@api_router.get("/jobs/{project_id}/{job_id}/status", response_model=JobDetails)
async def get_job_status(project_id: str, job_id: str):
    """
    Retrieve the current status of a specific job.

    Args:
        project_id (str): The ID of the project.
        job_id (str): The ID of the job whose status is to be retrieved.

    Returns:
        JobDetails: Current status and details of the job.

    Raises:
        HTTPException: If the project or job is not found.
    """
    # Verify that the project exists
    if not ProjectModel.find(project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    # Retrieve the job status, ensuring it belongs to the specified project
    job = JobModel.get_status(project_id, job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")

    details = job.details or {}
    return JobDetails(
        project_id=project_id,
        job_id=job_id,
        status=job.status,
        total_tasks=job.total_tasks,
        current_task=job.current_task,
        task_status_map=details.get("status_map", {}),
        details=details,
    )


@api_router.get("/runs/{project_id}", response_model=RecentRunsResponse)
async def get_recent_runs(
    project_id: str,
    limit: int = Query(5, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Retrieve a paginated list of recent runs for a specific project.

    Args:
        project_id (str): The ID of the project.
        limit (int, optional): Number of runs to retrieve. Defaults to 5.
        offset (int, optional): Number of runs to skip for pagination. Defaults to 0.

    Returns:
        RecentRunsResponse: A response containing recent runs and total count.

    Raises:
        HTTPException: If the project does not exist.
    """
    # Verify that the project exists
    if not ProjectModel.find(project_id):
        raise HTTPException(status_code=404, detail="Project not found")

    # Get total count of runs for this project
    total_runs = JobModel.count_jobs(project_id)

    # Retrieve recent jobs based on limit and offset for pagination
    recent_jobs = JobModel.list_recent(project_id, limit, offset)

    runs = []
    for job in recent_jobs:
        job_data = job.details or {}
        model = job.get_model_summary()

        # Initialize statistics for the run
        total = passed = failed = regression = score = 0
        task_status_map = job_data.get("status_map", {})
        if task_status_map:
            total = len(task_status_map)
            passed = sum(
                1
                for status in task_status_map.values()
                if status == TaskStatus.COMPLETED
            )
            failed = sum(
                1 for status in task_status_map.values() if status == TaskStatus.FAILED
            )
            regression = total - passed - failed
            if total > 0:
                score = passed / total

        # Append the run details to the list
        runs.append(
            {
                "id": job.id,
                "created_at": job.created_at.replace(tzinfo=timezone.utc).isoformat(),
                "finished_at": (
                    job.finished_at.replace(tzinfo=timezone.utc).isoformat()
                    if job.finished_at
                    else None
                ),
                "revision": job_data.get("git_revision") or "",
                "model": model,
                "score": score,
                "totalTests": total,
                "pass": passed,
                "fail": failed,
                "regression": regression,
                # "bookmarked": False,
                # "noted": False
            }
        )

    return RecentRunsResponse(runs=runs, total=total_runs)


def _get_task_details(task: TaskModel):
    """
    Helper function to convert a TaskModel instance to the TaskDetails schema.

    Args:
        task (TaskModel): The task instance to convert.

    Returns:
        TaskDetails: The schema representation of the task.
    """
    return TaskDetails(
        id=task.id,
        job_id=task.job_id,
        challenge_id=task.challenge_id,
        status=task.status,
        error=task.error,
        task_input=(
            {'str': task.task_input}
            if isinstance(task.task_input, str)
            else task.task_input
        ),
        task_output=(
            {'str': task.task_output}
            if isinstance(task.task_output, str)
            else task.task_output
        ),
        task_details=task.task_details,
        task_logs={'logs': task.task_logs} if task.task_logs else None,
        eval_spec=task.eval_spec,
        eval_passed=task.eval_passed,
        eval_score=task.eval_score,
        eval_details=task.eval_details,
        eval_logs={'logs': task.eval_logs} if task.eval_logs else None,
        created_at=task.created_at.replace(tzinfo=timezone.utc).isoformat(),
        executed_at=(
            task.executed_at.replace(tzinfo=timezone.utc).isoformat()
            if task.executed_at
            else None
        ),
        evaluated_at=(
            task.evaluated_at.replace(tzinfo=timezone.utc).isoformat()
            if task.evaluated_at
            else None
        ),
        finished_at=(
            task.finished_at.replace(tzinfo=timezone.utc).isoformat()
            if task.finished_at
            else None
        ),
    )


@api_router.get("/run-details/{run_id}", response_model=FullRunDetails)
async def get_run_details(run_id: str):
    """
    Retrieve detailed information about a specific run, including all associated tasks.

    Args:
        run_id (str): The ID of the run.

    Returns:
        FullRunDetails: Comprehensive details of the run, including tasks.

    Raises:
        HTTPException: If the run or associated project is not found.
    """
    # Retrieve the job corresponding to the run_id
    job = JobModel.find(run_id)
    if not job:
        raise HTTPException(status_code=404, detail="Run not found")

    # Retrieve project details associated with the job
    project = ProjectModel.find(job.project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Retrieve all tasks associated with the job
    tasks = TaskModel.list(run_id)
    task_details = [_get_task_details(task) for task in tasks]

    # Construct and return the full run details
    return FullRunDetails(
        id=run_id,
        project=Project(
            id=project.id, name=project.name, description=project.description
        ),
        details=job.details or {},
        date=job.created_at.replace(tzinfo=timezone.utc).isoformat(),
        status=job.status,
        tasks=task_details,
    )


@api_router.get(
    "/same-tasks/{project_id}/{challenge_id}", response_model=List[TaskDetails]
)
async def get_same_tasks(
    project_id: str,
    challenge_id: str,
    limit: int = Query(10, ge=1, le=100),
    offset: int = Query(0, ge=0),
):
    """
    Find and retrieve tasks within a project that share the same challenge ID.

    Args:
        project_id (str): The ID of the project.
        challenge_id (str): The challenge ID to search for.
        limit (int, optional): Maximum number of tasks to retrieve. Defaults to 10.
        offset (int, optional): Number of tasks to skip for pagination. Defaults to 0.

    Returns:
        List[TaskDetails]: A list of task details matching the challenge ID.
    """
    # Retrieve tasks that have the specified challenge ID within the project
    tasks = TaskModel.find_same_tasks(project_id, challenge_id, limit, offset)
    return [_get_task_details(task) for task in tasks]


@api_router.post("/jobs/{project_id}/task/{challenge_id}")
async def run_single_task(
    project_id: str,
    challenge_id: str,
    background_tasks: BackgroundTasks,
):
    """
    Start a new job that runs only a single task with the specified challenge ID.

    Args:
        project_id (str): The ID of the project.
        challenge_id (str): The challenge ID of the task to run.
        background_tasks: FastAPI background tasks handler.

    Returns:
        JobResponse: Details of the created job.
    """
    # Verify that the project exists
    project = ProjectModel.find(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create a new job
    job_id = JobModel.start(project_id)

    # Start the background task
    background_tasks.add_task(background_job, project_id, job_id, challenge_id)

    return {
        "project_id": project_id,
        "job_id": job_id,
        "status": "started",
        "total_tasks": 1,
    }


@api_router.post("/jobs/{project_id}/group/{group_id}")
async def run_group_tasks(
    project_id: str,
    group_id: str,
    background_tasks: BackgroundTasks,
):
    """
    Start a new job that runs all tasks from the specified group.

    Args:
        project_id (str): The ID of the project.
        group_id (str): The ID of the group to run tasks from.
        background_tasks: FastAPI background tasks handler.

    Returns:
        JobResponse: Details of the created job.
    """
    # Verify that the project exists
    project = ProjectModel.find(project_id)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Create a new job
    job_id = JobModel.start(project_id)

    # Start the background task
    background_tasks.add_task(background_job, project_id, job_id, None, group_id)

    return {
        "project_id": project_id,
        "job_id": job_id,
        "status": "started",
    }


def _process_task(task: Dict[str, Any], group_id: str = None) -> Dict[str, Any]:
    """
    Process a task from config.yaml and return a standardized task info dictionary.

    Args:
        task: The task dictionary from config.yaml
        group_id: Optional group ID to prefix the task ID with

    Returns:
        Dict containing standardized task information
    """
    task_info = {
        "id": task.get("id", None),
        "name": task.get("name", None),
        "description": task.get("description", None),
        "input": task.get("input", None),
    }

    # If no ID is provided, generate one from input
    if not task_info["id"] and task_info["input"]:
        task_info["id"] = hashlib.sha256(
            json.dumps(task_info["input"]).encode()
        ).hexdigest()

    # Add group_id prefix to task id for proper identification if provided
    if task_info["id"] and group_id:
        task_info["id"] = f"{group_id}/{task_info['id']}"

    return task_info


@api_router.get("/tasks/{project_id}")
async def get_available_tasks(project_id: str):
    """
    Get available tasks and groups from config.yaml for a project.

    Returns both a list of root-level tasks and a structured list of groups with their tasks.
    """
    try:
        # Retrieve the project from the database
        project = ProjectModel.find(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")

        # Get project config and add custom config file if specified in environment
        project_dict = project.to_dict()
        config_path = os.environ.get('MULTINEAR_CONFIG')
        if config_path:
            # Extract just the filename without path and .yaml extension
            config_file = Path(config_path).name
            project_dict["config_file"] = config_file

        # Load config.yaml from project folder
        project_folder = Path(project_dict["folder"])
        config_path = (
            project_folder
            / ".multinear"
            / project_dict.get("config_file", "config.yaml")
        )
        if not config_path.exists():
            raise HTTPException(status_code=404, detail="Config file not found")

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # Extract root-level tasks only
        root_tasks = [_process_task(task) for task in config.get("tasks", [])]

        # Extract groups and their tasks
        groups = []
        if "groups" in config:
            for group in config["groups"]:
                group_id = group.get("id", "")

                # Process tasks in this group
                group_tasks = [
                    _process_task(task, group_id) for task in group.get("tasks", [])
                ]

                # Create group info
                group_info = {
                    "id": group_id,
                    "name": group.get("name", ""),
                    "description": group.get("description", ""),
                    "task_count": len(group_tasks),
                    "tasks": group_tasks,
                }
                groups.append(group_info)

        return {"tasks": root_tasks, "groups": groups}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
