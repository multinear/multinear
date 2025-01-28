from datetime import timezone
from typing import Optional
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
import json

from ..utils import (
    format_duration,
    format_task_status,
    get_current_project
)
from ...engine.storage import JobModel, ProjectModel, TaskModel, TaskStatus


def add_parser(subparsers):
    parser = subparsers.add_parser(
        'details', help='Show detailed information about a specific run'
    )
    parser.add_argument('run_id', help='Partial or full ID of the run to show')
    parser.add_argument('--config', type=str, help='Name of custom config.yaml file')
    parser.set_defaults(func=handle)


def handle(args):
    partial_id = args.run_id
    job = find_run_by_partial_id(partial_id, args.config)
    if not job:
        console = Console()
        console.print(f"[red]Error:[/red] No run found matching ID '{partial_id}'")
        return

    print_details(Console(), job)


def print_run_header(
    console: Console,
    job: JobModel,
    project: ProjectModel,
    tasks: list
):
    """Print the run header with key information"""
    # Create run details table
    run_details = Table(show_header=False, box=None, padding=(0, 2))
    run_details.add_column("Field", style="cyan", width=12)
    run_details.add_column("Value")

    run_details.add_row("Run ID", job.id)
    run_details.add_row("Project", project.name)
    run_details.add_row("Created", job.created_at.strftime("%Y-%m-%d %H:%M:%S"))

    # Create summary table
    summary = Table(show_header=False, box=None, padding=(0, 2))
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value")

    # Calculate statistics
    total = len(tasks)
    completed = sum(1 for t in tasks if t.status == TaskStatus.COMPLETED)
    failed = sum(1 for t in tasks if t.status == TaskStatus.FAILED)
    in_progress = total - completed - failed

    # Format task counts
    task_counts = []
    if completed > 0:
        task_counts.append(f"{completed} completed")
    if failed > 0:
        task_counts.append(f"{failed} failed")
    if in_progress > 0:
        task_counts.append(f"{in_progress} in progress")

    task_status = f"{total} ({', '.join(task_counts)})"

    # Add rows with enhanced formatting
    summary.add_row(
        "Status",
        format_task_status(job.status)
    )
    summary.add_row(
        "Total Tasks",
        task_status
    )
    summary.add_row(
        "Model",
        job.details.get("model", "N/A") if job.details else "N/A"
    )

    if job.finished_at:
        created_at = job.created_at.replace(tzinfo=timezone.utc).isoformat()
        finished_at = job.finished_at.replace(tzinfo=timezone.utc).isoformat()
        summary.add_row("Duration", format_duration(created_at, finished_at))

    # Create a table for side-by-side layout
    layout_table = Table(show_header=False, box=None, padding=0, collapse_padding=True)
    layout_table.add_column("Run Details", ratio=1)
    layout_table.add_column("Summary", ratio=2)

    # Add the panels to the table
    layout_table.add_row(
        Panel(run_details, title="Run Details"),
        Panel(summary, title="Summary")
    )

    console.print("\n[bold]🔍 Run Information[/bold]")
    console.print(layout_table)


def print_tasks_overview(console: Console, tasks: list):
    """Print an overview table of all tasks"""
    tasks_table = Table(
        title="Tasks Overview",
        show_header=True,
        header_style="bold cyan",
        padding=(0, 1),
        expand=True
    )

    # Define columns
    tasks_table.add_column("ID", style="dim")
    tasks_table.add_column("Status", justify="center")
    tasks_table.add_column("Duration")
    tasks_table.add_column("Model")
    tasks_table.add_column("Score", justify="right")

    # Add rows for each task
    for task in tasks:
        # Calculate duration
        created_at = task.created_at.replace(tzinfo=timezone.utc).isoformat()
        finished_at = None
        if task.finished_at:
            finished_at = task.finished_at.replace(tzinfo=timezone.utc).isoformat()
        duration = format_duration(created_at, finished_at)

        # Format score with percentage and adjusted colors
        score = task.eval_score or 0
        score_percentage = int(score * 100)
        if score >= 0.9:
            score_color = "green"
        elif score > 0:
            score_color = "yellow"
        else:
            score_color = "red"
        score_text = f"[{score_color}]{score_percentage}%[/]"

        # Format status with color
        if task.status == TaskStatus.COMPLETED:
            status = "[green]completed[/green]"
        elif task.status == TaskStatus.FAILED:
            status = "[red]failed[/red]"
        elif task.status == TaskStatus.EVALUATING:
            status = "[yellow]evaluating[/yellow]"
        else:
            status = "[blue]running[/blue]"

        tasks_table.add_row(
            task.id[-8:],
            status,
            duration,
            task.task_details.get("model", "N/A") if task.task_details else "N/A",
            score_text,
        )

    console.print("\n[bold]📋 Tasks[/bold]")
    console.print(tasks_table)


def print_task_details(console: Console, task: TaskModel):
    """Print detailed information for a single task"""
    # Get status color for visual indicator
    if task.status == TaskStatus.COMPLETED:
        status_color = "green"
    elif task.status == TaskStatus.FAILED:
        status_color = "red"
    elif task.status == TaskStatus.EVALUATING:
        status_color = "yellow"
    else:
        status_color = "blue"

    # Create header for task details with colored lines
    console.print("\n\n")  # Add spacing
    console.print("━" * console.width, style=f"dim {status_color}")
    task_header = Text()
    task_header.append(f"Task {task.id[-8:]}", style="bold cyan")
    console.print(task_header)
    console.print("━" * console.width, style=f"dim {status_color}")

    # Create basic info table
    basic_info = Table(show_header=False, box=None, padding=(0, 2))
    basic_info.add_column("Field", style="cyan", width=12)
    basic_info.add_column("Value")

    # Add basic information
    basic_info.add_row("Status", format_task_status(task.status))
    basic_info.add_row("Created", task.created_at.strftime("%Y-%m-%d %H:%M:%S"))
    if task.finished_at:
        basic_info.add_row("Finished", task.finished_at.strftime("%Y-%m-%d %H:%M:%S"))
        created_at = task.created_at.replace(tzinfo=timezone.utc).isoformat()
        finished_at = task.finished_at.replace(tzinfo=timezone.utc).isoformat()
        basic_info.add_row("Duration", format_duration(created_at, finished_at))

    # Create task details table
    task_details_table = Table(show_header=False, box=None, padding=(0, 2))
    task_details_table.add_column("Field", style="cyan")
    task_details_table.add_column("Value")

    # Add task details if available
    if task.task_details:
        for key, value in task.task_details.items():
            formatted_value = (
                value if isinstance(value, str)
                else Text(json.dumps(value, indent=2), style="white")
            )
            task_details_table.add_row(key, formatted_value)

    # Create a table for side-by-side layout
    layout_table = Table(show_header=False, box=None, padding=0, collapse_padding=True)
    layout_table.add_column("Basic Info", ratio=1)
    layout_table.add_column("Task Details", ratio=2)

    # Add the panels to the table
    layout_table.add_row(
        Panel(basic_info, title="Basic Info"),
        Panel(
            task_details_table if task.task_details else "No task details available",
            title="Task Details"
        )
    )

    # Print the layout
    console.print(layout_table)

    # Print input/output if available in a side-by-side layout
    if task.task_input or task.task_output:
        console.print("\n[bold cyan]Input/Output:[/bold cyan]")
        io_table = Table(
            show_header=True,
            padding=(0, 1),
            expand=True
        )
        io_table.add_column("Input", ratio=1, style="cyan")
        io_table.add_column("Output", ratio=1)

        input_text = (
            task.task_input['str']
            if isinstance(task.task_input, dict) and 'str' in task.task_input
            else str(task.task_input) if task.task_input else ""
        )
        output_text = Text(
            task.task_output['str']
            if isinstance(task.task_output, dict) and 'str' in task.task_output
            else str(task.task_output) if task.task_output else "",
            style="white"
        )

        io_table.add_row(input_text, output_text)
        console.print(io_table)

    # Print evaluation results if available
    if task.eval_details:
        console.print("\n[bold cyan]Evaluation Results:[/bold cyan]")
        eval_table = Table(show_header=True, padding=(0, 1))
        eval_table.add_column("Criterion", style="cyan")
        eval_table.add_column("Score", justify="right")
        eval_table.add_column("Rationale")

        for ev in task.eval_details.get("evaluations", []):
            score = ev["score"]
            score_percentage = int(score * 100)
            if score >= 0.9:
                score_color = "green"
            elif score > 0:
                score_color = "yellow"
            else:
                score_color = "red"
            eval_table.add_row(
                ev["criterion"],
                f"[{score_color}]{score_percentage}%[/]",
                ev["rationale"]
            )

        console.print(eval_table)


def print_details(console: Console, job: JobModel):
    """Print all details in a well-formatted structure"""
    project = ProjectModel.find(job.project_id)
    tasks = TaskModel.list(job.id)

    # Print main sections
    print_run_header(console, job, project, tasks)
    print_tasks_overview(console, tasks)

    # Print detailed information for each task
    for task in tasks:
        print_task_details(console, task)


def find_run_by_partial_id(partial_id: str, config_path: Optional[str] = None) -> Optional[JobModel]:
    """
    Find a run by partial ID (last N characters).
    Returns the most recent matching run if multiple found.
    """
    project = get_current_project(config_path)
    if not project:
        return None

    # Get recent jobs and find one with matching partial ID
    jobs = JobModel.list_recent(project.id, limit=100)

    matching_jobs = [
        job for job in jobs
        if job.id.endswith(partial_id) or job.id == partial_id
    ]

    if not matching_jobs:
        return None

    # Return the most recent matching job
    return matching_jobs[0]
