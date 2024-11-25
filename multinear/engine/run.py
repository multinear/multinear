import importlib.util
from pathlib import Path
from typing import Dict, Any
import yaml
import random
import hashlib
import json

from .storage import JobModel, TaskModel, TaskStatus
from .evaluate import evaluate
from ..utils.capture import OutputCapture
from ..utils.git import get_git_revision


def run_experiment(project_config: Dict[str, Any], job: JobModel):
    """
    Run an experiment using the task_runner.run_task function from the project folder

    Args:
        project_config: Project configuration dictionary containing folder path
        job: JobModel instance for the job being run

    Yields:
        Dict containing status updates, final results, and status map
    """
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

    with open(config_path, "r") as f:
        config = yaml.safe_load(f)

    # Construct path to task_runner.py
    task_runner_path = project_folder / ".multinear" / "task_runner.py"

    if not task_runner_path.exists():
        raise FileNotFoundError(f"Task runner file not found at {task_runner_path}")

    # Dynamically load the task runner module
    spec = importlib.util.spec_from_file_location("task_runner", task_runner_path)
    task_runner_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(task_runner_module)

    # Check if run_task exists in the module
    if not hasattr(task_runner_module, "run_task"):
        raise AttributeError(f"run_task function not found in {task_runner_path}")

    # Run the experiment
    try:
        results = []
        total_tasks = len(config["tasks"])

        yield {"status": TaskStatus.STARTING, "total": total_tasks}

        for i, task in enumerate(config["tasks"]):
            current_task = i + 1

            try:
                input = task["input"]
                challenge_id = task.get("id", None)
                if not challenge_id:  # Calculate challenge ID from input
                    challenge_id = hashlib.sha256(
                        json.dumps(input).encode()
                    ).hexdigest()

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
                    "details": f"Running task {current_task}/{total_tasks}"
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
                    task_result["output"],
                    task_result["details"],
                    capture.logs,
                )

                yield {
                    "status": TaskStatus.EVALUATING,
                    "current": current_task,
                    "total": total_tasks,
                    "details": f"Evaluating task {current_task}/{total_tasks}"
                }

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
                print(f"Error running task {current_task}/{total_tasks}: {error_msg}")
                results.append({"error": error_msg})
                TaskModel.fail(task_id, error=error_msg)

        yield {
            "status": TaskStatus.COMPLETED,
            "current": total_tasks,
            "total": total_tasks,
            "results": results
        }

    except Exception as e:
        print(f"Error running experiment: {e}")
        yield {
            "status": TaskStatus.FAILED,
            "total": 0,
            "error": str(e)
        }
