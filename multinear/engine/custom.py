class CustomEvaluator():
    def __init__(self, spec, task_runner_module):
        self.spec = spec
        self.task_runner_module = task_runner_module

    def __call__(self, input, output):
        return self.task_runner_module.evaluate_custom(input, output, self.spec)
