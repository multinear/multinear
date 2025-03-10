import importlib.util
from pathlib import Path
from typing import Dict, Any
from rich.console import Console
import yaml

from .storage import JobModel, TaskModel, TaskStatus
from ..utils.git import get_git_revision
from .run_select import select_tasks
from .run_group import run_group


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
        # print(f"Git revision: {git_revision}")
        job.update(details={"git_revision": git_revision})

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
        all_tasks = select_tasks(config, challenge_id, group_id)

        global_repeat = config.get("meta", {}).get("repeat", 1)

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
