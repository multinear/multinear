# Multinear: CLI Reference

Quickly and easily run, analyze, and manage your experiments from the command line.

## Commands

### Run Experiments

- **`multinear run [--group <group_id>] [--config <name>]`**  
  Run your defined evaluation tasks.

```bash
multinear run                    # Run all tasks
multinear run --group retrieval  # Run tasks only from the "retrieval" group
multinear run --config staging   # Use `.multinear/staging.yaml` configuration file
```

### View Recent Runs

- **`multinear recent [--config <name>]`**  
  List recent experiment runs for quick reference.

```bash
multinear recent  # --config production
```

### Detailed Run Information

- **`multinear details <run-id|short-id> [--config <name>]`**  
  Display detailed results of a specific experiment run.

```bash
multinear details 3f8a92cd
```

### Export Experiment Data

- **`multinear export <run-id|short-id> [-o out.json] [--config <name>]`**  
  Export detailed run results to JSON format. Default output path: `run-<id>.json` in the current directory.

```bash
multinear export 3f8a92cd -o results.json
```

### Web Interface

- **`multinear web [--host 127.0.0.1] [--port 8000] [--debug] [--config <name>]`**  
  Launch the Multinear web UI for interactive experiments and results visualization.

```bash
multinear web --port 8080  # --config staging
```

- **`multinear web_dev [--host 127.0.0.1] [--port 8000] [--debug] [--config <name>]`**  
  Launch web UI in development mode with auto-reloading for config and code changes.

```bash
multinear web_dev
```

---

## Tips and Best Practices

- **Run Single Tasks Quickly**  
  Create a temporary configuration file with your single target task or leverage the API directly.

- **Short IDs**  
  Use the last 8 characters of run IDs for quick referencing in commands.

- **Automate Your Workflow**  
  Integrate `multinear run` within your CI/CD pipeline scripts to automatically detect regressions early in your development cycle.

- **Alternate Configurations (`--config`)**  
  Ideal for testing multiple evaluation scenarios without altering your primary configuration.

## Further Reading

Next: [Architecture & Contributing](/docs/architecture.md) – Learn or contribute to Multinear.

Contents

- [Introduction](/README.md)
- [Full Quickstart Guide](/docs/quickstart.md) – Get set up quickly.
- [Evaluations Reference](/docs/evaluations.md) – Deep dive into defining great tests.
- [Running Experiments](/docs/experiments.md) – Advanced experiment workflows.
- [Analyzing Results](/docs/results.md) – Understand outcomes clearly.
