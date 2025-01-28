import argparse
from importlib.metadata import version
from .commands import init, run, recent, details, web, export


def get_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Multinear CLI tool")
    parser.add_argument('--version', action='version',
                        version=f'%(prog)s {version("multinear")}')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # Define commands
    init.add_parser(subparsers)
    run.add_parser(subparsers)
    recent.add_parser(subparsers)
    details.add_parser(subparsers)
    web.add_parser(subparsers)
    export.add_parser(subparsers)

    return parser


def main():
    parser = get_parser()
    args = parser.parse_args()

    command_handlers = {
        'init': init.handle,
        'run': run.handle,
        'recent': recent.handle,
        'details': details.handle,
        'web': web.handle,
        'web_dev': web.handle_dev,
        'export': export.handle,
    }

    if args.command in command_handlers:
        command_handlers[args.command](args)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
