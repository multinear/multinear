from typing import Dict, Any, List, Iterator, Tuple
from rich.console import Console
import random
import hashlib
import json
import queue
import time
from concurrent.futures import ThreadPoolExecutor

from .storage import JobModel, TaskModel, TaskStatus
from .evaluate import evaluate
from ..utils.capture import OutputCapture
from .utils import rephrase_input


def rephrase_task_input(
    task: Dict[str, Any], previous_variations: List[Any], config: Dict[str, Any]
) -> Tuple[Dict[str, Any], List[Any]]:
    """
    Rephrase a task's input based on previous variations.

    Args:
        task: The task definition
        previous_variations: List of previous variations for this task
        config: Configuration dictionary

    Returns:
        Tuple of (rephrased task, updated previous_variations)
    """
    task_copy = task.copy()
    input = task_copy["input"]
    global_rephrase = config.get("meta", {}).get("rephrase", False)
    do_rephrase = task.get("rephrase", global_rephrase)

    # Create a new list for updated variations
    updated_variations = previous_variations.copy()

    if do_rephrase:
        # If the input is a dictionary, rephrase the 'question' key only
        if isinstance(input, dict) and 'question' in input:
            rephrased_question = rephrase_input(input['question'], updated_variations)
            if isinstance(rephrased_question, str):
                updated_variations.append(rephrased_question)
            task_copy["input"] = {**input, 'question': rephrased_question}
        else:
            rephrased_input = rephrase_input(input, updated_variations)
            if isinstance(rephrased_input, str):
                updated_variations.append(rephrased_input)
            task_copy["input"] = rephrased_input

    return task_copy, updated_variations


def execute_task(
    task: Dict[str, Any],
    job: JobModel,
    task_runner_module,
    current_task: int,
    total_tasks: int,
    config: Dict[str, Any],
    repeat: int = 0,
    update_queue: queue.Queue = None,
) -> Dict[str, Any]:
    """
    Execute a single task and return results and updates.

    Args:
        task: Task definition
        job: JobModel instance
        task_runner_module: Module with run_task function
        current_task: Current task number
        total_tasks: Total tasks to process
        config: Configuration dictionary
        repeat: Current repeat number (0-indexed)
        update_queue: Queue to send real-time updates (optional)

    Returns:
        Dict with results
    """
    result = None
    repeats = task.get("repeat", config.get("meta", {}).get("repeat", 1))

    try:
        input = task["input"]  # Input should already be rephrased if needed

        challenge_id = task.get("id", None)
        if not challenge_id:  # Calculate challenge ID from input
            challenge_id = hashlib.sha256(json.dumps(input).encode()).hexdigest()

        # Append repeat counter to challenge_id if this is a repeat
        if repeat > 0:
            challenge_id = f"{challenge_id}_{repeat}"

        # Start new task
        task_id = TaskModel.start(
            job_id=job.id, task_number=current_task, challenge_id=challenge_id
        )

        # Running status update
        running_update = {
            "status": TaskStatus.RUNNING,
            "current": current_task,
            "total": total_tasks,
            "details": (
                f"Running task {current_task}/{total_tasks}"
                + (f" (repeat {repeat + 1}/{repeats})" if repeat > 0 else "")
            ),
        }

        # Send update directly to queue if provided
        if update_queue:
            update_queue.put(running_update)

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

        # Evaluating status update
        evaluating_update = {
            "status": TaskStatus.EVALUATING,
            "current": current_task,
            "total": total_tasks,
            "details": f"Evaluating task {current_task}/{total_tasks}",
        }

        # Send update directly to queue if provided
        if update_queue:
            update_queue.put(evaluating_update)

        # Inject global context into the task
        task_copy = task.copy()
        task_copy["context"] = config.get("meta", {}).get("context", "")

        # Inject global checklist, if present
        global_checklist = config.get("meta", {}).get("checklist", None)
        if global_checklist and "checklist" not in task_copy:
            task_copy["checklist"] = global_checklist

        global_custom = config.get("meta", {}).get("custom", None)
        if global_custom and "custom" not in task_copy:
            task_copy["custom"] = global_custom

        # Evaluate the task
        with OutputCapture() as capture:
            eval_result = evaluate(
                task_copy, input, task_result["output"], task_runner_module
            )
        TaskModel.evaluated(
            task_id,
            {k: v for k, v in task_copy.items() if k != "input"},
            eval_result["passed"],
            eval_result["score"],
            eval_result["details"],
            capture.logs,
        )

        result = [task_result, eval_result]

    except Exception as e:
        error_msg = str(e)
        console = Console()
        console.print(
            f"[red bold]Error running task {current_task}/{total_tasks}:[/red bold] {error_msg}"
        )
        console.print_exception()
        result = {"error": error_msg}
        TaskModel.fail(task_id, error=error_msg)
        # Update job details with the error
        job.update(
            status=TaskStatus.FAILED,
            details={
                "error": error_msg,
                "status_map": TaskModel.get_status_map(job.id),
            },
        )

    return result


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
    max_workers = max(1, config.get("meta", {}).get("max_workers", 1))
    results = []

    # Group tasks by their ID to handle previous_variations correctly
    task_groups = {}
    current_task = current_task_offset

    # First pass: organize tasks by ID and prepare executions
    for task in tasks:
        task_id = task.get(
            "id", hashlib.sha256(json.dumps(task["input"]).encode()).hexdigest()
        )
        repeats = task.get("repeat", global_repeat)

        if task_id not in task_groups:
            task_groups[task_id] = {
                "task": task,
                "executions": [],
                "previous_variations": [],
            }

        for repeat in range(repeats):
            current_task += 1
            task_groups[task_id]["executions"].append(
                {"repeat": repeat, "task_number": current_task}
            )

    # Create a shared queue for real-time updates
    update_queue = queue.Queue()

    # Create thread pool
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Process each task group sequentially, but execute tasks in parallel
        futures = []

        for task_id, group in task_groups.items():
            task = group["task"]
            previous_variations = group["previous_variations"]

            for execution in group["executions"]:
                repeat = execution["repeat"]
                task_number = execution["task_number"]

                # Rephrase the task input if needed (only for repeats after the first one)
                if repeat > 0:
                    task_copy, previous_variations = rephrase_task_input(
                        task, previous_variations, config
                    )
                else:
                    task_copy = task.copy()

                # Submit the task to the thread pool
                future = executor.submit(
                    execute_task,
                    task_copy,
                    job,
                    task_runner_module,
                    task_number,
                    total_tasks,
                    config,
                    repeat,
                    update_queue  # Pass the update queue to the task
                )
                futures.append(future)

                # Process any available updates from the queue
                while True:
                    try:
                        update = update_queue.get_nowait()
                        yield update
                        update_queue.task_done()
                    except queue.Empty:
                        break

        # Continue processing updates until all tasks are complete
        completed = 0
        total_to_complete = len(futures)

        while completed < total_to_complete:
            # Check for completed futures
            newly_completed = sum(1 for f in futures if f.done())
            if newly_completed > completed:
                completed = newly_completed

            # Process updates from the queue
            try:
                update = update_queue.get(timeout=0.1)
                yield update
                update_queue.task_done()
            except queue.Empty:
                # No updates at the moment, continue
                # Add a small sleep to prevent CPU spinning
                time.sleep(0.01)

        # Collect results from all futures
        for future in futures:
            try:
                result = future.result()
                if result:
                    results.append(result)
            except Exception as e:
                console = Console()
                console.print(f"[red bold]Error in task execution:[/red bold] {str(e)}")
                console.print_exception()
                results.append({"error": str(e)})

    return results
