from pathlib import Path
from jinja2 import Template
from rich.console import Console

from ..utils import slugify


def add_parser(subparsers):
    parser = subparsers.add_parser('init', help='Initialize a new Multinear project')
    parser.set_defaults(func=handle)


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

    # Prompt the user for project details
    project_name = input("Project name: ").strip()
    default_id = slugify(project_name)
    project_id = input(f"Project ID [{default_id}]: ").strip() or default_id
    description = input("Project description: ").strip()

    # Read the configuration template
    template_path = Path(__file__).parent.parent / 'templates' / 'config.yaml'
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

    console.print(
        f"\n[green]Project initialized successfully in {MULTINEAR_CONFIG_DIR}[/green]"
    )
    console.print("You can now run 'multinear web' to start the server")
