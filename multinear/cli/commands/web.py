from pathlib import Path
from rich.console import Console
import uvicorn

from ..utils import get_current_project


def add_parser(subparsers):
    parser_web = subparsers.add_parser('web', help='Start platform web server')
    parser_web_dev = subparsers.add_parser(
        'web_dev', help='Start development web server with auto-reload'
    )
    for parser in [parser_web, parser_web_dev]:
        parser.add_argument(
            '--port', type=int, default=8000, help='Port to run the server on'
        )
        parser.add_argument(
            '--host', type=str, default='127.0.0.1', help='Host to run the server on'
        )


def handle(args):
    project = get_current_project()
    if not project:
        return

    uvicorn_config = {
        "app": "multinear.main:app",
        "host": args.host,
        "port": args.port,
    }

    if args.command == 'web_dev':
        # Add project directories to watch list for auto-reload
        current_dir = Path(__file__).parent.parent
        parent_dir = str(current_dir.parent)
        cwd = str(Path.cwd())
        uvicorn_config.update({
            "reload": True,
            "reload_dirs": [parent_dir, cwd],
            "reload_includes": ["*.py", "*.yaml"]
        })

    console = Console()
    mode = 'development' if args.command == 'web_dev' else 'production'
    console.print(f"Starting {mode} server on {args.host}:{args.port}")

    # Run the Uvicorn server with the specified configuration
    uvicorn.run(**uvicorn_config)


def handle_dev(args):
    args.command = 'web_dev'
    handle(args)
