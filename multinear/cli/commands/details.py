from datetime import timezone
from typing import Optional
from rich.console import Console
from rich.table import Table

from ..utils import (
    format_duration,
    get_score_color,
    format_task_status,
    get_current_project
)
from ...engine.storage import JobModel, ProjectModel, TaskModel


def add_parser(subparsers):
    parser = subparsers.add_parser(
        'details', help='Show detailed information about a specific run'
    )
    parser.add_argument('run_id', help='Partial or full ID of the run to show')
    parser.set_defaults(func=handle)


def handle(args):
    partial_id = args.run_id
    job = find_run_by_partial_id(partial_id)
    if not job:
        console = Console()
        console.print(f"[red]Error:[/red] No run found matching ID '{partial_id}'")
        return

    print_details(Console(), job)


def print_details(console, job):
    """Extracted function to print all details to the given console"""
    project = ProjectModel.find(job.project_id)
    tasks = TaskModel.list(job.id)

    # Header
    console.print(f"\n[bold]Run: {job.id[-8:]} (Full ID: {job.id})[/bold]")
    console.print(f"Project: {project.name}")
    console.print(f"Created: {job.created_at.strftime('%Y-%m-%d %H:%M:%S')}")

    # Summary Card
    summary = Table(show_header=False, box=None)
    summary.add_column("Metric", style="cyan")
    summary.add_column("Value")

    summary.add_row("Status", format_task_status(job.status))
    summary.add_row("Total Tasks", str(len(tasks)))
    summary.add_row("Model", job.details.get("model", "N/A") if job.details else "N/A")

    console.print("\n[bold]Summary[/bold]")
    console.print(summary)

    # Tasks Table
    tasks_table = Table(
        title="\nTasks",
        show_header=True,
        header_style="bold cyan"
    )

    tasks_table.add_column("Task ID", style="dim")
    tasks_table.add_column("Started")
    tasks_table.add_column("Duration")
    tasks_table.add_column("Model")
    tasks_table.add_column("Status")
    tasks_table.add_column("Score", justify="right")

    for task in tasks:
        # Format duration
        duration = format_duration(
            task.created_at.replace(tzinfo=timezone.utc).isoformat(),
            (
                task.finished_at.replace(tzinfo=timezone.utc).isoformat()
                if task.finished_at
                else None
            ),
        )

        # Format score with color
        score = task.eval_score or 0
        score_color = get_score_color(score)
        score_text = f"[{score_color}]{score:.2f}[/]"

        tasks_table.add_row(
            task.id[-8:],
            task.created_at.strftime("%H:%M:%S"),
            duration,
            task.task_details.get("model", "N/A") if task.task_details else "N/A",
            format_task_status(task.status),
            score_text
        )

    console.print(tasks_table)

    # Detailed Task View
    for task in tasks:
        console.print(f"\n[bold cyan]Task Details: {task.id[-8:]}[/bold cyan]")

        # Task Information
        task_details = Table(show_header=False, box=None)
        task_details.add_column("Field", style="cyan")
        task_details.add_column("Value")

        task_details.add_row("Status", format_task_status(task.status))
        task_details.add_row("Created", task.created_at.strftime("%Y-%m-%d %H:%M:%S"))
        if task.finished_at:
            task_details.add_row(
                "Finished", task.finished_at.strftime("%Y-%m-%d %H:%M:%S")
            )
        task_details.add_row(
            "Duration",
            format_duration(
                task.created_at.replace(tzinfo=timezone.utc).isoformat(),
                (
                    task.finished_at.replace(tzinfo=timezone.utc).isoformat()
                    if task.finished_at
                    else None
                ),
            ),
        )

        console.print(task_details)

        # Input
        if task.task_input:
            console.print("\n[bold]Input:[/bold]")
            input_text = (
                task.task_input['str']
                if isinstance(task.task_input, dict) and 'str' in task.task_input
                else str(task.task_input)
            )
            console.print(input_text)

        # Output
        if task.task_output:
            console.print("\n[bold]Output:[/bold]")
            output_text = (
                task.task_output['str']
                if isinstance(task.task_output, dict) and 'str' in task.task_output
                else str(task.task_output)
            )
            console.print(output_text)

        # Evaluation Results
        if task.eval_details:
            console.print("\n[bold]Evaluation Results:[/bold]")
            eval_table = Table(show_header=True)
            eval_table.add_column("Criterion")
            eval_table.add_column("Score", justify="right")
            eval_table.add_column("Rationale")

            for ev in task.eval_details.get("evaluations", []):
                score = ev["score"]
                score_color = get_score_color(score)
                eval_table.add_row(
                    ev["criterion"],
                    f"[{score_color}]{score:.2f}[/]",
                    ev["rationale"]
                )

            console.print(eval_table)


def find_run_by_partial_id(partial_id: str) -> Optional[JobModel]:
    """
    Find a run by partial ID (last N characters).
    Returns the most recent matching run if multiple found.
    """
    project = get_current_project()
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
