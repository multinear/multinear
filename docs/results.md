# Analyzing Results with Multinear

Analyzing results effectively is crucial for improving your Generative AI application's reliability. Multinear provides comprehensive insights, enabling you to easily interpret outcomes, quickly diagnose failures, and confidently manage regressions.

## Overview

Multinear equips you with powerful tools for analysis:

- **Run Summaries**  
    Immediate overviews of experiment outcomes.
- **Detailed Task Reports**  
    Deep visibility into each evaluation's inputs, outputs, and logs.
- **Regression Detection**  
    Instantly highlights regressions compared to previous benchmarks.
- **Trend Analysis**  
    Visualizes performance across multiple experiment runs.

## 1. Viewing Run Summaries

Upon completing an experiment, Multinear shows a concise summary showing:

- Total tasks executed
- Number of tasks passed/failed
- Overall experiment score
- Tasks flagged as regressions

This summary allows rapid assessment of your application's health at a glance.

## 2. Detailed Task Reports

For deeper insights, access detailed task reports:

- **Task Input and Output**  
    Clearly compare your application's output against expected results.
- **Evaluation Logs**  
    Review captured logs and rationales provided by evaluators, clearly showing why a task passed or failed.
- **Evaluator Feedback**  
    LLM-generated or custom evaluation feedback explicitly highlighting successes or pinpointing failure causes.

### How to Access Task Reports

- **Web UI**: Click on any task within the run summary dashboard.
- **CLI**: Run the following command:

```bash
multinear details <run-id>  # Example: multinear details 3f8a92cd
```

### Using Detailed Reports for Debugging

When reviewing failed tasks:

1. **Check Evaluator Feedback**  
    Start here for immediate insights into why the task failed.
2. **Inspect Logs**  
    Review captured logs to understand internal behavior (prompt structure, model responses, data retrieval, etc.).
3. **Compare Outputs**  
    See discrepancies between expected and actual outputs to quickly pinpoint root causes.

## 3. Detecting and Understanding Regressions

Multinear automatically compares current experiment runs with your established baseline to immediately identify regressions:

- **Regression Identification**: Marked within summaries and task reports.
- **Historical Comparisons**: Compare current failures against previous successful results.

### Addressing Regressions Effectively

When a regression is detected:

1. **Review Historical Comparisons**  
    Determine precisely what changed between runs (prompt changes, data shifts, or logic updates).
2. **Investigate Root Causes**  
    Use detailed task logs and evaluator feedback to quickly identify the exact issue.
3. **Make Targeted Improvements**  
    Apply fixes focused explicitly on identified root causes.

Re-run the experiment after changes to confirm regression resolution and re-establish your baseline.

## 4. Trend Analysis and Continuous Improvement

Regularly using Multinear allows you to track improvements and identify patterns over time:

- **Visualizing Trends**: Use Multinear's visualizations to monitor pass rates and regression counts across runs.
- **Performance Metrics**: Identify persistent issues or improvements in reliability.

By analyzing these trends, you can proactively adjust your strategy for greater reliability and better business outcomes.

## 5. Best Practices for Effective Result Analysis

Follow these best practices to maximize the value from analyzing results:

- **Analyze Frequently**  
    Regularly review results after each run to catch issues early.
- **Prioritize Regressions**  
    Address regressions immediately to maintain reliability.
- **Collaborate with Stakeholders**  
    Share insights with your team to align on improvements.
- **Document Changes**  
    Clearly log modifications (prompts, logic, data) and their impacts.
- **Update Evaluation Criteria**  
    Regularly refine your evaluation criteria based on feedback and analysis.

## Further Reading

Next: [CLI Reference](/docs/cli.md) – Automate your workflow.

Contents

- [Introduction](/README.md)
- [Evaluations Reference](/docs/evaluations.md) – Deep dive into defining great tests.
- [Running Experiments](/docs/experiments.md) – Advanced experiment workflows.
- [Architecture & Contributing](/docs/architecture.md) – Go deeper or contribute.
