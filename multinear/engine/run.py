import importlib.util
from pathlib import Path
from typing import Dict, Any
from rich.console import Console
import yaml
import random
import hashlib
import json

from .storage import JobModel, TaskModel, TaskStatus
from .evaluate import evaluate
from ..utils.capture import OutputCapture
from ..utils.git import get_git_revision
from .utils import rephrase_input


def run_experiment(project_config: Dict[str, Any], job: JobModel, challenge_id: str | None = None):
    """
    Run an experiment using the task_runner.run_task function from the project folder

    Args:
        project_config: Project configuration dictionary containing folder path
        job: JobModel instance for the job being run
        challenge_id: If provided, only run the task with this challenge ID

    Yields:
        Dict containing status updates, final results, and status map
    """
    try:
        # Get the project folder path
        project_folder = Path(project_config["folder"])

        # Load config.yaml from project folder
        config_path = project_folder / ".multinear" / "config.yaml"
        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")

        # Save git revision to job details
        git_revision = get_git_revision(project_folder)
        print(f"Git revision: {git_revision}")
        job.update(details={"git_revision": get_git_revision(project_folder)})

        if not config_path.exists():
            raise FileNotFoundError(f"Config file not found at {config_path}")

        with open(config_path, "r") as f:
            config = yaml.safe_load(f)

        # If challenge_id is provided, filter tasks to only include the specified task
        if challenge_id:
            # if challenge_id is a repeated task id (looks like xxx_[number]), clean it up
            if "_" in challenge_id and challenge_id.split("_")[1].isdigit():
                challenge_id = challenge_id.split("_")[0]
            config["tasks"] = [task for task in config["tasks"] if task.get("id") == challenge_id]
            if not config["tasks"]:
                raise ValueError(f"No task found with challenge ID {challenge_id}")

        # Construct path to task_runner.py
        task_runner_path = project_folder / ".multinear" / "task_runner.py"

        if not task_runner_path.exists():
            raise FileNotFoundError(f"Task runner file not found at {task_runner_path}")

        # Dynamically load the task runner module
        try:
            spec = importlib.util.spec_from_file_location("task_runner", task_runner_path)
            task_runner_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(task_runner_module)
        except Exception as e:
            error_msg = f"Failed to load task_runner.py: {str(e)}"
            console = Console()
            console.print(f"[red bold]{error_msg}[/red bold]")
            console.print_exception()
            job.update(
                status=TaskStatus.FAILED,
                details={
                    "error": error_msg,
                    "status_map": {}
                }
            )
            yield {
                "status": TaskStatus.FAILED,
                "total": 0,
                "error": error_msg,
                "status_map": {}
            }
            return

        # Check if run_task exists in the module
        if not hasattr(task_runner_module, "run_task"):
            error_msg = f"run_task function not found in {task_runner_path}"
            job.update(
                status=TaskStatus.FAILED,
                details={
                    "error": error_msg,
                    "status_map": {}
                }
            )
            yield {
                "status": TaskStatus.FAILED,
                "total": 0,
                "error": error_msg,
                "status_map": {}
            }
            return

        # Run start_run if it exists
        if hasattr(task_runner_module, "start_run"):
            try:
                task_runner_module.start_run()
            except Exception as e:
                error_msg = f"Error in start_run: {str(e)}"
                console = Console()
                console.print(f"[red bold]{error_msg}[/red bold]")
                console.print_exception()
                job.update(
                    status=TaskStatus.FAILED,
                    details={
                        "error": error_msg,
                        "status_map": {}
                    }
                )
                yield {
                    "status": TaskStatus.FAILED,
                    "total": 0,
                    "error": error_msg,
                    "status_map": {}
                }
                return

        # Check if tasks are defined
        if not config.get("tasks", []):
            raise ValueError("No tasks defined in config.yaml")

        # Run the experiment
        results = []
        total_tasks = sum(task.get("repeat", 1) for task in config["tasks"])

        yield {"status": TaskStatus.STARTING, "total": total_tasks}

        current_task = 0
        for task in config["tasks"]:
            # Get number of repeats for this task (default to 1)
            repeats = task.get("repeat", 1)

            # Initialize variations tracking for this task
            if task.get("rephrase", False):
                previous_variations = []

            for repeat in range(repeats):
                current_task += 1

                try:
                    input = task["input"]
                    # Rephrase the input for repeats, if enabled
                    if repeat > 0 and task.get("rephrase", False):
                        input = rephrase_input(input, previous_variations)
                        previous_variations.append(input)

                    challenge_id = task.get("id", None)
                    if not challenge_id:  # Calculate challenge ID from input
                        # Include repeat number in challenge ID to make it unique
                        challenge_id = hashlib.sha256(
                            json.dumps(input).encode()
                        ).hexdigest()

                    # Append repeat counter to challenge_id if this is a repeat
                    if repeat > 0:
                        challenge_id = f"{challenge_id}_{repeat}"

                    # Start new task
                    task_id = TaskModel.start(
                        job_id=job.id,
                        task_number=current_task,
                        challenge_id=challenge_id
                    )

                    yield {
                        "status": TaskStatus.RUNNING,
                        "current": current_task,
                        "total": total_tasks,
                        "details": (
                            f"Running task {current_task}/{total_tasks}"
                            +
                            (f" (repeat {repeat + 1}/{repeats})" if repeat > 0 else "")
                        )
                    }

                    # Do we simulate a failure?
                    fail_simulate = config.get("meta", {}).get("fail_simulate", None)
                    if fail_simulate is not None and random.random() < fail_simulate:
                        raise Exception("Simulated failure")

                    # Run the task
                    with OutputCapture() as capture:
                        task_result = task_runner_module.run_task(input)
                    TaskModel.executed(
                        task_id,
                        input,
                        task_result.get("output"),
                        task_result.get("details", {}),
                        capture.logs,
                    )

                    yield {
                        "status": TaskStatus.EVALUATING,
                        "current": current_task,
                        "total": total_tasks,
                        "details": f"Evaluating task {current_task}/{total_tasks}"
                    }

                    # Inject global context into the task
                    task["context"] = config.get("meta", {}).get("context", "")

                    # Evaluate the task
                    with OutputCapture() as capture:
                        eval_result = evaluate(task, input, task_result["output"])
                    TaskModel.evaluated(
                        task_id,
                        {k: v for k, v in task.items() if k != "input"},
                        eval_result["passed"],
                        eval_result["score"],
                        eval_result["details"],
                        capture.logs,
                    )

                    results.append([task_result, eval_result])

                except Exception as e:
                    error_msg = str(e)
                    console = Console()
                    console.print(f"[red bold]Error running task {current_task}/{total_tasks}:[/red bold] {error_msg}")
                    console.print_exception()
                    results.append({"error": error_msg})
                    TaskModel.fail(task_id, error=error_msg)
                    # Update job details with the error
                    job.update(
                        status=TaskStatus.FAILED,
                        details={
                            "error": error_msg,
                            "status_map": TaskModel.get_status_map(job.id)
                        }
                    )

        yield {
            "status": TaskStatus.COMPLETED,
            "current": total_tasks,
            "total": total_tasks,
            "results": results
        }

    except Exception as e:
        error_msg = str(e)
        console = Console()
        console.print(f"[red bold]Error running experiment:[/red bold] {error_msg}")
        console.print_exception()
        yield {
            "status": TaskStatus.FAILED,
            "total": 0,
            "error": error_msg,
            "status_map": TaskModel.get_status_map(job.id)
        }
