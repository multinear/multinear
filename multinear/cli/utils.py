import re
from datetime import datetime
from pathlib import Path
from typing import Optional
from rich.console import Console

from ..engine.storage import ProjectModel, TaskStatus, init_project_db


def get_config_path(custom_config: Optional[str] = None) -> Path:
    """Get the path to the config file, using custom path if provided."""
    if custom_config:
        path = Path(custom_config + ".yaml")
        if not path.is_absolute():
            path = Path.cwd() / ".multinear" / path
        return path
    return Path.cwd() / ".multinear" / "config.yaml"


def slugify(text: str) -> str:
    """Convert text to a slug suitable for URLs or identifiers."""
    text = re.sub(r'[^\w\s-]', '', text)
    return re.sub(r'[-\s]+', '-', text).strip().lower()


def format_duration(created_at: str, finished_at: Optional[str]) -> str:
    """Format duration between created_at and finished_at timestamps."""
    if not finished_at:
        return "-"

    start = datetime.fromisoformat(created_at.replace('Z', '+00:00'))
    end = datetime.fromisoformat(finished_at.replace('Z', '+00:00'))
    duration = end - start

    minutes = duration.seconds // 60
    seconds = duration.seconds % 60

    if minutes > 0:
        return f"{minutes}m {seconds}s"
    return f"{seconds}s"


def get_score_color(score: float) -> str:
    """Get color for score based on value."""
    if score >= 0.9:
        return "green"
    elif score >= 0.7:
        return "yellow"
    return "red"


def format_task_status(status: str) -> str:
    """Get colored status string."""
    if status == TaskStatus.COMPLETED:
        return f"[green]{status}[/green]"
    elif status == TaskStatus.FAILED:
        return f"[red]{status}[/red]"
    return f"[yellow]{status}[/yellow]"


def get_current_project(custom_config: Optional[str] = None) -> Optional[ProjectModel]:
    """Get the current project from the database, initializing if necessary."""
    try:
        config_path = get_config_path(custom_config)
        project_id = init_project_db(config_path)
        return ProjectModel.find(project_id)
    except FileNotFoundError as e:
        console = Console()
        console.print(f"[red]Error: {str(e)}[/red]")
        console.print(
            "[red]Error:[/red] .multinear directory not found. "
            "Please run 'multinear init' first."
        )
        return None
    except Exception as e:
        console = Console()
        console.print(f"[red]Error: {str(e)}[/red]")
        return None
