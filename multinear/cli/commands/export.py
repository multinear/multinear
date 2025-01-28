import json
from pathlib import Path
from rich.console import Console

from ..utils import get_current_project
from ...engine.storage import JobModel, TaskModel


def add_parser(subparsers):
    parser = subparsers.add_parser('export', help='Export experiment run to JSON file')
    parser.add_argument('job_id', help='Job ID (or last 8 characters)')
    parser.add_argument(
        '-o', '--output',
        help='Output file path (default: <job_id>.json)',
        type=str
    )
    parser.add_argument('--config', type=str, help='Name of custom config.yaml file')
    parser.set_defaults(func=handle)


def handle(args):
    project = get_current_project(args.config)
    if not project:
        return

    console = Console()

    # Find the job
    try:
        # Support both full and truncated job IDs
        jobs = JobModel.list_recent(project.id)
        job = next(
            (j for j in jobs if j.id.endswith(args.job_id)),
            None
        )
        if not job:
            console.print(f"[red]Error: Job {args.job_id} not found[/red]")
            return
    except Exception as e:
        console.print(f"[red]Error finding job: {e}[/red]")
        return

    # Prepare export data
    export_data = {
        "job_id": job.id,
        "project_id": job.project_id,
        "created_at": job.created_at.isoformat(),
        "finished_at": job.finished_at.isoformat() if job.finished_at else None,
        "status": job.status,
        "model": job.get_model_summary(),
        "details": job.details,
        "tasks": TaskModel.get_status_map(job.id)
    }

    # Determine output path
    output_path = args.output if args.output else f"{job.id}.json"
    output_path = Path(output_path)

    try:
        # Ensure parent directory exists
        output_path.parent.mkdir(parents=True, exist_ok=True)

        # Write the JSON file
        with open(output_path, 'w') as f:
            json.dump(export_data, f, indent=2)

        console.print(f"[green]Successfully exported job data to {output_path}[/green]")

    except Exception as e:
        console.print(f"[red]Error exporting data: {e}[/red]")
