# Multinear: Reliable GenAI Applications

Developing reliable applications powered by Generative AI presents unique challenges. The unpredictable nature of LLMs often leads to inconsistent outputs, regressions, and unforeseen behaviors, especially when iterating on prompts, models, and datasets. **Multinear** is a platform designed to help you navigate these challenges by providing a systematic way to run experiments, measure results, and gain insights, ensuring your GenAI applications are robust and trustworthy.

![Project Overview](static/project.png)

## Why Multinear?

- **End-to-End Evaluation**: Assess the full spectrum of your GenAI application — from inputs to outputs — capturing the interactions between models, prompts, datasets, and business logic.
- **Experimentation Made Easy**: Run experiments with various configurations effortlessly. Test different models, tweak prompts, adjust datasets, and modify your code to find the optimal setup.
- **Regression Detection**: Identify when new changes negatively impact previously successful cases. Multinear tracks regressions so you can maintain and improve application reliability over time.
- **Comprehensive Evaluation Methods**: Use a range of evaluation strategies, including strict output comparisons, LLM-as-a-judge assessments, and human evaluations, to ensure your application meets quality standards.
- **Insightful Analytics**: Compare results across different runs to understand the impact of changes. Visualize performance trends and make data-driven decisions to enhance your application.
- **Guardrail Testing**: Strengthen your application against malicious inputs, security threats, and safety concerns by evaluating it under challenging scenarios.

## Project Initialization

Initialize a new Multinear project in your project folder:

```bash
pip install multinear
multinear init
```

You'll be prompted to enter your project details:

- **Project Name**: A descriptive name for your project.
- **Project ID**: A URL-friendly identifier (default provided).
- **Project Description**: A brief summary of your project's purpose.

This command creates a `.multinear` folder containing your project configuration and an SQLite database for experiment results. It's recommended to commit this folder alongside your code to keep track of your evaluations.

## Running the Platform

Start the Multinear web server to access the interactive frontend:

```bash
multinear web
```
Access the platform at `http://127.0.0.1:8000` in your browser.

For development mode with auto-reload on file changes, use:

```bash
multinear web_dev
```

### Defining Your Task Runner

Create a `task_runner.py` in the `.multinear` folder of your project. This file defines the `run_task(input)` function, which contains the logic for processing each task using your GenAI application.

Example `task_runner.py`:

```python
def run_task(input):
    # Your GenAI-powered application logic here
    output = my_application.process(input)  # If your app is standalone, expose an API and call it here to get the output
    details = {'model': 'gpt-4o'}
    return {'output': output, 'details': details}
```

### Configuring Tasks and Evaluations

Define your tasks and evaluation criteria in `.multinear/config.yaml`.

Example `config.yaml`:

```yaml
project:
  id: my-genai-project
  name: My GenAI Project
  description: Experimenting with GenAI models

meta:
  context: |
    This is a global context that will be injected into each task evaluation.
    It's important to include any useful information that may be needed to evaluate each result.

tasks:
  - id: task1
    input: Input data for task 1
    checklist:
      - The output should be in English.
      - The response should be polite.
      - The response should be less than 500 words.
    # Overall score, some checklist items can completely fail, and still pass if the majority pass
    # (in this case, 2/3 items will pass)
    min_score: 0.6
  - id: task2
    input: "Input data for task 2"
    checklist:
      - The output should include at least two examples.
      - The response should be less than 500 words.
      - text: Tests can have individual minimum scores, as sometimes it's hard to compose an assertion that is both comprehensive and easy to evaluate.
        min_score: 0.5  # Individual checklist item score
```

### Running Experiments

You can run experiments either through the command line interface (CLI) or the web frontend.

#### Using the Frontend

1. Start the web server if not already running:
```bash
multinear web
```

2. Open `http://127.0.0.1:8000` in your browser

3. Click "Run Experiment" to start an experiment

The frontend provides:
- Real-time progress tracking
- Interactive results visualization
- Detailed task-level information
- Ability to compare multiple runs

![Experiment Overview](static/experiment.png)

#### Using the CLI

Run an experiment using the `run` command:

```bash
multinear run
```

This will:
- Start a new experiment run
- Show real-time progress with a progress bar
- Display current status and results
- Save detailed output to `.multinear/last_output.txt`

View recent experiment results:
```bash
multinear recent
```

Get detailed information about a specific run:
```bash
multinear details <run-id>
```

## Analyzing Results

Once the experiment run is complete, you can analyze the results via the frontend dashboard. The platform provides:

- **Run Summaries**: Overview of each experiment run, including total tasks, passed/failed counts, and overall score.
- **Detailed Reports**: Drill down into individual tasks to see input, output, logs, and evaluation details.
- **Trend Analysis**: Compare results across runs to identify improvements or regressions.
- **Filter and Search**: Find specific tasks or runs based on criteria such as challenge ID, date, or status.

## Architecture

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

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch for your feature or bugfix.
3. Make your changes with clear commit messages.
4. Submit a pull request to the `main` branch.

Please ensure that your code adheres to the project's coding standards and passes all tests.

## License

Multinear is released under the [MIT License](LICENSE). You are free to use, modify, and distribute this software as per the terms of the license.
