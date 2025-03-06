import importlib.util
from pathlib import Path
from typing import Dict, Any, List, Iterator
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


def run_group(
    tasks: List[Dict[str, Any]],
    job: JobModel,
    task_runner_module,
    config: Dict[str, Any],
    current_task_offset: int = 0,
    total_tasks: int = 0,
) -> Iterator[Dict[str, Any]]:
    """
    Run a group of tasks.

    Args:
        tasks: List of tasks to run
        job: JobModel instance for the job being run
        task_runner_module: Dynamically loaded task runner module
        config: The full config dictionary
        current_task_offset: Offset for task numbering
        total_tasks: Total number of tasks across all groups

    Yields:
        Dict containing status updates and results
    """
    global_repeat = config.get("meta", {}).get("repeat", 1)
    results = []
    current_task = current_task_offset

    for task in tasks:
        # Get number of repeats for this task (default to global repeat)
        repeats = task.get("repeat", global_repeat)

        # Initialize variations tracking for this task
        global_rephrase = config.get("meta", {}).get("rephrase", False)
        do_rephrase = task.get("rephrase", global_rephrase)
        if do_rephrase:
            previous_variations = []

        for repeat in range(repeats):
            current_task += 1

            try:
                input = task["input"]
                # Rephrase the input for repeats, if enabled
                if repeat > 0 and do_rephrase:
                    # If the input is a dictionary, rephrase the 'question' key only
                    if isinstance(input, dict) and 'question' in input:
                        rephrased_question = rephrase_input(
                            input['question'], previous_variations
                        )
                        previous_variations.append(rephrased_question)
                        input = {
                            **input,
                            'question': rephrased_question,
                        }  # Create new dict with rephrased question
                    else:
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
                    job_id=job.id, task_number=current_task, challenge_id=challenge_id
                )

                yield {
                    "status": TaskStatus.RUNNING,
                    "current": current_task,
                    "total": total_tasks,
                    "details": (
                        f"Running task {current_task}/{total_tasks}"
                        + (f" (repeat {repeat + 1}/{repeats})" if repeat > 0 else "")
                    ),
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
                    "details": f"Evaluating task {current_task}/{total_tasks}",
                }

                # Inject global context into the task
                task["context"] = config.get("meta", {}).get("context", "")

                # Inject global checklist, if present
                global_checklist = config.get("meta", {}).get("checklist", None)
                if (
                    global_checklist and "checklist" not in task
                ):  # avoid overriding task-specific checklist
                    task["checklist"] = global_checklist
                global_custom = config.get("meta", {}).get("custom", None)
                if (
                    global_custom and "custom" not in task
                ):  # avoid overriding task-specific custom
                    task["custom"] = global_custom

                # Evaluate the task
                with OutputCapture() as capture:
                    eval_result = evaluate(
                        task, input, task_result["output"], task_runner_module
                    )
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
                console.print(
                    f"[red bold]Error running task {current_task}/{total_tasks}:[/red bold] {error_msg}"
                )
                console.print_exception()
                results.append({"error": error_msg})
                TaskModel.fail(task_id, error=error_msg)
                # Update job details with the error
                job.update(
                    status=TaskStatus.FAILED,
                    details={
                        "error": error_msg,
                        "status_map": TaskModel.get_status_map(job.id),
                    },
                )

    return results


def run_experiment(
    project_config: Dict[str, Any],
    job: JobModel,
    challenge_id: str | None = None,
    group_id: str | None = None,
):
    """
    Run an experiment using the task_runner.run_task function from the project folder

    Args:
        project_config: Project configuration dictionary containing folder path
        job: JobModel instance for the job being run
        challenge_id: If provided, only run the task with this challenge ID
        group_id: If provided, only run tasks from the specified group

    Yields:
        Dict containing status updates, final results, and status map
    """
    try:
        # Get the project folder path
        project_folder = Path(project_config["folder"])

        # Load config.yaml from project folder
        config_path = (
            project_folder
            / ".multinear"
            / project_config.get("config_file", "config.yaml")
        )
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

        # Construct path to task_runner.py
        task_runner_path = project_folder / ".multinear" / "task_runner.py"

        if not task_runner_path.exists():
            raise FileNotFoundError(f"Task runner file not found at {task_runner_path}")

        # Dynamically load the task runner module
        try:
            spec = importlib.util.spec_from_file_location(
                "task_runner", task_runner_path
            )
            task_runner_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(task_runner_module)
        except Exception as e:
            error_msg = f"Failed to load task_runner.py: {str(e)}"
            console = Console()
            console.print(f"[red bold]{error_msg}[/red bold]")
            console.print_exception()
            job.update(
                status=TaskStatus.FAILED, details={"error": error_msg, "status_map": {}}
            )
            yield {
                "status": TaskStatus.FAILED,
                "total": 0,
                "error": error_msg,
                "status_map": {},
            }
            return

        # Check if run_task exists in the module
        if not hasattr(task_runner_module, "run_task"):
            error_msg = f"run_task function not found in {task_runner_path}"
            job.update(
                status=TaskStatus.FAILED, details={"error": error_msg, "status_map": {}}
            )
            yield {
                "status": TaskStatus.FAILED,
                "total": 0,
                "error": error_msg,
                "status_map": {},
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
                    details={"error": error_msg, "status_map": {}},
                )
                yield {
                    "status": TaskStatus.FAILED,
                    "total": 0,
                    "error": error_msg,
                    "status_map": {},
                }
                return

        # Determine tasks to run based on config structure and filters
        all_tasks = []
        global_repeat = config.get("meta", {}).get("repeat", 1)

        if "groups" in config:
            # Using groups structure
            if group_id:
                # Filter to only include tasks from the specified group
                for group in config["groups"]:
                    if group.get("id") == group_id and "tasks" in group:
                        if challenge_id:
                            # Filter tasks by challenge_id
                            clean_challenge_id = challenge_id
                            if (
                                "_" in challenge_id
                                and challenge_id.split("_")[1].isdigit()
                            ):
                                clean_challenge_id = challenge_id.split("_")[0]
                            tasks = [
                                t
                                for t in group["tasks"]
                                if t.get("id") == clean_challenge_id
                            ]
                            if tasks:
                                all_tasks.append({"group_id": group_id, "tasks": tasks})
                        else:
                            all_tasks.append(
                                {"group_id": group_id, "tasks": group["tasks"]}
                            )
                        break
                if not all_tasks:
                    raise ValueError(
                        f"No group found with ID {group_id} or no matching tasks"
                    )
            else:
                # Include tasks from all groups
                for group in config["groups"]:
                    if "tasks" in group:
                        group_tasks = group["tasks"]
                        if challenge_id:
                            # Filter tasks by challenge_id
                            clean_challenge_id = challenge_id
                            if (
                                "_" in challenge_id
                                and challenge_id.split("_")[1].isdigit()
                            ):
                                clean_challenge_id = challenge_id.split("_")[0]
                            group_tasks = [
                                t
                                for t in group_tasks
                                if t.get("id") == clean_challenge_id
                            ]
                        if group_tasks:
                            all_tasks.append(
                                {
                                    "group_id": group.get("id", "unknown"),
                                    "tasks": group_tasks,
                                }
                            )
        elif "tasks" in config:
            # Using traditional tasks structure
            tasks = config["tasks"]
            if challenge_id:
                # Filter tasks by challenge_id
                clean_challenge_id = challenge_id
                if "_" in challenge_id and challenge_id.split("_")[1].isdigit():
                    clean_challenge_id = challenge_id.split("_")[0]
                tasks = [t for t in tasks if t.get("id") == clean_challenge_id]
            if tasks:
                all_tasks.append({"group_id": None, "tasks": tasks})

        if not all_tasks:
            raise ValueError("No tasks to run found in config.yaml")

        # Calculate total tasks across all groups
        total_tasks = 0
        for group_data in all_tasks:
            for task in group_data["tasks"]:
                total_tasks += task.get("repeat", global_repeat)

        yield {"status": TaskStatus.STARTING, "total": total_tasks}

        # Run each group of tasks
        all_results = []
        current_task_offset = 0

        for group_data in all_tasks:
            # Run the group and collect results
            group_tasks = group_data["tasks"]

            for update in run_group(
                group_tasks,
                job,
                task_runner_module,
                config,
                current_task_offset,
                total_tasks,
            ):
                if isinstance(update, list):  # Results from run_group
                    all_results.extend(update)
                else:  # Status update
                    yield update

            # Update the offset for the next group
            current_task_offset += sum(
                task.get("repeat", global_repeat) for task in group_tasks
            )

        yield {
            "status": TaskStatus.COMPLETED,
            "current": total_tasks,
            "total": total_tasks,
            "results": all_results,
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
            "status_map": TaskModel.get_status_map(job.id),
        }
