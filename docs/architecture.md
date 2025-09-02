# Multinear Architecture

Multinear consists of several components:

- **CLI (`cli/` folder)**: Command-line interface for initializing projects and starting the web server.
- **Web Server (`main.py`)**: A FastAPI application serving API endpoints and static Svelte frontend files.
- **Engine (`engine/` folder)**:
  - **Run Management (`run.py`)**: Handles execution of tasks and evaluation.
  - **Storage (`storage.py`)**: Manages data models and database operations using SQLAlchemy.
  - **Evaluation (`evaluate.py`, `checklist.py`)**: Provides evaluation mechanisms for task outputs.
- **API (`api/` folder)**: Defines API routes and schemas for interaction with the frontend.
- **Utilities (`utils/capture.py`)**: Captures task execution output and logs.
- **Frontend**: A Svelte-based interface for interacting with the platform (located in `multinear/frontend/`).

## Development

To install Multinear and its dependencies for local development, run:

```bash
git clone https://github.com/multinear/multinear
cd multinear
make install
```

This will install the required Python packages.

For development mode with auto-reload on file changes, use:

```bash
multinear web_dev
```

## Contributing to Multinear

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make your changes with clear commit messages.
4. Submit a pull request to the `main` branch.

Please ensure that your code adheres to the project's coding standards and passes all tests.

## Further Reading

- [Introduction](/README.md)
- [Full Quickstart Guide](/docs/quickstart.md) – Get set up quickly.
- [Defining Evaluations](/docs/evaluations.md) – Learn how to design great tests.
- [Running Experiments](/docs/experiments.md) – Run, benchmark, and iterate.
- [Analyzing Results](/docs/results.md) – Understand outcomes clearly.
- [CLI Reference](/docs/cli.md) – Automate your workflow.
