import tqdm
from pathlib import Path
from rich.console import Console
from rich.table import Table

from .details import print_details
from ..utils import get_current_project
from ...engine.run import run_experiment
from ...engine.storage import JobModel, TaskModel


def add_parser(subparsers):
    parser = subparsers.add_parser('run', help='Run experiment and track progress')
    parser.add_argument('--config', type=str, help='Name of custom config.yaml file')
    parser.add_argument('--group', type=str, help='Run only tasks from the specified group')
    parser.set_defaults(func=handle)


def handle(args):
    project = get_current_project(args.config)
    if not project:
        return
    job_id = JobModel.start(project.id)
    job = JobModel.find(job_id)

    # Initialize Rich consoles
    console = Console()
    console_plain = Console(no_color=True, force_terminal=False, width=120)

    # Execute the experiment with progress tracking
    results = []
    pbar = None

    try:
        # Add config file to project config if specified
        project_dict = project.to_dict()
        if args.config:
            project_dict["config_file"] = args.config + ".yaml"

        # Run the experiment with optional group filtering
        for update in run_experiment(project_dict, job, group_id=args.group):
            results.append(update)

            # Add status map from TaskModel to the update
            update["status_map"] = TaskModel.get_status_map(job_id)

            # Update job status in the database
            job.update(
                status=update["status"],
                total_tasks=update.get("total", 0),
                current_task=update.get("current"),
                details=update
            )

            # Initialize progress bar when we get total tasks
            if pbar is None and update.get("total") is not None:
                pbar = tqdm.tqdm(total=update["total"], desc="Running Experiment")

            # Update progress bar if initialized
            if pbar is not None and update.get("current") is not None:
                pbar.n = update["current"]
                pbar.refresh()

            # Update Rich console with status
            status_table = Table(title="Experiment Status")
            status_table.add_column(
                "Status", justify="left", style="cyan", no_wrap=True
            )
            status_table.add_column("Details", style="magenta")

            status_table.add_row(update["status"], update.get("details", ""))
            console.clear()
            console.print(status_table)

        # Mark the job as finished upon successful completion
        job.finish()

    except Exception as e:
        # Handle exceptions and update the job as failed
        console.print(f"[red]Error running experiment: {e}[/red]")
        job.update(
            status="failed",
            details={
                "error": str(e),
                "status_map": TaskModel.get_status_map(job_id)
            }
        )
    finally:
        # Close progress bar if it was initialized
        if pbar is not None:
            pbar.close()

    # Generate summary
    summary_table = Table(title="Experiment Summary")
    summary_table.add_column("Metric", style="cyan")
    summary_table.add_column("Value", style="magenta")

    summary_table.add_row("Job ID", job_id)
    summary_table.add_row("Final Status", results[-1]["status"])
    summary_table.add_row("Total Tasks", str(results[-1].get("total", 0)))
    summary_table.add_row("Completed Tasks", str(results[-1].get("current", 0)))

    details_message = (
        f"For detailed information about this run, use: multinear details {job_id[-8:]}"
    )

    console.print(summary_table)
    console.print(f"\n[bold cyan]{details_message}[/bold cyan]")

    # Write summary and details to .multinear/last_output.txt
    with console_plain.capture() as capture:
        console_plain.print(summary_table)
        console_plain.print(f"\n{details_message}")
    plain_output = capture.get()

    with open(Path('.multinear') / "last_output.txt", "w") as f:
        f.write(plain_output)

    # Append detailed information
    console_plain = Console(no_color=True, force_terminal=False, width=120)
    with console_plain.capture() as capture:
        print_details(console_plain, job)
    details_output = capture.get()

    with open(Path('.multinear') / "last_output.txt", "a") as f:
        f.write("\n\n" + details_output)
