# Multinear: Evaluation Platform for Reliable, Predictable AI Apps

**Multinear** enables teams to ship reliable Genenerative AI applications that actually work. Our evaluation platform gives engineers and product managers the benchmarks, regression detection, and actionable insights they need to iterate fast while maintaining quality — turning AI's inherent unpredictability into controlled, measurable progress.

![Project Overview](static/project.png)

**The Challenge**: Generative AI outcomes are inherently probabilistic. Even minor changes — in prompts, LLM models, data, or logic — can introduce regressions and break your app unpredictably. Traditional testing falls short because it assumes deterministic outcomes, leaving teams frustrated and uncertain.

Multinear solves this by providing structured experimentation, clear benchmarking, and instant visibility into regressions. It shifts evaluation from vague metrics to concrete, business-centric tests, empowering your team to continuously deliver measurable improvements.

## Why Multinear?

- **Predictable outcomes**  
  Replace ambiguous metrics with clear, pass/fail criteria tied directly to your product’s real-world impact.
- **Immediate regression detection**  
  Instantly spot regressions caused by changes to prompts, models, data, or business logic — no more guesswork.
- **Rapid experimentation**  
  Quickly test and measure each change’s exact effect on reliability, accelerating your development cycle.
- **Clear visibility into failures**  
  Know exactly why tests fail — prompt, model behavior, or data — allowing targeted, efficient fixes.
- **Continuous improvement**  
  Maintain and evolve your baseline, confidently shipping measurable incremental improvements.

| Before Multinear | After Multinear |
| --- | --- |
| ❌ Constant uncertainty around regressions | ✅ Immediate visibility into what breaks and why |
| ❌ Manual, ad-hoc testing | ✅ Continuous, reliable regression testing |
| ❌ Difficult-to-debug failures | ✅ Clear benchmarks for every iteration |

## How It Works

Multinear makes building reliable AI applications simple and systematic:

1. **Define clear evaluations**  
  Specify precise, binary (pass/fail) tests aligned to real-world business goals.
2. **Run structured experiments**  
  Systematically test changes in prompts, models, data, or logic with instant regression detection.
3. **Iterate confidently**  
  Benchmark every iteration, immediately see improvements or regressions, and rapidly iterate to reliable solutions.

With Multinear, you'll spend less time guessing and debugging — and more time confidently shipping AI-driven solutions.

## Quick Start Guide

Follow these simple steps to get Multinear running quickly and easily:

### 1. Install Multinear

Begin by installing the Multinear package from PyPI:

```bash
pip install multinear
```

### 2. Initialize Your Project

Create your Multinear project and configuration structure:

```bash
multinear init
```

This command sets up a `.multinear` folder in your project directory, including essential configuration files and an SQLite database for experiment results.

### 3. Define a Task Runner

Create a task runner file `.multinear/task_runner.py`. This file acts as the entry point for your AI application logic. It processes tasks defined in your evaluations and returns outputs for Multinear to assess.

* **Why do I need it?**
  Your task runner integrates Multinear directly with your AI application, ensuring experiments run consistently and reliably.

### 4. Configure Evaluations

Define your evaluation criteria in `.multinear/config.yaml`. Here you'll specify your tasks, evaluation methods, and success criteria, ensuring your tests align directly with your desired business outcomes.

### 5. Run Your Experiments

Start the Multinear web platform to run experiments and monitor progress visually:

```bash
multinear web
```

Visit [http://127.0.0.1:8000](http://127.0.0.1:8000) in your browser.

![Multinear Experiment Dashboard](static/experiment.png)

Prefer command line? You can do all the same tasks in CLI.

```bash
multinear run
```

### 6. Analyze Results

Multinear provides detailed insights and instant visibility into your test outcomes, making it easy to understand and debug failures. Quickly detect regressions, visualize trends, and iterate confidently.

## Further Reading

- [Full Quickstart Guide](/docs/quickstart.md) – Get set up quickly.
- [Defining Evaluations](/docs/evaluations.md) – Learn how to design great tests.
- [Running Experiments](/docs/experiments.md) – Run, benchmark, and iterate.
- [Analyzing Results](/docs/results.md) – Understand outcomes clearly.
- [CLI Reference](/docs/cli.md) – Automate your workflow.
- [Architecture & Contributing](/docs/architecture.md) – Go deeper or contribute.

---

## License

Multinear is released under the [MIT License](LICENSE). Feel free to use, modify, and distribute this software per the terms of the license.
