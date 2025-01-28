from rich.console import Console
from rich.table import Table
from datetime import timezone

from ..utils import format_duration, get_score_color, get_current_project
from ...engine.storage import JobModel, TaskStatus


def add_parser(subparsers):
    parser = subparsers.add_parser('recent', help='Show recent experiment runs')
    parser.add_argument('--config', type=str, help='Name of custom config.yaml file')
    parser.set_defaults(func=handle)


def handle(args):
    project = get_current_project(args.config)
    if not project:
        return

    # Get recent jobs
    jobs = JobModel.list_recent(project.id, limit=10)

    # Create and configure the table
    console = Console()
    table = Table(
        title=f"Recent Experiments for {project.name}",
        show_header=True,
        header_style="bold cyan"
    )

    # Add columns
    table.add_column("Run ID", style="dim")
    table.add_column("Date & Time")
    table.add_column("Duration")
    table.add_column("Model Version")
    table.add_column("Total Tests", justify="right")
    table.add_column("Score", justify="center")
    table.add_column("Results")

    # Add rows
    for job in jobs:
        details = job.details or {}
        status_map = details.get("status_map", {})

        # Calculate statistics
        total = len(status_map)
        passed = sum(
            1 for status in status_map.values() if status == TaskStatus.COMPLETED
        )
        failed = sum(1 for status in status_map.values() if status == TaskStatus.FAILED)
        regression = total - passed - failed
        score = (passed / total) if total > 0 else 0

        # Get model info
        model = job.get_model_summary()

        # Format results bar using unicode blocks
        if total > 0:
            bar_length = 20
            # Calculate exact number of blocks, keeping fractional parts
            pass_ratio = passed / total
            fail_ratio = failed / total
            regr_ratio = regression / total

            # Calculate blocks
            pass_blocks = int(pass_ratio * bar_length)
            fail_blocks = int(fail_ratio * bar_length)
            regr_blocks = int(regr_ratio * bar_length)

            # Calculate remainder and add it to the last non-zero category
            remainder = bar_length - (pass_blocks + fail_blocks + regr_blocks)
            if remainder > 0:
                if regression > 0:
                    regr_blocks += remainder
                elif failed > 0:
                    fail_blocks += remainder
                else:
                    pass_blocks += remainder

            results_bar = (
                f"[green]{'█' * pass_blocks}[/green]"
                f"[red]{'█' * fail_blocks}[/red]"
                f"[yellow]{'█' * regr_blocks}[/yellow]"
            )
        else:
            results_bar = ""

        # Add row to table
        table.add_row(
            job.id[-8:],  # Short ID
            job.created_at.strftime("%Y-%m-%d %H:%M"),
            format_duration(
                job.created_at.replace(tzinfo=timezone.utc).isoformat(),
                (
                    job.finished_at.replace(tzinfo=timezone.utc).isoformat()
                    if job.finished_at
                    else None
                ),
            ),
            model,
            str(total),
            f"[{get_score_color(score)}]{score:.2f}[/]",
            results_bar,
        )

    # Print the table
    console.print(table)

    # Print legend
    legend = Table.grid(padding=1)
    legend.add_column()
    legend.add_row(
        "[green]█[/green] Pass", "[red]█[/red] Fail", "[yellow]█[/yellow] Regression"
    )
    console.print("\nLegend:", legend)
