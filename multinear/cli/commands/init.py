from pathlib import Path
from jinja2 import Template
from rich.console import Console

from ..utils import slugify


def add_parser(subparsers):
    parser = subparsers.add_parser('init', help='Initialize a new Multinear project')
    parser.set_defaults(func=handle)


def _get_validated_input(prompt: str, default: str = None, required: bool = True) -> str:
    """Get and validate user input with optional default value."""
    console = Console()
    while True:
        display_prompt = f"{prompt} [{default}]: " if default else f"{prompt}: "
        value = input(display_prompt).strip()

        if default and not value:
            return default
        if value or not required:
            return value

        console.print(f"[red]{prompt} cannot be empty[/red]")


def handle(args):
    MULTINEAR_CONFIG_DIR = '.multinear'
    console = Console()

    # Check if the project has already been initialized
    multinear_dir = Path(MULTINEAR_CONFIG_DIR)
    if multinear_dir.exists():
        console.print(
            f"[yellow]{MULTINEAR_CONFIG_DIR} directory already exists. "
            "Project appears to be already initialized.[/yellow]"
        )
        return

    # Create the .multinear directory for project configuration
    multinear_dir.mkdir()

    # Prompt the user for project details (with validation)
    project_name = _get_validated_input("Project name")
    project_id = _get_validated_input("Project ID", default=slugify(project_name))
    description = _get_validated_input("Project description")

    # Read the configuration template
    template_path = Path(__file__).parent.parent.parent / 'templates' / 'config.yaml'
    with open(template_path, 'r') as f:
        template_content = f.read()

    # Render the template with user-provided details
    template = Template(template_content)
    config_content = template.render(
        project_name=project_name,
        project_id=project_id,
        description=description
    )

    # Write the rendered configuration to config.yaml
    config_path = multinear_dir / 'config.yaml'
    with open(config_path, 'w') as f:
        f.write(config_content)

    # Copy task_runner.py template to project root
    task_runner_template = Path(__file__).parent.parent.parent / 'templates' / 'task_runner.py'
    task_runner_dest = multinear_dir / 'task_runner.py'

    if task_runner_template.exists():
        with open(task_runner_template, 'r') as src, open(task_runner_dest, 'w') as dst:
            dst.write(src.read())

    console.print(
        f"\n[green]Project initialized successfully in {MULTINEAR_CONFIG_DIR}[/green]"
    )
    console.print("You can now run 'multinear web' to start the server")
