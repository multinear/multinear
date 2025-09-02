# Running Experiments with Multinear

Multinear empowers you to systematically evaluate your Generative AI application, ensuring reliable outcomes and rapid iteration cycles. This guide walks you through running structured experiments, effectively detecting regressions, and adopting best practices for continuous improvement.

## Overview

Experiments in Multinear follow a simple, repeatable workflow:

1. **Define your evaluations** clearly and precisely.
2. **Run experiments** using the Multinear web UI or CLI.
3. **Analyze results** to detect regressions and understand outcomes.
4. **Iterate confidently** by making informed, measurable improvements.

## 1. Setting Up Your Experiment

Before running an experiment, ensure you've configured your project properly.

- **Evaluation Criteria**: Defined clearly in `.multinear/config.yaml`.
- **Task Runner**: Defined in `.multinear/task_runner.py`, integrated with your AI application logic.

Ensure you have your OpenAI credentials configured if you're using LLM-based evaluators:

```bash
export OPENAI_API_KEY=sk-...
```

## 2. Running Experiments via Web UI

To run experiments interactively, use the Multinear web interface:

```bash
multinear web
```

Navigate to [http://127.0.0.1:8000](http://127.0.0.1:8000).

### Start an Experiment

- Click the **"Run Experiment"** button.
- Monitor the real-time progress on the dashboard.

### Dashboard Overview

The dashboard provides:

- **Real-time progress** indicators.
- **Task-level outcomes**: Pass/fail statuses with clear color coding.
- **Immediate regression detection**: Compares current results with your baseline.
- **Detailed results inspection**: Click tasks for deeper introspection.

![Experiment Dashboard](/static/experiment.png)

### Run Specific Groups

For larger evaluation sets, organize tasks into groups in your config, then run selectively.

## 3. Detecting Problems and Managing Regressions

### Debugging Failures

When tasks fail:

1. **Inspect detailed logs**: Click on the failed tasks to see why they failed.
2. **Identify the root cause** or at least make an educated guess what you need to change to fix that - prompt, business logic, something else.
3. **Apply fixes** and rerun your experiments immediately to confirm resolution.
4. **Run all tests** to validate that your fix didn't affect other tests (regression).

### Understanding Regressions

A regression occurs when previously passing tasks fail after you introduce changes (to prompts, model, data, or logic).

### Establishing and Updating Your Baseline

Treat successful runs as benchmarks:

- After fixing regressions and passing all tests, this becomes your new baseline.
- Continuous benchmarking ensures you're always improving from a known good state.

## 4. Best Practices for Running Experiments

To maximize Multinear’s effectiveness:

### Clearly Define Binary Evaluations

- Prefer clearly defined pass/fail criteria tied directly to business outcomes.
- Avoid vague or subjective criteria.

**✅ Good Example:**

- "Response explicitly lists 3 troubleshooting steps."

**❌ Bad Example:**

- "Answer feels informative."

### Frequent, Small Iterations

- Test small changes frequently rather than large changes occasionally.
- This helps pinpoint regressions precisely, speeding up debugging and resolution.

### Use Groups and Context Effectively

- Group tasks logically (e.g., customer support, sales).
- Leverage shared context and group-level configurations to streamline evaluation definitions.

### Automate Regression Detection

Integrate Multinear with your CI/CD pipeline:

- Use CLI commands (`multinear run`) as part of automated testing.
- Automatically alert your team when regressions are detected.

### Maintain Experiment Logs

- Commit your `.multinear` folder to version control.
- Track historical evaluation criteria, results, and regression points clearly.

## 5. Continuous Improvement

Multinear is a long-term solution for maintaining AI reliability:

- Continuously refine and update your evaluation criteria as your application evolves.
- Regularly rerun experiments to catch regressions early and ensure continuous improvement.

## Further Reading

Next: [Analyzing Results](/docs/results.md) – Understand outcomes clearly.

Contents

- [Introduction](/README.md)
- [Evaluations Reference](/docs/evaluations.md) – Deep dive into defining great tests.
- [Running Experiments](/docs/experiments.md) – Advanced experiment workflows.
- [CLI Reference](/docs/cli.md) – Automate your workflow.
- [Architecture & Contributing](/docs/architecture.md) – Go deeper or contribute.
