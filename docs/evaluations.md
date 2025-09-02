# Multinear: Evaluations Reference

## Structuring Evaluations for Real-World Impact (NEW)

Multinear helps you measure AI solutions against real-world business outcomes, not abstract metrics. To achieve maximum impact, evaluations should be:

- **Binary and Actionable**  
  Clearly define tests that yield pass/fail outcomes — no ambiguity.
- **Business-Focused**  
  Directly align evaluation criteria with actual business scenarios and user expectations.
- **Transparent**  
  When tests fail, they should provide explicit insights into why, guiding clear next steps.

### Good vs. Bad Criteria Examples

**✅ Good:**  
- "Answer explicitly outlines refund steps." (Binary, clear)
- "Answer includes user’s subscription expiry date." (Actionable)
- "Answer mentions at least two alternative solutions." (Measurable, business-centric)

**❌ Bad:**  
- "Response is high-quality." (Ambiguous)
- "Tone is friendly." (Subjective without criteria)
- "Overall accuracy above 0.75." (Unclear relevance)

## Configuration

Multinear reads `.multinear/config.yaml`. You can define a flat `tasks:` list or organize tasks into `groups:`. Below is the supported structure with examples.

```yaml
project:            # Required project metadata
  id: my-project
  name: My Project
  description: Demo

meta:               # Optional: defaults and execution controls
  repeat: 1         # Default repeats per task (int)
  rephrase: false   # Rephrase inputs for repeats > 1 via OpenAI
  max_workers: 1    # Parallel workers for concurrent execution
  context: |        # Shared context injected into evaluators
    Shared evaluation context here
  fail_simulate: 0  # Optional float (0..1) to simulate failures for testing
  # Optional evaluator defaults for single‑metric tasks
  # checklist: [...]
  # custom: { ... }

# Choose one style: grouped or flat
groups:
  - id: retrieval
    name: Retrieval checks
    description: Validate RAG answers and structure
    tasks: [ ... ]  # See Task object below

# Flat mode (alternative to groups)
tasks:
  - { ... }
```

Note: `rephrase` only affects repeats after the first; the first execution always uses the original input.

## Task object examples:

### Single‑metric task (choose one evaluator block):

```yaml
tasks:
  - id: task-1                              # Optional; auto‑derived sha256(input) if omitted
    input: "Summarize the process in simple terms."  # String or object. If object has `question`, only that key is rephrased
    min_score: 0.7                           # Optional: pass threshold (default 1.0)
    repeat: 1                                # Optional: override meta.repeat
    rephrase: false                          # Optional: override meta.rephrase
    context: "Audience: non‑experts"         # Optional: appended after meta.context (single‑metric only)

    # Checklist evaluator (active example)
    checklist:
      - text: Response is in English
      - text: Tone is polite
      - text: Uses 2–3 concise bullet points
        min_score: 0.5                      # Optional per‑item min; >= min counts as full pass

    # weighted_score:                       # Alternative (commented)
    #   - { id: accuracy,  eval: "Technically accurate",  weight: 0.5 }
    #   - { id: clarity,   eval: "Clear to layperson",    weight: 0.3 }
    #   - { id: brevity,   eval: "<= 200 words",          weight: 0.2 }
    # context: "Evaluation context"          # Optional

    # list:                                  # Alternative (commented)
    #   path: "$.payload.required_keys"      # Optional: JSONPath into output
    #   includes: ["id", "email"]
    #   excludes: ["password"]
    #   max_length: 10

    # numeric:                               # Alternative (commented)
    #   expected: 0.85
    #   method: tolerance                     # One of: direct_diff | mse | rmse | tolerance | range
    #   absolute_tolerance: 0.05              # Or use relative_tolerance
    #   # Optional helpers:
    #   # path: "$.score"
    #   # extraction_hint: "the AUC"
    #   # preprocessing: strip_spaces

    # custom:                                # Alternative (commented)
    #   checks:
    #     - name: Has greeting
    #       criterion: "Contains 'Hello'"
    #       type: contains
    #       value: "Hello"
    #     - name: Max length 200
    #       criterion: "<= 200 characters"
    #       type: max_length
    #       value: 200
    # # Note: custom is additive; pair it with another evaluator for best results.
```

### Multi‑metric task (average score; all metrics must pass):

```yaml
tasks:
  - id: task-2
    input: "Answer and cite at least two sources."
    # Optional: shared context across metrics (use meta.context for multi‑metric)
    # meta:
    #   context: "Enterprise tone"
    metrics:
      - type: checklist
        checklist:
          - text: Cites at least 2 sources
          - text: Avoids marketing buzzwords
        min_score: 0.6                      # Optional per‑metric threshold
        context: "Formal tone"               # Optional per‑metric context
      - type: weighted_score
        weighted_score:
          - { id: structure, eval: "Structured sections", weight: 0.4 }
          - { id: facts,     eval: "Factual accuracy",  weight: 0.6 }
        min_score: 0.7
```

Task IDs:
- If `id` is omitted, Multinear derives it as `sha256(input)`.
- When `repeat > 1`, subsequent repeats append `_<n>` (e.g., `_1`, `_2`).

### Groups example:

```yaml
groups:
  - id: rag
    name: RAG
    description: Retrieval‑augmented generation checks
    tasks:
      - id: rag-basic
        input: { question: "What is vector search?" }
        checklist:
          - text: Mentions dense embeddings
          - text: Explains approximate nearest neighbors (ANN)
```

## Evaluator blocks

### Checklist (LLM‑as‑judge with per‑item scoring):

Uses an LLM to score each checklist item (0–1) with a rationale, then averages across items. You can set per‑item `min_score` to grant full credit when met and pass optional `context` (appended after `meta.context`).

```yaml
tasks:
  - id: checklist-demo
    input: "Summarize the process."
    context: "Audience: non‑experts"  # Optional: appended after meta.context
    checklist:
      - text: Response is in English
      - text: Tone is polite
      - text: Under 200 words; min_score: 0.5  # Optional per‑item min; >= min counts as full pass
    min_score: 0.7  # Optional pass threshold (default 1.0)
```

### Weighted Score (multi‑criterion with weights):

Scores multiple criteria and combines them using your weights to produce a final 0–1 score. Returns per‑criterion rationales; weights don’t need to sum to 1 (the evaluator normalizes by total weight).

```yaml
tasks:
  - id: weighted-demo
    input: "Explain vector search to a PM."
    weighted_score:
      - { id: accuracy,  eval: "Technically accurate",  weight: 0.5 }
      - { id: clarity,   eval: "Clear to layperson",    weight: 0.3 }
      - { id: brevity,   eval: "Brevity (<= 200 words)", weight: 0.2 }
    # Optional fields:
    # context: "Evaluation context"
```

### List (structural checks over arrays):

Validates list structure/content in the output. Target the list via optional JSONPath `path`, then require items (`includes`), forbid items (`excludes`), and enforce `max_length`; non‑list values fail.

```yaml
tasks:
  - id: list-demo
    input: { payload: { required_keys: ["id", "email", "role"] } }
    list:
      path: "$.payload.required_keys"   # Optional JSONPath into the output
      includes: ["id", "email"]
      excludes: ["password"]
      max_length: 10
```

### Custom (user‑defined Python in `.multinear/task_runner.py`):

A Python hook to implement domain‑specific checks. Return a dict with `score` and `metadata.evaluations`; use alongside another evaluator when you want both LLM judgment and deterministic rules.

```yaml
tasks:
  - id: custom-demo
    input: "Hello, this is a short response about vectors."
    # Note: custom is additive; pair it with another evaluator when needed
    checklist:
      - text: Mentions 'vector' (case-insensitive); min_score: 0.5
    custom:
      checks:
        - name: Has greeting
          criterion: "Contains 'Hello'"
          type: contains
          value: "Hello"
        - name: Max length 200
          criterion: "<= 200 characters"
          type: max_length
          value: 200
```

Minimal `.multinear/task_runner.py` shape:

```python
# .multinear/task_runner.py
from typing import Any, Dict, List


def _score_bool(ok: bool) -> float:
    return 1.0 if ok else 0.0


def evaluate_custom(input: Any, output: Any, spec: Dict) -> Dict:
    """
    Example custom evaluator matching the YAML `custom:` block above.
    Supports check types: contains, icontains, max_length, min_length.
    """
    checks: List[Dict] = spec.get("checks", [])

    # Normalize output to string for simple checks
    out_text = output if isinstance(output, str) else str(output)

    evaluations: List[Dict] = []
    total = 0.0

    for chk in checks:
        ctype = chk.get("type")
        crit = chk.get("criterion") or chk.get("name") or "Unnamed check"
        val = chk.get("value")

        ok = False
        rationale = ""

        try:
            if ctype == "contains":
                ok = (val or "") in out_text
                rationale = f"{'Found' if ok else 'Missing'} substring: {val!r}"
            elif ctype == "icontains":
                ok = (val or "").lower() in out_text.lower()
                rationale = f"{'Found' if ok else 'Missing'} substring (case-insensitive): {val!r}"
            elif ctype == "max_length":
                limit = int(val)
                ok = len(out_text) <= limit
                rationale = f"Length {len(out_text)} / {limit}"
            elif ctype == "min_length":
                limit = int(val)
                ok = len(out_text) >= limit
                rationale = f"Length {len(out_text)} >= {limit}"
            else:
                rationale = f"Unknown check type: {ctype}"
        except Exception as e:
            ok = False
            rationale = f"Check error: {e}"

        s = _score_bool(ok)
        total += s
        evaluations.append({
            "criterion": crit,
            "score": s,
            "rationale": rationale,
        })

    # Average score across checks; empty list -> 0.0
    overall = (total / len(evaluations)) if evaluations else 0.0

    result = {
        "score": overall,
        "metadata": {
            "evaluations": evaluations,
            "overall_score": overall,
        },
    }

    # Optional pass honoring custom min_score if provided in spec
    if isinstance(spec.get("min_score"), (int, float)):
        result["passed"] = overall >= float(spec["min_score"])

    return result
```

Notes:
- Merging: Multinear merges custom results assuming a dict return type with `metadata.evaluations`. Returning a `Score` object will not merge rationales correctly.
- Combination: When combined with another evaluator, Multinear averages the custom `score` with the primary evaluator’s score and concatenates both `metadata.evaluations` lists.
- Additive: Use custom alongside another evaluator (e.g., checklist + custom) rather than as a standalone replacement.

### Numeric (extract and compare numbers):

Extracts a numeric value from output (regex, JSONPath, or with an LLM hint) and compares it to an expected value. Supports `direct_diff`, `mse`, `rmse`, `tolerance`, and `range` methods for flexible numeric validation.

```yaml
tasks:
  - id: numeric-demo
    input: "The AUC achieved was 0.87 on the validation set."
    numeric:
      expected: 0.85
      method: tolerance               # direct_diff | mse | rmse | tolerance | range
      absolute_tolerance: 0.05        # Or use relative_tolerance
      # Optional helpers:
      # path: "$.score"
      # extraction_hint: "the AUC"
      # preprocessing: strip_spaces
```

## Repeats and Rephrasing

- Repeats: Control how many times a task runs with `meta.repeat` (default 1) or per‑task `repeat`. Each repeat produces its own record; when task IDs are omitted Multinear derives ID as `sha256(input)` and appends `_<n>` for repeats after the first (e.g., `_1`, `_2`). Repeats respect configured concurrency via `meta.max_workers`.
- Rephrasing: Set `meta.rephrase: true` or per‑task `rephrase: true` to automatically generate paraphrases for repeats after the first. Multinear calls an LLM to rephrase inputs (requires `OPENAI_API_KEY`) and tracks prior variations to avoid duplicates. If the task input is an object with a `question` key, only `question` is rephrased; otherwise the entire input string is rephrased.

Examples:

A) Global default repeat + rephrase

```yaml
meta:
  repeat: 3           # Run all tasks 3 times unless overridden
  rephrase: true      # Paraphrase repeats > 1 via LLM

tasks:
  - id: paraphrase-global
    input: { question: "How does vector search work?" }
    checklist:
      - text: Mentions dense embeddings
      - text: Explains ANN indexing
```

B) Per-task override

```yaml
meta:
  repeat: 1           # Default: run once
  rephrase: false     # Default: no rephrasing

tasks:
  - id: paraphrase-override
    input: { question: "How does vector search work?" }
    repeat: 2         # Override to run this task twice
    rephrase: true    # Rephrase this task’s repeats only
    checklist:
      - text: Mentions dense embeddings
      - text: Explains ANN indexing
```

## Pass/fail semantics
- Single‑metric tasks: Pass when `score >= min_score` (default `min_score: 1.0`). If using `checklist`, per‑item `min_score` can bump that item to full credit; the task’s `min_score` still applies to the averaged score.
- Multi‑metric tasks: Each metric has its own `min_score` and must pass independently (AND logic). The task’s overall score is the average of metric scores. Note: a task‑level `min_score` is ignored when `metrics:` is used — set `min_score` per metric.
- Custom + primary evaluator: When `custom:` is present in a metric, Multinear averages the custom score with the primary metric’s score and concatenates their rationales; pass/fail is determined against that metric’s `min_score`.
- Weighted Score edge case: An empty `weighted_score: []` is treated as a no‑op and returns `score=1.0, passed=true`.

## Setup and Environment

- Models: Evaluators default to a sensible OpenAI chat model. If your stack supports customizing models (via autoevals or your environment), set the appropriate env var per your setup.
- Database: Results are stored in a local SQLite DB at `.multinear/multinear.db` (created automatically). The engine enables WAL mode for better concurrency.
- Git revision: If the project directory is a Git repo, Multinear records the current revision for each run and shows it in recent runs and run details.
- Alternate config: Use `MULTINEAR_CONFIG` or CLI `--config <name>` to point to `.multinear/<name>.yaml`.


## Tips and Gotchas

### Context propagation
- Single‑metric tasks: The engine injects `meta.context` into the task as `context` before evaluation. If you also set `task.context`, the injected value overwrites it. Recommendation: for single‑metric tasks, put shared evaluator context in `meta.context` only.
- Multi‑metric tasks: Place `context` inside each metric item for per‑metric guidance. To share a value across all metrics in a task, add `meta.context` under the task:
  
  ```yaml
  tasks:
    - id: t1
      meta:
        context: "Shared across metrics"
      metrics:
        - type: checklist
          context: "Tone: formal"
          checklist: [ ... ]
        - type: weighted_score
          weighted_score: [ ... ]
  ```
  The engine concatenates shared context first, then per‑metric context.
- Evaluator support: `context` is used by LLM‑based evaluators (checklist, weighted_score). Structural evaluators (`list`, `numeric`) ignore `context`.
- Repeats: Rephrasing changes only the input; `context` remains unchanged across repeats.

### Regression label in recent runs
- The “regression” slice in the recent runs chart reflects tasks that are neither passed nor failed in that run (e.g., errored or pending), not historical regressions versus prior runs. Use run comparisons in the UI to assess cross‑run regressions.

## Further Reading

- [Introduction](/README.md)
- [Full Quickstart Guide](/docs/quickstart.md) – Get set up quickly.
- [Running Experiments](/docs/experiments.md) – Run, benchmark, and iterate.
- [Analyzing Results](/docs/results.md) – Understand outcomes clearly.
- [CLI Reference](/docs/cli.md) – Automate your workflow.
- [Architecture & Contributing](/docs/architecture.md) – Go deeper or contribute.
