from typing import Dict, Any, List, Iterator
from rich.console import Console
import random
import hashlib
import json

from .storage import JobModel, TaskModel, TaskStatus
from .evaluate import evaluate
from ..utils.capture import OutputCapture
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
