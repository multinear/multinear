# README Improvements TODO

This checklist captures concrete updates to improve README.md based on the latest functionality added across the CLI, engine, and config. Each item includes suggested content and example snippets you can adapt.

## Structure

- Add a Running section covering CLI flags, and advanced runs (single task, group runs, custom config files).
- Add a Setup section for environment variables and API keys (OpenAI).
- Add a Tips and Gotchas section (challenge IDs, repeats, context propagation, etc.).

## Task Runner Hooks and Details

- Document `run_task(input) -> {output, details}` (already present) and optional `start_run()` hook to warm up clients, load caches, etc. See `multinear/engine/run.py:52`.
- Encourage providing `details.model` or similar for nicer summaries (see model summary aggregation in `multinear/engine/storage.py:147`).

## Running: CLI

- CLI additions (document flags and examples):
  - `multinear run --group <group_id>` to run only a group (`multinear/cli/commands/run.py:1`).
  - `multinear web --config <name>` and `multinear run --config <name>` to use an alternate config file living at `.multinear/<name>.yaml` (sets or uses `MULTINEAR_CONFIG`).
  - `multinear recent`, `multinear details <run-id-suffix>`, `multinear export <run-id> [-o out.json]`.
  - Short IDs: most CLI commands accept the last 8 chars of a run ID (details/export). Make this explicit in examples.

## Repeats and Rephrasing

- Explain how repeats are controlled by `meta.repeat` and `task.repeat` overrides.
- Describe rephrasing behavior (`meta.rephrase: true` or per-task `rephrase: true`) and that it uses OpenAI chat to generate unique paraphrases (requires `OPENAI_API_KEY`). See `multinear/engine/utils.py:1` and integration at `multinear/engine/run_group.py:22`.

## Setup and Environment

- Add a short section about credentials and environment:
  - `OPENAI_API_KEY` required for LLM-as-judge (Checklist/Weighted Score) and rephrasing.
  - Optional: configuring different OpenAI models if supported by `autoevals`.
  - Database location: `.multinear/multinear.db` (SQLite). See `multinear/engine/storage.py:308`.
  - Git revision: if the working directory is a Git repo, the current revision is recorded on each run and shown in recent runs and run details (`git rev-parse HEAD`). See `multinear/engine/run.py:31`.

## Tips and Gotchas

- Context propagation:
  - For single-metric tasks, `context` under the task is passed to the evaluator.
  - For multi-metric tasks, put `context` inside each metric item; alternatively, you can put `meta.context` inside the task object itself if you want a shared value across metrics (see `multinear/engine/evaluate.py:64` for how `meta.context` is read during multi-metric evaluation).
- Pass/fail semantics:
  - Single metric: pass if score >= `min_score` (default 1.0).
  - Multi‑metric: pass only if all metrics pass; overall score is the average.
- Single-task run with grouped configs:
  - The single-task API expects the raw task `id` from YAML. If you surface `group_id/<id>` in a UI, strip the `group_id/` prefix before calling `POST /api/jobs/{project_id}/task/{challenge_id}` or use the group job endpoint instead: `POST /api/jobs/{project_id}/group/{group_id}`.
- Challenge IDs:
  - Omitted IDs are hashed from `input`; repeats append `_n` when `repeat > 0` (important when re‑running individual challenges).
- Logs:
  - All `print` and `logging` output during task execution/evaluation is captured and shown in details (`multinear/utils/capture.py:1`).
- Alternate configs:
  - Use `--config <name>` or set `MULTINEAR_CONFIG` to point the web/CLI to `.multinear/<name>.yaml`.
- “Regression” label in recent runs:
  - In the current UI summary, the yellow “regression” slice counts tasks that are neither passed nor failed for that run (not historical regression detection). Adjust copy in README to avoid confusion with cross-run regression analysis.

## Minor README Touch-ups

- Mention optional `start_run()` hook in `.multinear/task_runner.py` for warm-up (e.g., model/client init, caches). See `multinear/engine/run.py:52`.
- Encourage including a `model` key in `details` from `run_task` so run summaries aggregate model info (see `get_model_summary()` in `multinear/engine/storage.py:147`).
- Note that `export` outputs a single JSON file with job metadata plus a `tasks` object keyed by `challenge_id` containing each task’s full record.

## Optional: Examples Section in README

- Provide a few end‑to‑end snippets tying it all together:
  1) A grouped config using multi‑metric evaluation with a custom evaluator.
  2) A structural JSON list validation example using JSONPath.
  3) A simple single‑metric checklist task with per‑item `min_score`.

## (Nice-to-have) CLI/UI alignment note

- If you list the expected shape of `eval_details` in README, clarify that it varies by evaluator:
  - Checklist/WeightedScore expose `metadata.evaluations` entries.
  - Multi‑metric exposes `details.metrics` (an array of per‑metric results). Consider adding a small note or table so users know where to look for rationales vs aggregated scores.
